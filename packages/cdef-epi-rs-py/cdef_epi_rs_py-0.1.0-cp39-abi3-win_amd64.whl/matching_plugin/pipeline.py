from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterable, Optional

import polars as pl

from ._internal import did_aggregate_py as _did_aggregate_rust  # type: ignore
from ._internal import did_att_gt_py as _did_att_gt_rust  # type: ignore
from ._internal import (
    format_match_output as _format_match_output_rust,  # type: ignore
)
from ._internal import (
    match_scd_cases_with_diagnostics as _match_scd_cases_with_diag_rust,  # type: ignore
)


def run_full_parent_income_pipeline(
    match_input_df: pl.DataFrame,
    relations_df: pl.DataFrame,
    *,
    matching_config: dict | str,
    ind_registry_pattern: str,
    income_vars: list[str],
    bef_registry_pattern: str | None = None,
    akm_registry_pattern: str | None = None,
    uddf_file_path: str | None = None,
    income_temporal_range: tuple[int, int] = (-10, 10),
    vital_df: pl.DataFrame | None = None,
    did_config: dict | str | None = None,
) -> dict[str, Any]:
    """
    Run the full pipeline:
    1) Matching with diagnostics
    2) Build parent-year DID panel (returns panel diagnostics)
    3) Estimate ATT(g,t) via did-core (requires did_config)

    Returns a dict with keys: matches, match_diagnostics, panel, panel_diagnostics, att_gt (optional).
    """
    # 1) Matching with diagnostics
    match_start = time.perf_counter()
    cfg_json = (
        matching_config
        if isinstance(matching_config, str)
        else json.dumps(matching_config)
    )
    match_out = _match_scd_cases_with_diag_rust(match_input_df, vital_df, cfg_json)
    match_elapsed = time.perf_counter() - match_start

    matches_df = match_out["matches"]
    match_diagnostics = match_out["diagnostics"]
    match_diagnostics["timings"]["python_wrapper_ms"] = int(match_elapsed * 1000)

    # Convert to long format for panel building
    long_df = _format_match_output_rust(matches_df)

    # 2) Build panel (single-shot; panel builder already robust to schema drift)
    panel_start = time.perf_counter()
    # Local import avoids circular import at module load
    from . import build_parent_did_panel

    panel_df = build_parent_did_panel(
        match_df=long_df,
        relations_df=relations_df,
        ind_registry_pattern=ind_registry_pattern,
        income_vars=income_vars,
        bef_registry_pattern=bef_registry_pattern,
        akm_registry_pattern=akm_registry_pattern,
        uddf_file_path=uddf_file_path,
        income_temporal_range=income_temporal_range,
    )
    panel_elapsed = time.perf_counter() - panel_start

    # Panel diagnostics: simple, fast, and informative
    role_counts = (
        long_df.lazy()
        .group_by("ROLE")
        .agg(pl.len().alias("n"))
        .collect()
        .to_dict(as_series=False)
    )

    # missingness for income vars
    income_missing = {}
    for v in income_vars:
        if v in panel_df.columns:
            n = panel_df.height
            miss = panel_df.select(pl.col(v).is_null().sum().alias("m")).item()
            income_missing[v] = {
                "missing": int(miss),
                "missing_pct": (miss / n if n else 0.0),
            }

    panel_diagnostics = {
        "counts": {
            "match_long_rows": long_df.height,
            "panel_rows": panel_df.height,
            "unique_parents": panel_df.select(pl.col("parent_pnr")).n_unique()
            if "parent_pnr" in panel_df.columns
            else 0,
        },
        "roles": role_counts,
        "income_missing": income_missing,
        "timings_ms": {"panel_build_py": int(panel_elapsed * 1000)},
        "columns_present": panel_df.columns,
    }

    result: dict[str, Any] = {
        "matches": matches_df,
        "match_diagnostics": match_diagnostics,
        "panel": panel_df,
        "panel_diagnostics": panel_diagnostics,
    }

    # 3) DID (optional)
    if did_config is not None:
        cfg_json = did_config if isinstance(did_config, str) else json.dumps(did_config)
        att_gt = _did_att_gt_rust(panel_df, cfg_json)
        result["att_gt"] = att_gt

    return result


