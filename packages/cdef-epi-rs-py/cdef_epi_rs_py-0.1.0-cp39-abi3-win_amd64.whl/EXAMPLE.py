from pathlib import Path

import polars as pl

from matching_plugin import _internal

relations_df = pl.read_parquet("data/relations.parquet")
vital_df = pl.read_parquet("data/vital.parquet")
scd_df = pl.read_parquet("data/scd.parquet")

match_input_df = relations_df.join(scd_df, on="PNR")

ind_registry_pattern = Path("data/ind_registry.parquet")
bef_registry_pattern = Path("data/bef_registry.parquet")
akm_registry_pattern = Path("data/akm_registry.parquet")
uddf_file_path = Path("data/uddf.parquet")

# WorkflowConfig for matching
matching_config = {
    "birth_date_window_days": 30,
    "parent_birth_date_window_days": 365,
    "match_parent_birth_dates": True,
    "match_mother_birth_date_only": False,
    "require_both_parents": False,
    "match_parity": True,
    "match_birth_type": True,
    "matching_ratio": 4,
}
workflow_config = {
    "matching": matching_config,
    "algorithm": "partitioned_parallel",
}

# ParentIncomeStudyConfig
parent_income_study_config = {
    "matching": workflow_config,
    "ind_registry_pattern": ind_registry_pattern,
    "income_vars": ["PERINDKIALT_13"],
    "outcome_var": "PERINDKIALT_13",
    "bef_registry_pattern": bef_registry_pattern,
    "akm_registry_pattern": akm_registry_pattern,
    "uddf_file_path": uddf_file_path,
    "income_temporal_range": [-5, 15],
    "did_controls": ["gender", "socio13_cat", "education"],
    "gender_values": ["M", "F"],
    "socio13_order": [
        "Working_SelfEmployed",
        "Working_ManagerHighLevel",
        "Student",
        "Unemployed",
    ],
    "confidence": 0.95,
    "uniform_bands": False,
    "plot_output_dir": "plots/parent_income",
    "plot_format": "png",
}


result = _internal.run_parent_income_study_py(
    match_input_df=match_input_df,
    relations_df=relations_df,
    config_json=parent_income_study_config,
    vital_df=vital_df,
)
