"""
Epidemiological Analysis Plugin

This plugin provides high-performance epidemiological analysis tools including:
- Case-control matching with proper risk-set sampling methodology
- Temporal data extraction from registry files with dynamic year ranges
- Optimized Rust implementations for large-scale data processing
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Tuple

import polars as pl

if TYPE_CHECKING:
    from matching_plugin.typing import PolarsDataType

from matching_plugin._internal import __version__ as __version__  # type: ignore
from matching_plugin._internal import (
    did_aggregate_py as _did_aggregate_rust,  # type: ignore
)
from matching_plugin._internal import did_att_gt_py as _did_att_gt_rust  # type: ignore
from matching_plugin._internal import (
    did_panel_info_py as _did_panel_info_rust,  # type: ignore
)
from matching_plugin._internal import (
    extract_cohabitation_status_py as _extract_cohabitation_rust,
)  # type: ignore
from matching_plugin._internal import (
    extract_ethnicity_temporal_py as _extract_ethnicity_rust,
)  # type: ignore
from matching_plugin._internal import (
    extract_highest_education_level_batched_py as _extract_education_batched_rust,
)  # type: ignore
from matching_plugin._internal import (
    extract_highest_education_level_py as _extract_education_rust,
)  # type: ignore
from matching_plugin._internal import (
    extract_parent_income_timeseries_py as _extract_parent_income_rust,
)  # type: ignore
from matching_plugin._internal import (
    extract_parent_socio13_py as _extract_parent_socio13_rust,
)  # type: ignore
from matching_plugin._internal import (
    extract_temporal_data_batched_py as _extract_temporal_batched_rust,
)  # type: ignore
from matching_plugin._internal import (
    extract_temporal_data_dynamic_year_py as _extract_temporal_rust,
)  # type: ignore
from matching_plugin._internal import (
    format_match_output as _format_match_output_rust,  # type: ignore
)
from matching_plugin._internal import (
    match_scd_cases as _match_scd_cases_rust,  # type: ignore
)
from matching_plugin._internal import (
    match_scd_cases_with_diagnostics as _match_scd_cases_with_diag_rust,  # type: ignore
)

# Public utilities
from matching_plugin.inflation import adjust_for_inflation

__all__ = [
    "__version__",
    "complete_scd_matching_workflow",
    "create_match_output_format",
    "extract_temporal_data",
    "extract_temporal_data_batched",
    "extract_highest_education_level",
    "extract_highest_education_level_batched",
    "extract_ethnicity_categories",
    "extract_parent_socio13",
    "extract_cohabitation_status",
    "extract_parent_income_timeseries",
    "compute_att_gt",
    "get_panel_info",
    "aggregate_effects",
    "debug_did_cells",
    "build_parent_did_panel",
    "match_scd_cases_with_diagnostics",
    "run_full_parent_income_pipeline",
    "build_did_config",
    "run_gender_split_dynamic",
    "run_category_split_dynamic",
    "run_parent_income_study",
    "prepare_matching_input",
    "adjust_for_inflation",
]


def complete_scd_matching_workflow(
    mfr_data: pl.DataFrame,
    lpr_data: pl.DataFrame,
    vital_data: pl.DataFrame | None = None,
    matching_ratio: int = 5,
    birth_date_window_days: int = 30,
    parent_birth_date_window_days: int = 365,
    match_parent_birth_dates: bool = True,
    match_mother_birth_date_only: bool = False,
    require_both_parents: bool = False,
    match_parity: bool = True,
    match_birth_type: bool = False,
    algorithm: str = "spatial_index",
) -> pl.DataFrame:
    """
    Complete SCD case-control matching workflow with risk-set sampling.

    Combines MFR/LPR data, performs matching, and returns the standard output format.
    Cases are processed chronologically by diagnosis date to avoid immortal time bias.
    Optionally incorporates vital status data for temporal validity.

    Parameters
    ----------
    mfr_data : pl.DataFrame
        Output from process_mfr_data() - eligible population with parent info
    lpr_data : pl.DataFrame
        Output from process_lpr_data() - SCD status for all eligible children
    vital_data : pl.DataFrame, optional
        Output from process_vital_status() - death/emigration events for children and parents
        If provided, ensures individuals and parents are alive/present at matching time
    matching_ratio : int, default 5
        Number of controls to match per case
    birth_date_window_days : int, default 30
        Maximum difference in days between case and control birth dates
    parent_birth_date_window_days : int, default 365
        Maximum difference in days between parent birth dates
    match_parent_birth_dates : bool, default True
        Whether to match on parent birth dates
    match_mother_birth_date_only : bool, default False
        Whether to match only on maternal birth dates
    require_both_parents : bool, default False
        Whether both parents are required for matching
    match_parity : bool, default True
        Whether to match on parity (birth order)
    match_birth_type : bool, default False
        Whether to match on birth type (singleton, doubleton, tripleton, quadleton, multiple)
        Requires 'birth_type' column in input data
    algorithm : str, default "spatial_index"
        Algorithm to use for matching. Options:
        - "spatial_index": Optimized with parallel processing and spatial indexing
        - "partitioned_parallel": Ultra-optimized with advanced data structures (20-60% faster than spatial_index)

    Returns
    -------
    pl.DataFrame
        Output format: MATCH_INDEX, PNR, ROLE, INDEX_DATE
        - MATCH_INDEX: Unique identifier for each case-control group (1:X matching)
        - PNR: Person identifier
        - ROLE: "case" or "control"
        - INDEX_DATE: SCD diagnosis date from the case

        When vital_data is provided:
        - Ensures children and parents are alive/present at matching time
        - Individuals who died or emigrated before case diagnosis cannot serve as controls
        - Chronological processing with proper temporal validity
    """
    # Validate algorithm parameter
    valid_algorithms = ["spatial_index", "partitioned_parallel"]
    if algorithm not in valid_algorithms:
        raise ValueError(
            f"Invalid algorithm '{algorithm}'. Must be one of: {valid_algorithms}"
        )

    algorithm_names = {
        "spatial_index": "optimized with spatial indexing",
        "partitioned_parallel": "ultra-optimized with advanced data structures",
    }

    if vital_data is not None:
        print(
            f"Starting SCD case-control matching with vital status using {algorithm_names[algorithm]}..."
        )
    else:
        print(
            f"Starting SCD case-control matching using {algorithm_names[algorithm]}..."
        )

    # Combine MFR and LPR data
    combined_data = mfr_data.join(lpr_data, on="PNR", how="inner")
    print(f"Combined dataset: {len(combined_data):,} individuals")

    if vital_data is not None:
        print(f"Vital events data: {len(vital_data):,} events")

    # Perform risk-set sampling matching (with or without vital data)
    config = {
        "matching": {
            "birth_date_window_days": birth_date_window_days,
            "parent_birth_date_window_days": parent_birth_date_window_days,
            "match_parent_birth_dates": match_parent_birth_dates,
            "match_mother_birth_date_only": match_mother_birth_date_only,
            "require_both_parents": require_both_parents,
            "match_parity": match_parity,
            "match_birth_type": match_birth_type,
            "matching_ratio": matching_ratio,
        },
        "algorithm": algorithm,
    }

    matched_cases = _match_scd_cases_rust(combined_data, vital_data, json.dumps(config))

    # Transform to requested output format
    output_df = _format_match_output_rust(matched_cases)

    print(f"Matching complete: {len(output_df):,} records")
    print(f"Match groups: {output_df['MATCH_INDEX'].n_unique():,}")
    print(f"Cases: {(output_df['ROLE'] == 'case').sum():,}")
    print(f"Controls: {(output_df['ROLE'] == 'control').sum():,}")

    return output_df


def create_match_output_format(matched_cases_df: pl.DataFrame) -> pl.DataFrame:
    """
    Transform matched cases into the standard output format.

    Parameters
    ----------
    matched_cases_df : pl.DataFrame
        Matched cases DataFrame from the Rust matching functions

    Returns
    -------
    pl.DataFrame
        Standard output format: MATCH_INDEX, PNR, ROLE, INDEX_DATE
        - MATCH_INDEX: Unique identifier for each case-control group
        - PNR: Person identifier
        - ROLE: "case" or "control"
        - INDEX_DATE: SCD diagnosis date from the case (same for all members of match group)
    """
    return _format_match_output_rust(matched_cases_df)


def extract_temporal_data(
    df: pl.DataFrame,
    identifier_col: str,
    index_date_col: str,
    registry_path_pattern: str,
    variable_col: str,
    temporal_range: Tuple[int, int] = (-1, 1),
    additional_cols: list[str] | None = None,
    use_cache: bool = True,
) -> pl.DataFrame:
    """
    Extract temporal data from registry files with dynamic year ranges.

    This function provides high-performance extraction of temporal data from registry
    files based on dynamic year ranges relative to index dates. Uses optimized Rust
    implementation for efficient processing of large datasets.

    Parameters
    ----------
    df : pl.DataFrame
        Input dataframe with identifiers and index dates
    identifier_col : str
        Column name for unique identifiers (e.g., "PNR")
    index_date_col : str
        Column name for index dates (e.g., "diagnosis_date")
    registry_path_pattern : str
        Path pattern for registry files supporting glob patterns
        (e.g., "/data/registries/registry_*.parquet")
    variable_col : str
        Column name for the main variable to extract from registry
    temporal_range : Tuple[int, int], default=(-1, 1)
        Range of years relative to index year (start_offset, end_offset)
        - (-1, 1): Extract data from 1 year before to 1 year after index
        - (-2, 0): Extract data from 2 years before to index year
    additional_cols : list[str] | None, default=None
        Additional columns to extract from registry files
    use_cache : bool, default=True
        Whether to cache registry files for repeated calls (improves performance)

    Returns
    -------
    pl.DataFrame
        DataFrame with temporal data joined from registry files containing:
        - Original identifier and index date columns
        - ARET: Registry year for each extracted record
        - RELATIVE_YEAR: Years relative to index year (e.g., -1, 0, 1)
        - Variable columns from registry files

    Examples
    --------
    Extract prescription data around diagnosis dates:

    >>> cases_df = pl.DataFrame({
    ...     "PNR": ["123456", "789012"],
    ...     "diagnosis_date": ["2020-05-15", "2021-08-20"]
    ... })
    >>> prescriptions = extract_temporal_data(
    ...     df=cases_df,
    ...     identifier_col="PNR",
    ...     index_date_col="diagnosis_date",
    ...     registry_path_pattern="/data/prescriptions/lms_*.parquet",
    ...     variable_col="ATC_CODE",
    ...     temporal_range=(-2, 1),  # 2 years before to 1 year after
    ...     additional_cols=["DOSE", "STRENGTH"]
    ... )

    Extract hospital admissions with 1-year window:

    >>> admissions = extract_temporal_data(
    ...     df=cases_df,
    ...     identifier_col="PNR",
    ...     index_date_col="diagnosis_date",
    ...     registry_path_pattern="/data/lpr/lpr_*.ipc",
    ...     variable_col="ICD10_CODE",
    ...     temporal_range=(-1, 1)
    ... )

    Notes
    -----
    - Registry files must contain the identifier column and year information
    - If ARET column is missing, it will be inferred from filename
    - Supports .parquet, .ipc, .feather, and .arrow file formats
    - Files are processed in deterministic sorted order
    - Uses LRU caching for repeated registry file access
    """
    return _extract_temporal_rust(
        df,
        identifier_col,
        index_date_col,
        registry_path_pattern,
        variable_col,
        temporal_range,
        additional_cols,
        use_cache,
    )


def extract_parent_socio13(
    df: pl.DataFrame,
    identifier_col: str,
    index_date_col: str,
    akm_registry_pattern: str,
    year_offset: int = -1,
) -> pl.DataFrame:
    return _extract_parent_socio13_rust(
        df, identifier_col, index_date_col, akm_registry_pattern, year_offset
    )


def extract_cohabitation_status(
    df: pl.DataFrame,
    identifier_col: str,
    index_date_col: str,
    bef_registry_pattern: str,
    year_offset: int = -1,
) -> pl.DataFrame:
    return _extract_cohabitation_rust(
        df, identifier_col, index_date_col, bef_registry_pattern, year_offset
    )


def extract_parent_income_timeseries(
    df: pl.DataFrame,
    identifier_col: str,
    index_date_col: str,
    ind_registry_pattern: str,
    income_vars: list[str],
    temporal_range: tuple[int, int] = (-10, 10),
) -> pl.DataFrame:
    return _extract_parent_income_rust(
        df,
        identifier_col,
        index_date_col,
        ind_registry_pattern,
        income_vars,
        temporal_range,
    )


def _std_find(df: pl.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name in df.columns:
            return name
        if name.lower() in cols:
            return cols[name.lower()]
    return None


def _std_match_df(match_df: pl.DataFrame) -> pl.DataFrame:
    # Accept common aliases and enforce canonical names and types
    pnr = _std_find(match_df, ["PNR", "pnr", "CPR", "id", "child_pnr"])
    idx = _std_find(
        match_df, ["INDEX_DATE", "index_date", "SCD_DATE", "diagnosis_date"]
    )  # noqa: N816
    role = _std_find(match_df, ["ROLE", "role", "treated", "is_case"])  # noqa: N816

    out = match_df.clone()

    if pnr is None:
        raise ValueError("match_df requires a child identifier column (PNR/CPR)")
    if pnr != "PNR":
        out = out.rename({pnr: "PNR"})

    if idx is None:
        raise ValueError(
            "match_df requires an index date (INDEX_DATE/SCD_DATE/index_date)"
        )
    if idx != "INDEX_DATE":
        out = out.rename({idx: "INDEX_DATE"})
    # Cast INDEX_DATE to Date if possible
    if out.schema.get("INDEX_DATE") not in (pl.Date, pl.Datetime):
        out = out.with_columns(
            pl.col("INDEX_DATE").str.strptime(pl.Date, strict=False, exact=False)
        )

    if role is None:
        # Try to derive ROLE from SCD_STATUS or treated flag
        scd_status = _std_find(out, ["SCD_STATUS", "scd_status"])  # optional
        if scd_status is not None:
            out = out.with_columns(
                pl.when(pl.col(scd_status) == "SCD")
                .then(pl.lit("case"))
                .otherwise(pl.lit("control"))
                .alias("ROLE")
            )
        else:
            treated = _std_find(out, ["treated", "is_treated", "is_case"])  # optional
            if treated is None:
                raise ValueError(
                    "match_df requires ROLE or enough info to derive it (SCD_STATUS/treated)"
                )
            out = out.with_columns(
                pl.when(pl.col(treated).cast(pl.Int8) == 1)
                .then(pl.lit("case"))
                .otherwise(pl.lit("control"))
                .alias("ROLE")
            )
    elif role != "ROLE":
        # Normalize role values to {case, control}
        out = out.rename({role: "ROLE"}).with_columns(
            pl.when(pl.col("ROLE").cast(pl.Utf8).str.to_lowercase() == "case")
            .then(pl.lit("case"))
            .otherwise(pl.lit("control"))
            .alias("ROLE")
        )

    return out.select(
        [
            "PNR",
            "INDEX_DATE",
            "ROLE",
            *[
                c
                for c in match_df.columns
                if c not in {pnr or "PNR", idx or "INDEX_DATE", role or "ROLE"}
            ],
        ]
    )


def _std_relations_df(rel: pl.DataFrame) -> pl.DataFrame:
    # Normalize parent column names and ensure presence
    pnr = _std_find(rel, ["PNR", "pnr", "CPR", "child_pnr"]) or "PNR"
    m = _std_find(rel, ["CPR_MODER", "CPR_MOR", "MOR_CPR", "MOTHER_CPR", "MOTHER_ID"])  # noqa: N816
    f = _std_find(rel, ["CPR_FADER", "CPR_FAR", "FAR_CPR", "FATHER_CPR", "FATHER_ID"])  # noqa: N816
    out = rel.clone()
    if m is None or f is None:
        missing = [n for n, v in {"CPR_MODER": m, "CPR_FADER": f}.items() if v is None]
        raise ValueError(
            f"relations_df missing required parent columns (accepted aliases): {missing}"
        )
    rename_map = {}
    if pnr != "PNR":
        rename_map[pnr] = "PNR"
    if m != "CPR_MODER":
        rename_map[m] = "CPR_MODER"
    if f != "CPR_FADER":
        rename_map[f] = "CPR_FADER"
    if rename_map:
        out = out.rename(rename_map)
    # Keep only necessary columns and drop duplicates on PNR
    out = out.select(["PNR", "CPR_MODER", "CPR_FADER"]).unique(maintain_order=True)
    return out


def _ensure_cols(df: pl.DataFrame, needed: dict[str, "PolarsDataType"]) -> pl.DataFrame:
    out = df
    existing = set(df.columns)
    to_add = {k: v for k, v in needed.items() if k not in existing}
    if to_add:
        out = out.with_columns(
            [pl.lit(None, dtype=dt).alias(name) for name, dt in to_add.items()]
        )
    return out


def build_parent_did_panel(
    match_df: pl.DataFrame,
    relations_df: pl.DataFrame,
    *,
    ind_registry_pattern: str,
    income_vars: list[str],
    bef_registry_pattern: str | None = None,
    akm_registry_pattern: str | None = None,
    uddf_file_path: str | None = None,
    income_temporal_range: tuple[int, int] = (-10, 10),
) -> pl.DataFrame:
    # Normalize inputs (accept aliases, enforce schema & types)
    match_df = _std_match_df(match_df)
    relations_df = _std_relations_df(relations_df)

    # Prepare minimal child-date pairs and lazy views
    base_unique_df = match_df.select(["PNR", "INDEX_DATE"]).unique(maintain_order=True)
    match_lf = match_df.lazy()
    rel_lf = relations_df.lazy()
    base_lf = match_lf.join(rel_lf, on="PNR", how="inner")

    # Income time series for both parents (wide MOR_/FAR_ per child-year)
    # The extractor requires parent CPRs; attach minimal parent IDs to the unique child-date pairs
    base_income_input = base_unique_df.join(
        relations_df.select(["PNR", "CPR_MODER", "CPR_FADER"]), on="PNR", how="left"
    )
    income_wide = extract_parent_income_timeseries(
        df=base_income_input,
        identifier_col="PNR",
        index_date_col="INDEX_DATE",
        ind_registry_pattern=ind_registry_pattern,
        income_vars=income_vars,
        temporal_range=income_temporal_range,
    )
    # Ensure expected columns and attach parent IDs lazily
    base_income_cols: dict[str, "PolarsDataType"] = {
        "ARET": pl.Int32,
        "RELATIVE_YEAR": pl.Int32,
    }
    for v in income_vars:
        base_income_cols[f"MOR_{v}"] = pl.Float64
        base_income_cols[f"FAR_{v}"] = pl.Float64
    income_wide = _ensure_cols(income_wide, base_income_cols)
    income_wide_lf = income_wide.lazy().join(
        rel_lf.select(["PNR", "CPR_MODER", "CPR_FADER"]), on="PNR", how="left"
    )

    # Build long panel by stacking mother and father rows
    long_parts: list[pl.LazyFrame] = []
    # Mother
    mother_cols = {f"MOR_{v}": v for v in income_vars}
    mother_df = income_wide_lf.select(
        [
            "PNR",
            "INDEX_DATE",
            pl.col("ARET").alias("year"),
            pl.col("RELATIVE_YEAR").alias("event_time"),
            pl.col("CPR_MODER").alias("parent_pnr"),
            *[pl.col(k).alias(v) for k, v in mother_cols.items()],
        ]
    ).with_columns([pl.lit("F").alias("gender")])
    long_parts.append(mother_df)
    # Father
    father_cols = {f"FAR_{v}": v for v in income_vars}
    father_df = income_wide_lf.select(
        [
            "PNR",
            "INDEX_DATE",
            pl.col("ARET").alias("year"),
            pl.col("RELATIVE_YEAR").alias("event_time"),
            pl.col("CPR_FADER").alias("parent_pnr"),
            *[pl.col(k).alias(v) for k, v in father_cols.items()],
        ]
    ).with_columns([pl.lit("M").alias("gender")])
    long_parts.append(father_df)

    panel_lf = pl.concat(long_parts, how="vertical")

    # Join case/control and compute cohort (first.treat) and treated
    panel_lf = panel_lf.join(
        match_lf.select(["PNR", "INDEX_DATE", "ROLE"]),
        on=["PNR", "INDEX_DATE"],
        how="left",
    )
    panel_lf = panel_lf.with_columns(
        [
            pl.col("INDEX_DATE").dt.year().alias("index_year"),
            (pl.col("ROLE") == "case").cast(pl.Int8).alias("treated"),
        ]
    )
    panel_lf = panel_lf.with_columns(
        [
            pl.when(pl.col("treated") == 1)
            .then(pl.col("index_year"))
            .otherwise(pl.lit(0))
            .cast(pl.Int64)
            .alias("first.treat"),
        ]
    )

    # Optional baseline covariates (measured at index_year-1)
    if akm_registry_pattern is not None:
        # Socio extractor requires parent CPRs present
        base_socio_input = base_unique_df.join(
            relations_df.select(["PNR", "CPR_MODER", "CPR_FADER"]), on="PNR", how="left"
        )
        socio = extract_parent_socio13(
            df=base_socio_input,
            identifier_col="PNR",
            index_date_col="INDEX_DATE",
            akm_registry_pattern=akm_registry_pattern,
            year_offset=-1,
        )
        socio_lf = socio.lazy().join(
            rel_lf.select(["PNR", "CPR_MODER", "CPR_FADER"]), on="PNR", how="left"
        )
        socio_long = pl.concat(
            [
                socio_lf.select(
                    [
                        "PNR",
                        "INDEX_DATE",
                        pl.col("MOR_SOCIO13_CAT").alias("socio13_cat"),
                        pl.col("CPR_MODER").alias("parent_pnr"),
                    ]
                ).with_columns([pl.lit("F").alias("gender")]),
                socio_lf.select(
                    [
                        "PNR",
                        "INDEX_DATE",
                        pl.col("FAR_SOCIO13_CAT").alias("socio13_cat"),
                        pl.col("CPR_FADER").alias("parent_pnr"),
                    ]
                ).with_columns([pl.lit("M").alias("gender")]),
            ],
            how="vertical",
        )
        panel_lf = panel_lf.join(
            socio_long.select(
                ["PNR", "INDEX_DATE", "parent_pnr", "gender", "socio13_cat"]
            ),
            on=["PNR", "INDEX_DATE", "parent_pnr", "gender"],
            how="left",
        )

    if bef_registry_pattern is not None:
        # Cohabitation extractor requires parent CPRs present
        base_cohab_input = base_unique_df.join(
            relations_df.select(["PNR", "CPR_MODER", "CPR_FADER"]), on="PNR", how="left"
        )
        cohab = extract_cohabitation_status(
            df=base_cohab_input,
            identifier_col="PNR",
            index_date_col="INDEX_DATE",
            bef_registry_pattern=bef_registry_pattern,
            year_offset=-1,
        )
        cohab_lf = cohab.lazy().join(
            rel_lf.select(["PNR", "CPR_MODER", "CPR_FADER"]), on="PNR", how="left"
        )
        cohab_long = pl.concat(
            [
                cohab_lf.select(
                    [
                        "PNR",
                        "INDEX_DATE",
                        pl.col("MOR_COHAB_STATUS").alias("cohab_status"),
                        pl.col("CPR_MODER").alias("parent_pnr"),
                    ]
                ).with_columns([pl.lit("F").alias("gender")]),
                cohab_lf.select(
                    [
                        "PNR",
                        "INDEX_DATE",
                        pl.col("FAR_COHAB_STATUS").alias("cohab_status"),
                        pl.col("CPR_FADER").alias("parent_pnr"),
                    ]
                ).with_columns([pl.lit("M").alias("gender")]),
            ],
            how="vertical",
        )
        panel_lf = panel_lf.join(
            cohab_long.select(
                ["PNR", "INDEX_DATE", "parent_pnr", "gender", "cohab_status"]
            ),
            on=["PNR", "INDEX_DATE", "parent_pnr", "gender"],
            how="left",
        )

    # Child ethnicity at baseline (-1) as covariate (same value for both parents)
    if bef_registry_pattern is not None:
        # Ethnicity extractor requires parent CPRs present
        base_eth_input = base_unique_df.join(
            relations_df.select(["PNR", "CPR_MODER", "CPR_FADER"]), on="PNR", how="left"
        )
        eth = extract_ethnicity_categories(
            df=base_eth_input,
            identifier_col="PNR",
            index_date_col="INDEX_DATE",
            bef_registry_pattern=bef_registry_pattern,
            temporal_range=(-1, -1),
        )
        # Keep baseline only, attach as child_ethnicity
        eth_lf = (
            eth.lazy()
            .filter(pl.col("RELATIVE_YEAR") == -1)
            .select(
                [
                    "PNR",
                    "INDEX_DATE",
                    pl.col("ethnicity_category").alias("child_ethnicity"),
                ]
            )
        )
        panel_lf = panel_lf.join(eth_lf, on=["PNR", "INDEX_DATE"], how="left")

    # Parent highest education at baseline (-1) as covariate (separate per parent)
    if uddf_file_path is not None:
        # Mothers
        mothers = base_lf.select(
            [
                pl.col("PNR"),
                pl.col("INDEX_DATE"),
                pl.col("CPR_MODER").alias("_ID"),
            ]
        )
        edu_m_input = mothers.select(
            [pl.col("INDEX_DATE"), pl.col("_ID").alias("PNR")]
        ).collect()
        edu_m = extract_highest_education_level(
            df=edu_m_input,
            identifier_col="PNR",
            index_date_col="INDEX_DATE",
            uddf_file_path=uddf_file_path,
        ).rename({"highest_education_level": "mother_education"})
        edu_m_lf = (
            edu_m.lazy()
            .join(
                mothers,
                left_on=["PNR", "INDEX_DATE"],
                right_on=["PNR", "INDEX_DATE"],
                how="left",
            )
            .select(
                [
                    "INDEX_DATE",
                    pl.col("_ID").alias("parent_pnr"),
                    pl.col("mother_education").alias("education_level"),
                ]
            )
            .with_columns([pl.lit("F").alias("gender")])
        )

        # Fathers
        fathers = base_lf.select(
            [
                pl.col("PNR"),
                pl.col("INDEX_DATE"),
                pl.col("CPR_FADER").alias("_ID"),
            ]
        )
        edu_f_input = fathers.select(
            [pl.col("INDEX_DATE"), pl.col("_ID").alias("PNR")]
        ).collect()
        edu_f = extract_highest_education_level(
            df=edu_f_input,
            identifier_col="PNR",
            index_date_col="INDEX_DATE",
            uddf_file_path=uddf_file_path,
        ).rename({"highest_education_level": "father_education"})
        edu_f_lf = (
            edu_f.lazy()
            .join(
                fathers,
                left_on=["PNR", "INDEX_DATE"],
                right_on=["PNR", "INDEX_DATE"],
                how="left",
            )
            .select(
                [
                    "INDEX_DATE",
                    pl.col("_ID").alias("parent_pnr"),
                    pl.col("father_education").alias("education_level"),
                ]
            )
            .with_columns([pl.lit("M").alias("gender")])
        )

        edu_long_lf = pl.concat([edu_m_lf, edu_f_lf], how="vertical")
        panel_lf = panel_lf.join(
            edu_long_lf,
            on=["INDEX_DATE", "parent_pnr", "gender"],
            how="left",
        )

    keep_cols = [
        "PNR",
        "INDEX_DATE",
        "parent_pnr",
        "gender",
        "year",
        "event_time",
        "first.treat",
        "treated",
    ] + income_vars
    if akm_registry_pattern is not None:
        keep_cols.append("socio13_cat")
    if bef_registry_pattern is not None:
        keep_cols.append("cohab_status")
        keep_cols.append("child_ethnicity")
    if uddf_file_path is not None:
        keep_cols.append("education_level")

    # Ensure keep columns are present, add missing with nulls for a stable schema
    keep_types: dict[str, "PolarsDataType"] = {
        "PNR": pl.Utf8,
        "INDEX_DATE": pl.Date,
        "parent_pnr": pl.Utf8,
        "gender": pl.Utf8,
        "year": pl.Int32,
        "event_time": pl.Int32,
        "first.treat": pl.Int64,
        "treated": pl.Int8,
    }
    for v in income_vars:
        keep_types[v] = pl.Float64
    if akm_registry_pattern is not None:
        keep_types["socio13_cat"] = pl.Utf8
    if bef_registry_pattern is not None:
        keep_types["cohab_status"] = pl.Utf8
        keep_types["child_ethnicity"] = pl.Utf8
    if uddf_file_path is not None:
        keep_types["education_level"] = pl.Utf8

    panel_df = panel_lf.collect()
    panel_df = _ensure_cols(panel_df, keep_types).select(list(keep_types.keys()))
    return panel_df


def debug_did_cells(
    df: pl.DataFrame,
    config: dict | str,
    limit: int | None = 50,
) -> pl.DataFrame:
    cfg = config if isinstance(config, dict) else json.loads(config)
    gcol = cfg["group_var"] if cfg.get("group_var") else cfg["treatment_var"]
    tcol = cfg["time_var"]
    control_group = cfg.get("control_group", "NotYetTreated")

    tlist = (
        df.select(pl.col(tcol).unique()).to_series().to_list() if df.height > 0 else []
    )
    tlist = sorted([int(x) for x in tlist if x is not None])
    glist = (
        df.select(pl.col(gcol).unique()).to_series().to_list() if df.height > 0 else []
    )
    glist = sorted([int(x) for x in glist if x not in (None, 0)])
    union_vals = sorted(set(glist) | set(tlist))
    idx_map = {v: i + 1 for i, v in enumerate(union_vals)}

    def _idx(val: int | None) -> int | None:
        if val is None:
            return None
        return idx_map.get(int(val))

    df_std = df.with_columns(
        [
            pl.col(gcol).map_elements(_idx, return_dtype=pl.Int64).alias("_g_idx"),
            pl.col(tcol).map_elements(_idx, return_dtype=pl.Int64).alias("_t_idx"),
        ]
    )

    rows: list[dict] = []
    for g in glist:
        g_idx = idx_map[g]
        for t in tlist:
            pret = (g - 1) if t >= g else (t - 1)
            if pret not in tlist:
                continue
            t_idx = idx_map[t]
            pret_idx = idx_map[pret]
            max_idx = max(t_idx, pret_idx)

            dta = df_std.filter(pl.col(tcol).is_in([t, pret]))
            is_treated = pl.col("_g_idx") == g_idx
            if control_group == "NeverTreated":
                is_control = pl.col(gcol) == 0
            else:
                is_control = (pl.col(gcol) == 0) | (
                    (pl.col("_g_idx") > max_idx) & (pl.col("_g_idx") != g_idx)
                )

            treated_post = dta.filter(is_treated & (pl.col(tcol) == t)).height
            treated_pre = dta.filter(is_treated & (pl.col(tcol) == pret)).height
            control_post = dta.filter(is_control & (pl.col(tcol) == t)).height
            control_pre = dta.filter(is_control & (pl.col(tcol) == pret)).height

            rows.append(
                {
                    "group": g,
                    "time": t,
                    "pret": pret,
                    "n_treated_pre": treated_pre,
                    "n_treated_post": treated_post,
                    "n_control_pre": control_pre,
                    "n_control_post": control_post,
                    "has_all_cells": all(
                        x > 0
                        for x in [treated_pre, treated_post, control_pre, control_post]
                    ),
                }
            )

    out = pl.DataFrame(rows)
    if limit is not None and out.height > limit:
        return out.sort(["has_all_cells", "group", "time"]).head(limit)
    return out


def extract_temporal_data_batched(
    df: pl.DataFrame,
    batch_size: int,
    identifier_col: str,
    index_date_col: str,
    registry_path_pattern: str,
    variable_col: str,
    temporal_range: Tuple[int, int] = (-1, 1),
    additional_cols: list[str] | None = None,
    use_cache: bool = True,
) -> pl.DataFrame:
    """
    Extract temporal data in batches for memory-efficient processing of large datasets.

    This function processes large input DataFrames in smaller batches to manage memory
    usage while maintaining high performance through the Rust implementation.

    Parameters
    ----------
    df : pl.DataFrame
        Input dataframe with identifiers and index dates
    batch_size : int
        Number of rows to process per batch (e.g., 5000, 10000)
    identifier_col : str
        Column name for unique identifiers
    index_date_col : str
        Column name for index dates
    registry_path_pattern : str
        Path pattern for registry files (supports globbing)
    variable_col : str
        Column name for the main variable to extract from registry
    temporal_range : Tuple[int, int], default=(-1, 1)
        Range of years relative to index year (start_offset, end_offset)
    additional_cols : list[str] | None, default=None
        Additional columns to extract from registry files
    use_cache : bool, default=True
        Whether to cache registry files (highly recommended for batched processing)

    Returns
    -------
    pl.DataFrame
        Combined results from all batches with same structure as extract_temporal_data()

    Examples
    --------
    Process a large cohort in batches:

    >>> large_cohort = pl.read_parquet("large_cohort.parquet")  # 100,000+ rows
    >>> temporal_data = extract_temporal_data_batched(
    ...     df=large_cohort,
    ...     batch_size=5000,
    ...     identifier_col="PNR",
    ...     index_date_col="index_date",
    ...     registry_path_pattern="/data/registry_*.parquet",
    ...     variable_col="CODE",
    ...     temporal_range=(-1, 1),
    ...     use_cache=True  # Important for batched processing
    ... )

    Notes
    -----
    - Registry files are cached across batches when use_cache=True
    - Batch size should be chosen based on available memory
    - Smaller batches reduce memory usage but may increase processing time
    - Results are identical to non-batched processing
    """
    return _extract_temporal_batched_rust(
        df,
        batch_size,
        identifier_col,
        index_date_col,
        registry_path_pattern,
        variable_col,
        temporal_range,
        additional_cols,
        use_cache,
    )


def match_scd_cases_with_diagnostics(
    df: pl.DataFrame,
    vital_df: pl.DataFrame | None,
    config: dict | str,
):
    """
    Run matching and return both matches and diagnostics.

    Returns a dict: {"matches": pl.DataFrame, "diagnostics": dict}
    """
    cfg_json = config if isinstance(config, str) else json.dumps(config)
    return _match_scd_cases_with_diag_rust(df, vital_df, cfg_json)


# Light re-export of the pipeline helpers for convenience
try:
    from .pipeline import (
        build_did_config,
        run_category_split_dynamic,
        run_full_parent_income_pipeline,
        run_gender_split_dynamic,
        run_parent_income_study,
    )  # noqa: F401
    from .prep import prepare_matching_input  # noqa: F401
except Exception:  # pragma: no cover - optional in minimal builds
    pass


def extract_highest_education_level(
    df: pl.DataFrame,
    identifier_col: str,
    index_date_col: str,
    uddf_file_path: str,
) -> pl.DataFrame:
    """
    Extract highest attained education level from UDDF register data.

    This function processes UDDF (education) register data to determine the highest
    education level achieved by each individual at their index date, accounting for
    temporal validity of education records.

    Parameters
    ----------
    df : pl.DataFrame
        Input dataframe with identifiers and index dates
    identifier_col : str
        Column name for unique identifiers (e.g., "PNR")
    index_date_col : str
        Column name for index dates (e.g., "diagnosis_date", "index_date")
    uddf_file_path : str
        Path to the UDDF register file (.parquet, .ipc, .feather, or .arrow)
        Must contain columns: identifier, HFAUDD, HF_VFRA, HF_VTIL

    Returns
    -------
    pl.DataFrame
        Original dataframe with added 'highest_education_level' column containing:
        - "short": Primary & lower secondary education (HFAUDD codes 10, 15)
        - "medium": Upper secondary & vocational education (HFAUDD codes 20, 30, 35)
        - "long": Tertiary education (HFAUDD codes 40, 50, 60, 70, 80)
        - "unknown": Missing or unclassified education (HFAUDD code 90)

    Notes
    -----
    Education Level Categorization (based on HFAUDD codes):
    - **Short education (10, 15)**: Primary & lower secondary, preparatory education
    - **Medium education (20, 30, 35)**: General upper secondary, vocational training
    - **Long education (40, 50, 60, 70, 80)**: Academy, bachelor's, master's, PhD programs
    - **Unknown (90)**: Missing, unclassified, or born ≤1920

    Temporal Validity:
    - Only education records valid at the index date are considered
    - Validity determined by: HF_VFRA ≤ index_date ≤ HF_VTIL
    - Missing HF_VFRA/HF_VTIL dates are treated as always valid

    Highest Level Selection:
    - Among temporally valid records, selects the highest education level
    - Excludes unknown/missing records (HFAUDD code 90) from ranking
    - If no valid education records exist, returns "unknown"

    Examples
    --------
    Extract education levels for a cohort at diagnosis:

    >>> cases_df = pl.DataFrame({
    ...     "PNR": ["123456789", "987654321"],
    ...     "diagnosis_date": ["2020-05-15", "2021-08-20"]
    ... })
    >>> education_df = extract_highest_education_level(
    ...     df=cases_df,
    ...     identifier_col="PNR",
    ...     index_date_col="diagnosis_date",
    ...     uddf_file_path="/data/registers/uddf_2021.parquet"
    ... )
    >>> print(education_df)
    │ PNR       │ diagnosis_date │ highest_education_level │
    │ str       │ date           │ str                     │
    ├───────────┼────────────────┼─────────────────────────┤
    │ 123456789 │ 2020-05-15     │ long                    │
    │ 987654321 │ 2021-08-20     │ medium                  │

    The function uses compile-time embedded HFAUDD categorization mapping for efficiency
    and processes ~5,370 different education codes automatically.
    """
    return _extract_education_rust(
        df,
        identifier_col,
        index_date_col,
        uddf_file_path,
    )


def extract_highest_education_level_batched(
    df: pl.DataFrame,
    batch_size: int,
    identifier_col: str,
    index_date_col: str,
    uddf_file_path: str,
) -> pl.DataFrame:
    """
    Extract highest education levels in batches for memory-efficient processing.

    This function processes large input DataFrames in smaller batches to manage memory
    usage while maintaining the same functionality as extract_highest_education_level.

    Parameters
    ----------
    df : pl.DataFrame
        Input dataframe with identifiers and index dates
    batch_size : int
        Number of rows to process per batch (e.g., 5000, 10000)
    identifier_col : str
        Column name for unique identifiers
    index_date_col : str
        Column name for index dates
    uddf_file_path : str
        Path to the UDDF register file

    Returns
    -------
    pl.DataFrame
        Combined results from all batches with same structure as extract_highest_education_level()

    Examples
    --------
    Process a large cohort in batches:

    >>> large_cohort = pl.read_parquet("large_cohort.parquet")  # 100,000+ rows
    >>> education_levels = extract_highest_education_level_batched(
    ...     df=large_cohort,
    ...     batch_size=10000,
    ...     identifier_col="PNR",
    ...     index_date_col="index_date",
    ...     uddf_file_path="/data/uddf_register.parquet"
    ... )

    Notes
    -----
    - Batch size should be chosen based on available memory
    - Smaller batches reduce memory usage but may increase processing time
    - Results are identical to non-batched processing
    - UDDF register file is loaded once per batch for efficiency
    """
    return _extract_education_batched_rust(
        df,
        batch_size,
        identifier_col,
        index_date_col,
        uddf_file_path,
    )


def extract_ethnicity_categories(
    df: pl.DataFrame,
    identifier_col: str,
    index_date_col: str,
    bef_registry_pattern: str,
    temporal_range: tuple[int, int] = (-1, 1),
) -> pl.DataFrame:
    """
    Extract SEPLINE-compliant ethnicity categories from BEF with parental lookups.

    For each individual/year window around the index date, this function:
    - Looks up the child's BEF row to get `OPR_LAND`, `IE_TYPE`, and parent CPRs
    - Looks up the mother's/father's BEF rows (by CPR) for the same `ARET` to get their `OPR_LAND`
    - Maps `OPR_LAND` to Danish/Western/Non-Western categories via compiled mapping
    - Applies SEPLINE rules using parent origins and `IE_TYPE`

    Parameters
    ----------
    df : pl.DataFrame
        Input dataframe with identifiers and index dates
    identifier_col : str
        Column name for identifiers (CPR/PNR)
    index_date_col : str
        Column name for index dates
    bef_registry_pattern : str
        Glob pattern to BEF files (e.g., "/data/bef_*.parquet")
    temporal_range : tuple[int, int], default (-1, 1)
        Year offsets around index year to search (inclusive)

    Returns
    -------
    pl.DataFrame
        Columns: identifier_col, index_date_col, ARET, RELATIVE_YEAR, ethnicity_category
    """
    return _extract_ethnicity_rust(
        df,
        identifier_col,
        index_date_col,
        bef_registry_pattern,
        temporal_range,
    )


def compute_att_gt(df: pl.DataFrame, config: dict | str) -> pl.DataFrame:
    """
    Compute ATT(g,t) using did-core on a Polars DataFrame.

    Parameters
    ----------
    df : pl.DataFrame
        Input data with columns matching did-core configuration
    config : dict | str
        JSON config or dict serializable to did-core's DidConfig

    Returns
    -------
    pl.DataFrame
        Columns: group, time, att, se, t_stat, p_value, conf_low, conf_high
    """
    cfg_json = config if isinstance(config, str) else json.dumps(config)
    return _did_att_gt_rust(df, cfg_json)


def get_panel_info(df: pl.DataFrame, config: dict | str) -> pl.DataFrame:
    """
    Return panel diagnostics based on did-core preprocessing.

    Returns columns: panel_type, is_balanced, n_periods
    """
    cfg_json = config if isinstance(config, str) else json.dumps(config)
    return _did_panel_info_rust(df, cfg_json)


def aggregate_effects(
    df: pl.DataFrame,
    config: dict | str,
    kind: str = "simple",
    confidence: float = 0.95,
    uniform_bands: bool = False,
) -> pl.DataFrame:
    """
    Aggregate ATT(g,t) from did-core using the original DataFrame and config.

    Parameters
    ----------
    df : pl.DataFrame
        Input data with columns matching did-core configuration.
    config : dict | str
        JSON config or dict serializable to did-core's DidConfig.
    kind : str
        One of: "simple", "group", "dynamic" (aka "event"), "calendar".
    confidence : float
        Confidence level for bands (e.g., 0.95).
    uniform_bands : bool
        Use uniform bands where supported.

    Returns
    -------
    pl.DataFrame
        Columns: group, time, event_time, att, se, conf_low, conf_high, is_overall
    """
    cfg_json = config if isinstance(config, str) else json.dumps(config)
    return _did_aggregate_rust(df, cfg_json, kind, confidence, uniform_bands)
