from typing import Any, Optional

__version__: str

def match_scd_cases(py_df: Any, py_vital_df: Optional[Any], config: str) -> Any: ...
def match_scd_cases_with_diagnostics(
    py_df: Any, py_vital_df: Optional[Any], config: str
) -> Any: ...
def format_match_output(py_df: Any) -> Any: ...
def extract_temporal_data_dynamic_year_py(
    py_df: Any,
    identifier_col: str,
    index_date_col: str,
    registry_pattern: str,
    variable_col: str,
    temporal_range: tuple[int, int],
    additional_cols: Optional[list[str]],
    use_cache: bool,
) -> Any: ...
def extract_temporal_data_batched_py(
    py_df: Any,
    batch_size: int,
    identifier_col: str,
    index_date_col: str,
    registry_pattern: str,
    variable_col: str,
    temporal_range: tuple[int, int],
    additional_cols: Optional[list[str]],
    use_cache: bool,
) -> Any: ...
def extract_highest_education_level_py(
    py_df: Any,
    identifier_col: str,
    index_date_col: str,
    uddf_file_path: str,
) -> Any: ...
def extract_highest_education_level_batched_py(
    py_df: Any,
    batch_size: int,
    identifier_col: str,
    index_date_col: str,
    uddf_file_path: str,
) -> Any: ...
def extract_ethnicity_temporal_py(
    py_df: Any,
    identifier_col: str,
    index_date_col: str,
    bef_registry_pattern: str,
    temporal_range: tuple[int, int],
) -> Any: ...
def extract_parent_socio13_py(
    py_df: Any,
    identifier_col: str,
    index_date_col: str,
    akm_registry_pattern: str,
    year_offset: int,
) -> Any: ...
def extract_cohabitation_status_py(
    py_df: Any,
    identifier_col: str,
    index_date_col: str,
    bef_registry_pattern: str,
    year_offset: int,
) -> Any: ...
def extract_parent_income_timeseries_py(
    py_df: Any,
    identifier_col: str,
    index_date_col: str,
    ind_registry_pattern: str,
    income_vars: list[str],
    temporal_range: tuple[int, int],
) -> Any: ...
def did_att_gt_py(py_df: Any, config_json: str) -> Any: ...
def did_panel_info_py(py_df: Any, config_json: str) -> Any: ...
def did_aggregate_py(
    py_df: Any, config_json: str, kind: str, confidence: float, uniform_bands: bool
) -> Any: ...
