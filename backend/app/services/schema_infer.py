import re
from typing import List, Dict,Tuple

SQL_RESERVED = {
    "select", "from", "where", "insert", "update", "delete",
    "create", "drop", "table", "index", "join", "order", "group"
}

def normalize_columns(columns: List[str]) -> List[Dict[str, str]]:
    """
    Normalize and deduplicate column names.
    Reserved keywords are auto-fixed by appending '_col'.
    """
    seen = {}
    normalized = []

    for col in columns:
        original = col

        # snake_case + lowercase
        name = re.sub(r'\W+', '_', col.strip().lower())
        if not name:
            name = "col"

        # deduplicate
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0

        # auto-fix reserved keyword
        fixed_name = f"{name}_col" if name in SQL_RESERVED else name

        normalized.append({
            "original_name": original,
            "normalized_name": fixed_name,
            "was_reserved": name in SQL_RESERVED
        })

    return normalized


def validate_schema(schema: List[Dict]) -> List[str]:
    """
    Returns warnings, not blockers.
    After auto-fix, no schema should be invalid.
    """
    warnings = []
    names = [col["original_name"] for col in schema]

    # Duplicates shouldn't exist after normalize, but double-check
    if len(names) != len(set(names)):
        warnings.append("Duplicate column names were auto-renamed")

    for col in schema:
        if col.get("was_reserved", False):
            warnings.append(
                f"Column '{col['original_name']}' renamed to '{col['name']}' (reserved keyword)"
            )

    if not any(col.get("is_primary_key") for col in schema):
        warnings.append("No primary key defined in schema")

    return warnings

def ensure_primary_key(schema: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """
    Ensure schema has a primary key.
    If none exists, auto-add 'id' as surrogate PK.
    """
    warnings = []
    has_pk = any(col.get("is_primary_key") for col in schema)

    if not has_pk:
        schema.insert(0, {
            "name": "id",
            "original_name": None,
            "inferred_type": "int64",
            "nullable": False,
            "is_primary_key": True,
            "was_reserved": False
        })
        warnings.append("Auto-added 'id' column as primary key")

    return schema, warnings
