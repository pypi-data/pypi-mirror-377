import sqlite3
import pandas as pd
from storyteller.mintilo_ai_app.mapping_sheet import MAPPING_CHILD, MAPPING_HOUSEHOLD, MAPPING_MOTHER


def apply_dq_rules(df, mapping):
    """Replace missing codes with <NA> and enforce pandas nullable types."""
    for col, rule in mapping.items():
        if col in df.columns:
            missing_vals = rule.get("missing", None)
            if missing_vals:
                df[col] = df[col].apply(lambda x: pd.NA if x in missing_vals else x)

            # Enforce pandas nullable types
            if rule["dtype"] == int:
                df[col] = df[col].astype("Int64")
            elif rule["dtype"] == float:
                df[col] = df[col].astype("Float64")
            elif rule["dtype"] == str:
                df[col] = df[col].astype("string")
    return df


def apply_special_recoding(df, mapping):
    """Apply custom recoding rules from mapping (e.g., 996 -> 0 for water source time)."""
    for col, rule in mapping.items():
        if col in df.columns and "special_recode" in rule:
            df[col] = df[col].replace(rule["special_recode"])
    return df


def apply_recoding(df, recode_table, conn, mapping):
    """Apply recoding from _recode tables for categorical variables."""
    col_map = {v["name"]: k for k, v in mapping.items() if v["dtype"] == str}
    if not col_map:
        return df

    placeholders = ', '.join(['?'] * len(col_map))
    recode_df = pd.read_sql(
        f"SELECT Name, Value, ValueDesc FROM {recode_table} WHERE Name IN ({placeholders})",
        conn,
        params=list(col_map.keys())
    )

    recode_map = {}
    for name in recode_df["Name"].unique():
        subset = recode_df[recode_df["Name"] == name]
        recode_map[name] = dict(zip(subset["Value"], subset["ValueDesc"]))

    for orig_name, col_name in col_map.items():
        if col_name in df.columns and orig_name in recode_map:
            normalized_map = {}
            if pd.api.types.is_string_dtype(df[col_name]):
                # If column is string dtype, map using string keys
                normalized_map = {str(k): v for k, v in recode_map[orig_name].items()}
            else:
                # Default: try to use integer keys
                for k, v in recode_map[orig_name].items():
                    try:
                        normalized_map[int(k)] = v
                    except ValueError:
                        normalized_map[k] = v

            df[col_name] = df[col_name].map(normalized_map).fillna(df[col_name])

    return df


def add_polygamy_flags(ir_df):
    """Add is_polygamous_mother and prepare for household-level aggregation."""
    if "number_of_other_wives" in ir_df.columns:
        ir_df["is_polygamous_mother"] = ir_df["number_of_other_wives"].apply(
            lambda x: 1 if pd.notna(x) and x > 0 else 0
        ).astype("Int64")
    else:
        ir_df["is_polygamous_mother"] = pd.Series([pd.NA] * len(ir_df), dtype="Int64")
    return ir_df


def check_duplicates(df, keys, table_name):
    """Warn if duplicates exist based on keys."""
    if not df.empty and df.duplicated(subset=keys).any():
        print(f"WARNING: Duplicate records found in {table_name} for keys {keys}. Review before modeling.")


def build_dataset(db_path):
    conn = sqlite3.connect(db_path)
    queries = {}

    # CHILD (KR_main) ---------------------------------------------------------------------------
    child_vars = [v["name"] for v in MAPPING_CHILD.values()]
    kr_query = f"SELECT {', '.join(child_vars)} FROM KR_main"
    queries["child"] = kr_query
    kr_df = pd.read_sql(kr_query, conn)
    kr_df.rename(columns={v["name"]: k for k, v in MAPPING_CHILD.items()}, inplace=True)
    kr_df = apply_dq_rules(kr_df, MAPPING_CHILD)
    kr_df = apply_special_recoding(kr_df, MAPPING_CHILD)
    kr_df = apply_recoding(kr_df, "KR_recode", conn, MAPPING_CHILD)

    # HOUSEHOLD (HR_main) ----------------------------------------------------------------------
    hh_vars = [v["name"] for v in MAPPING_HOUSEHOLD.values()]
    hr_query = f"SELECT {', '.join(hh_vars)} FROM HR_main"
    queries["household"] = hr_query
    try:
        hr_df = pd.read_sql(hr_query, conn)
        hr_df.rename(columns={v["name"]: k for k, v in MAPPING_HOUSEHOLD.items()}, inplace=True)
        hr_df = apply_dq_rules(hr_df, MAPPING_HOUSEHOLD)
        hr_df = apply_special_recoding(hr_df, MAPPING_HOUSEHOLD)
        hr_df = apply_recoding(hr_df, "HR_recode", conn, MAPPING_HOUSEHOLD)

        check_duplicates(hr_df, ["cluster_number", "household_number"], "HR_main")
    except Exception:
        hr_df = pd.DataFrame()

    # MOTHER (IR_main) -------------------------------------------------------------------------
    mother_vars = [v["name"] for v in MAPPING_MOTHER.values()]
    ir_query = f"SELECT {', '.join(mother_vars)} FROM IR_main"
    queries["mother"] = ir_query
    try:
        ir_df = pd.read_sql(ir_query, conn)
        ir_df.rename(columns={v["name"]: k for k, v in MAPPING_MOTHER.items()}, inplace=True)
        ir_df = apply_dq_rules(ir_df, MAPPING_MOTHER)
        ir_df = apply_special_recoding(ir_df, MAPPING_MOTHER)
        ir_df = apply_recoding(ir_df, "IR_recode", conn, MAPPING_MOTHER)
        ir_df = add_polygamy_flags(ir_df)

        check_duplicates(ir_df,
                         ["cluster_number_mother", "household_number_mother", "respondent_line_number_mother"],
                         "IR_main")
    except Exception:
        ir_df = pd.DataFrame()

    # MERGE ------------------------------------------------------------------------------------
    merged = kr_df

    if not hr_df.empty:
        merged = merged.merge(
            hr_df,
            left_on=["cluster_number_child", "household_number_child"],
            right_on=["cluster_number", "household_number"],
            how="left"
        )

    if not ir_df.empty:
        merged = merged.merge(
            ir_df,
            left_on=[
                "cluster_number_child",
                "household_number_child",
                "respondent_line_number_child"
            ],
            right_on=[
                "cluster_number_mother",
                "household_number_mother",
                "respondent_line_number_mother"
            ],
            how="left"
        )

    conn.close()

    return merged, queries