def build_did_config(
    outcome_var: str,
    *,
    treatment_var: str = "treated",
    time_var: str = "year",
    id_var: str = "parent_pnr",
    group_var: str = "first.treat",
    control_vars: list[str] | None = None,
    cluster_var: str | None = "parent_pnr",
    weights_var: str | None = None,
    bootstrap_iterations: int = 500,
    confidence_level: float = 0.95,
    base_period: str = "Varying",
    control_group: str = "NotYetTreated",
    method: str = "Dr",
    inference: str = "Drdid",
    panel_type: str = "UnbalancedPanel",
    allow_unbalanced_panel: bool = True,
    rng_seed: int | None = 123,
    strict_missing_cells: bool = False,
) -> dict:
    return {
        "outcome_var": outcome_var,
        "treatment_var": treatment_var,
        "time_var": time_var,
        "id_var": id_var,
        "group_var": group_var,
        "control_vars": control_vars or [],
        "cluster_var": cluster_var,
        "weights_var": weights_var,
        "bootstrap_iterations": bootstrap_iterations,
        "confidence_level": confidence_level,
        "base_period": base_period,
        "control_group": control_group,
        "method": method,
        "inference": inference,
        "loss": "Logistic",
        "panel_type": panel_type,
        "allow_unbalanced_panel": allow_unbalanced_panel,
        "rng_seed": rng_seed,
        "strict_missing_cells": strict_missing_cells,
    }


def run_gender_split_dynamic(
    panel: pl.DataFrame,
    did_config: dict,
    *,
    genders: Iterable[str] = ("M", "F"),
    confidence: float = 0.95,
    uniform_bands: bool = False,
) -> dict[str, pl.DataFrame]:
    """
    Estimate dynamic ATT(g,t) curves separately for each gender value (e.g., 'M', 'F').
    Returns a dict mapping gender -> aggregated dynamic DataFrame.
    """
    out: dict[str, pl.DataFrame] = {}
    cfg_json = did_config if isinstance(did_config, str) else json.dumps(did_config)
    for g in genders:
        sub = panel.filter(pl.col("gender") == g)
        if sub.height == 0:
            continue
        att = _did_att_gt_rust(sub, cfg_json)
        dyn = _did_aggregate_rust(att, cfg_json, "dynamic", confidence, uniform_bands)
        out[str(g)] = dyn
    return out


def run_category_split_dynamic(
    panel: pl.DataFrame,
    did_config: dict,
    *,
    category_col: str = "socio13_cat",
    categories: list[str] | None = None,
    confidence: float = 0.95,
    uniform_bands: bool = False,
) -> dict[str, pl.DataFrame]:
    """
    Estimate dynamic ATT(g,t) curves separately for each category in `category_col`.
    If `categories` is None, discovers unique non-null categories present in the panel.
    Returns a dict mapping category -> aggregated dynamic DataFrame.
    """
    out: dict[str, pl.DataFrame] = {}
    if category_col not in panel.columns:
        return out
    if categories is None:
        categories = (
            panel.select(pl.col(category_col))
            .drop_nulls()
            .unique(maintain_order=True)
            .to_series()
            .to_list()
        )
        categories = [str(c) for c in categories]

    cfg_json = did_config if isinstance(did_config, str) else json.dumps(did_config)
    for cat in categories:
        sub = panel.filter(pl.col(category_col) == cat)
        if sub.height == 0:
            continue
        att = _did_att_gt_rust(sub, cfg_json)
        dyn = _did_aggregate_rust(att, cfg_json, "dynamic", confidence, uniform_bands)
        out[cat] = dyn
    return out


