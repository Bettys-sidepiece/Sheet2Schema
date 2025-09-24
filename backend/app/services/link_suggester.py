from typing import List, Dict
import random

# Naming heuristics
def suggest_links_by_name(new_table: dict, existing_tables: list) -> List[Dict]:
    """Suggest links between columns of a new table and existing tables based on naming conventions.

    Args:
        new_table (dict): schema of the newly added table
        existing_tables (list): list of existing tables

    Returns:
        List[Dict]: list of link suggestions
    """
    suggestions = []
    for col in new_table["columns"]:
        col_name = col["name"].lower()
        if col_name.endswith("_id") or col_name == "id":
            for t in existing_tables:
                pk_candidates = [c for c in t["columns"] if c.get("is_primary_key")]
                for pk in pk_candidates:
                    if (col_name == f"{t['name']}_id") or (col_name.rstrip("_id") == t["name"].rstrip("s")):
                        suggestions.append({
                            "from": f"{new_table['name']}.{col['name']}",
                            "to": f"{t['name']}.{pk['name']}",
                            "confidence": 0.5
                        })
    return suggestions

def boost_links_by_type(suggestions: list, tables: list) -> list:
    """Boost link suggestions based on column type matching.

    Args:
        suggestions (list): list of link suggestions
        tables (list): list of existing tables

    Returns:
        list: boosted link suggestions
    """
    boosted = []
    for s in suggestions:
        from_table, from_col = s["from"].split(".")
        to_table, to_col = s["to"].split(".")
        from_dtype = next(c["inferred_type"] for t in tables if t["name"] == from_table for c in t["columns"] if c["name"] == from_col)
        to_dtype = next(c["inferred_type"] for t in tables if t["name"] == to_table for c in t["columns"] if c["name"] == to_col)

        if from_dtype == to_dtype:
            s["confidence"] += 0.2
        boosted.append(s)
    return boosted

def validate_links_by_overlap(new_table_schema, dfs: dict, suggestions: list, sample_size=200) -> list:
    """Validate link suggestions by checking for value overlap.

    Args:
        new_table_schema (_type_): schema of the newly added table
        dfs (dict): stored dataframes by table name
        suggestions (list): list of link suggestions
        sample_size (int, optional): number of samples to use for validation. Defaults to 200.

    Returns:
        list: validated link suggestions
    """
    validated = []
    new_table = new_table_schema["name"]
    df_from = dfs[new_table]

    for s in suggestions:
        from_table, from_col = s["from"].split(".")
        to_table, to_col = s["to"].split(".")

        if from_table != new_table:
            continue

        if from_col not in df_from.columns or to_col not in dfs[to_table].columns:
            validated.append(s)
            continue

        sample_vals = df_from[from_col].dropna().sample(min(sample_size, len(df_from))).unique()
        target_vals = set(dfs[to_table][to_col].dropna().unique())

        if len(sample_vals) > 0:
            match_rate = sum(val in target_vals for val in sample_vals) / len(sample_vals)
            if match_rate > 0.7:
                s["confidence"] += 0.2
        validated.append(s)

    return validated