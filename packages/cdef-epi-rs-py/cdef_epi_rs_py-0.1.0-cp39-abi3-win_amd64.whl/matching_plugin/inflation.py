"""
Inflation adjustment helpers for Polars DataFrames and LazyFrames.

The main entry point is `adjust_for_inflation`, which scales nominal amounts
to a specified target year using a provided CPI/price index mapping.

Example
-------
>>> import polars as pl
>>> from matching_plugin.inflation import adjust_for_inflation
>>>
>>> df = pl.DataFrame({
...     "year": [2018, 2019, 2020, 2020],
...     "amount": [100.0, 100.0, 100.0, 250.0],
... })
>>> cpi = {2018: 98.1, 2019: 100.0, 2020: 102.3}
>>> out = adjust_for_inflation(df, amount_col="amount", year_col="year", index=cpi, target_year=2020)
>>> out
shape: (4, 3)
┌──────┬────────┬────────────────────┐
│ year ┆ amount ┆ amount_real_2020   │
│ ---  ┆ ---    ┆ ---                │
│ i64  ┆ f64    ┆ f64                │
╞══════╪════════╪════════════════════╡
│ 2018 ┆ 100.0  ┆ 104.283...         │
│ 2019 ┆ 100.0  ┆ 102.3              │
│ 2020 ┆ 100.0  ┆ 100.0              │
│ 2020 ┆ 250.0  ┆ 250.0              │
└──────┴────────┴────────────────────┘
"""

from __future__ import annotations

from typing import Mapping, Optional, Union

import polars as pl

PolarsFrame = Union[pl.DataFrame, pl.LazyFrame]


def _build_index_df(
    year_col: str, index: Mapping[Union[int, str], float]
) -> pl.DataFrame:
    years = [int(y) for y in index.keys()]
    values = [float(v) for v in index.values()]
    return pl.DataFrame({year_col: years, "__cpi__": values}).with_columns(
        [pl.col(year_col).cast(pl.Int64), pl.col("__cpi__").cast(pl.Float64)]
    )


def adjust_for_inflation(
    frame: PolarsFrame,
    *,
    amount_col: str,
    year_col: str,
    index: Mapping[Union[int, str], float],
    target_year: int,
    out_col: Optional[str] = None,
    drop_helper_cols: bool = True,
    strict: bool = True,
) -> PolarsFrame:
    """
    Adjust nominal amounts to a target year using a CPI/price index mapping.

    Parameters
    - frame: pl.DataFrame or pl.LazyFrame to transform.
    - amount_col: Name of the nominal amount column to adjust.
    - year_col: Name of the column with calendar years (int-like).
    - index: Mapping of year -> CPI (or any price index). Must include `target_year`.
    - target_year: Year to which amounts are adjusted.
    - out_col: Optional name for the adjusted column. Defaults to "{amount_col}_real_{target_year}".
    - drop_helper_cols: Drop temporary helper columns (like the joined CPI column). Default True.
    - strict: For eager DataFrames, raise if any year is missing in `index`. For LazyFrames,
      missing years will yield null adjusted values.

    Returns
    - A DataFrame or LazyFrame (matching the input type) with an added column of adjusted amounts.

    Notes
    - Formula: adjusted = amount * (CPI[target_year] / CPI[year]).
    - If `frame` is Lazy, validation of missing years is deferred and nulls will appear if the
      year is not found in the provided `index` mapping.
    """
    if target_year not in {int(k) for k in index.keys()}:
        raise KeyError(f"target_year {target_year} not present in index mapping")
    target_cpi = float(index[int(target_year)])

    cpi_df = _build_index_df(year_col, index)
    out_col = out_col or f"{amount_col}_real_{target_year}"

    is_lazy = isinstance(frame, pl.LazyFrame)
    left = frame
    right = cpi_df.lazy() if is_lazy else cpi_df

    joined: PolarsFrame = left.join(right, on=year_col, how="left")  # type: ignore[arg-type]

    # Compute adjusted amount
    with_adjusted = joined.with_columns(
        (pl.col(amount_col) * (pl.lit(target_cpi) / pl.col("__cpi__"))).alias(out_col)
    )

    if not is_lazy:
        df = with_adjusted  # type: ignore[assignment]
        if strict:
            missing_years = (
                df.filter(pl.col("__cpi__").is_null())
                .select(pl.col(year_col))
                .unique()
                .to_series()
                .to_list()
            )
            if missing_years:
                raise ValueError(
                    "Some years in the DataFrame are missing from the index mapping: "
                    f"{sorted(missing_years)}"
                )
        if drop_helper_cols:
            df = df.drop("__cpi__")
        return df
    else:
        lf = with_adjusted  # type: ignore[assignment]
        if drop_helper_cols:
            lf = lf.drop("__cpi__")
        return lf


__all__ = ["adjust_for_inflation"]