def run_parent_income_study(
    match_input_df: pl.DataFrame,
    relations_df: pl.DataFrame,
    *,
    matching_config: dict | str,
    ind_registry_pattern: str,
    income_vars: list[str],
    outcome_var: str,
    bef_registry_pattern: str | None = None,
    akm_registry_pattern: str | None = None,
    uddf_file_path: str | None = None,
    income_temporal_range: tuple[int, int] = (-10, 10),
    vital_df: pl.DataFrame | None = None,
    did_controls: list[str] | None = None,
    gender_values: Iterable[str] = ("M", "F"),
    socio13_order: list[str] | None = None,
    confidence: float = 0.95,
    uniform_bands: bool = False,
    plot_output_dir: Optional[str] = None,
    plot_format: str = "png",
    plot_via_rust: bool = False,
    typst_output_dir: Optional[str] = "did_plots_typst",
) -> dict[str, Any]:
    """
    Run the full pipeline and produce outputs to answer:
    1) Overall income trajectory difference (treated vs control) → dynamic curve.
    2) Gender differences → dynamic curves by gender.
    3) Socioeconomic moderation → dynamic curves by socio13_cat.

    Returns a dict with keys:
      - matches, match_diagnostics, panel, panel_diagnostics
      - att_gt_overall, dynamic_overall
      - dynamic_by_gender (dict), dynamic_by_socio13 (dict)
    """
    did_cfg = build_did_config(
        outcome_var=outcome_var,
        control_vars=did_controls or [],
        control_group="NotYetTreated",
        method="Dr",
        inference="Drdid",
    )

    # Run the core pipeline with an overall DID config
    res = run_full_parent_income_pipeline(
        match_input_df=match_input_df,
        relations_df=relations_df,
        matching_config=matching_config,
        ind_registry_pattern=ind_registry_pattern,
        income_vars=income_vars,
        bef_registry_pattern=bef_registry_pattern,
        akm_registry_pattern=akm_registry_pattern,
        uddf_file_path=uddf_file_path,
        income_temporal_range=income_temporal_range,
        vital_df=vital_df,
        did_config=did_cfg,
    )

    out: dict[str, Any] = dict(res)

    # Overall dynamic curve
    if "att_gt" in res:
        cfg_json = json.dumps(did_cfg)
        out["att_gt_overall"] = res["att_gt"]
        out["dynamic_overall"] = _did_aggregate_rust(
            res["att_gt"], cfg_json, "dynamic", confidence, uniform_bands
        )

    # Gender split
    out["dynamic_by_gender"] = run_gender_split_dynamic(
        res["panel"],
        did_cfg,
        genders=gender_values,
        confidence=confidence,
        uniform_bands=uniform_bands,
    )

    # Socioeconomic moderation
    out["dynamic_by_socio13"] = run_category_split_dynamic(
        res["panel"],
        did_cfg,
        category_col="socio13_cat",
        categories=socio13_order,
        confidence=confidence,
        uniform_bands=uniform_bands,
    )

    # Optional: emit Typst source files for plots (no rendering)
    if typst_output_dir is not None:
        out_dir = Path(typst_output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            from ._internal import did_typst_write_py as _did_typst_write  # type: ignore

            if "dynamic_overall" in out and isinstance(
                out["dynamic_overall"], pl.DataFrame
            ):
                fp = out_dir / "dynamic_overall.typ"
                _did_typst_write(out["dynamic_overall"], str(fp), "dynamic")

            dyn_gender = out.get("dynamic_by_gender", {}) or {}
            if isinstance(dyn_gender, dict):
                for g, df in dyn_gender.items():
                    if isinstance(df, pl.DataFrame) and df.height > 0:
                        fp = out_dir / f"dynamic_gender_{g}.typ"
                        _did_typst_write(df, str(fp), "dynamic")

            dyn_soc = out.get("dynamic_by_socio13", {}) or {}
            if isinstance(dyn_soc, dict):
                for cat, df in dyn_soc.items():
                    if isinstance(df, pl.DataFrame) and df.height > 0:
                        safe = str(cat).replace("/", "-").replace(" ", "_")
                        fp = out_dir / f"dynamic_socio13_{safe}.typ"
                        _did_typst_write(df, str(fp), "dynamic")
            out["typst_files_dir"] = str(out_dir)
        except Exception as e:  # noqa: BLE001
            out["typst_error"] = f"Typst file generation failed: {e}"

    # Optional plotting: save event-study plots for overall + splits (matplotlib or Rust PNG/PDF)
    if typst_output_dir is None and plot_output_dir is not None:
        out_dir = Path(plot_output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        plots: dict[str, str] = {}
        used_rust = False

        if plot_via_rust:
            try:
                # This function exists only when compiled with --features viz
                from ._internal import did_plot_py as _did_plot_viz_rust  # type: ignore

                if "dynamic_overall" in out and isinstance(
                    out["dynamic_overall"], pl.DataFrame
                ):
                    fp = out_dir / f"dynamic_overall.{plot_format}"
                    _did_plot_viz_rust(
                        out["dynamic_overall"], str(fp), "dynamic", plot_format
                    )
                    plots["overall"] = str(fp)

                dyn_gender = out.get("dynamic_by_gender", {}) or {}
                if isinstance(dyn_gender, dict):
                    for g, df in dyn_gender.items():
                        if isinstance(df, pl.DataFrame) and df.height > 0:
                            fp = out_dir / f"dynamic_gender_{g}.{plot_format}"
                            _did_plot_viz_rust(df, str(fp), "dynamic", plot_format)
                            plots[f"gender_{g}"] = str(fp)

                dyn_soc = out.get("dynamic_by_socio13", {}) or {}
                if isinstance(dyn_soc, dict):
                    for cat, df in dyn_soc.items():
                        if isinstance(df, pl.DataFrame) and df.height > 0:
                            safe = str(cat).replace("/", "-").replace(" ", "_")
                            fp = out_dir / f"dynamic_socio13_{safe}.{plot_format}"
                            _did_plot_viz_rust(df, str(fp), "dynamic", plot_format)
                            plots[f"socio13_{cat}"] = str(fp)
                used_rust = True
            except Exception as e:  # noqa: BLE001
                out["plotting_error_rust_viz"] = (
                    f"Rust viz failed, falling back to matplotlib: {e}"
                )

        if not used_rust:
            try:
                from .plotting import plot_event_study

                if "dynamic_overall" in out and isinstance(
                    out["dynamic_overall"], pl.DataFrame
                ):
                    fp = out_dir / f"dynamic_overall.{plot_format}"
                    plot_event_study(
                        out["dynamic_overall"],
                        title="Dynamic Effects — Overall",
                        xlabel="Event time",
                        ylabel=outcome_var,
                        output_path=str(fp),
                    )
                    plots["overall"] = str(fp)

                dyn_gender = out.get("dynamic_by_gender", {}) or {}
                if isinstance(dyn_gender, dict):
                    for g, df in dyn_gender.items():
                        if isinstance(df, pl.DataFrame) and df.height > 0:
                            fp = out_dir / f"dynamic_gender_{g}.{plot_format}"
                            plot_event_study(
                                df,
                                title=f"Dynamic Effects — Gender {g}",
                                xlabel="Event time",
                                ylabel=outcome_var,
                                output_path=str(fp),
                            )
                            plots[f"gender_{g}"] = str(fp)

                dyn_soc = out.get("dynamic_by_socio13", {}) or {}
                if isinstance(dyn_soc, dict):
                    for cat, df in dyn_soc.items():
                        if isinstance(df, pl.DataFrame) and df.height > 0:
                            fp = out_dir / f"dynamic_socio13_{cat}.{plot_format}"
                            plot_event_study(
                                df,
                                title=f"Dynamic Effects — Socio13 {cat}",
                                xlabel="Event time",
                                ylabel=outcome_var,
                                output_path=str(fp),
                            )
                            plots[f"socio13_{cat}"] = str(fp)
            except ImportError as e:
                out["plotting_error"] = f"Plotting skipped (missing dependency): {e}"

        if plots:
            out["plots"] = plots

    return out
