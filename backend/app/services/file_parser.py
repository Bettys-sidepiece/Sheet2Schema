import pandas as pd
import numpy as np
from typing import Dict, Any
from io import BytesIO
from app.services.schema_infer import normalize_columns, validate_schema

SQL_RESERVED = {
    "select", "from", "where", "insert", "update", "delete",
    "create", "drop", "table", "index", "join", "order", "group"
}

def to_builtin(obj: Any) -> Any: # Convert numpy types to native Python types for JSON serialization
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, dict):
        return {k: to_builtin(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_builtin(v) for v in obj]
    return obj

def get_schema(file_bytes: bytes,
               filename: str,
               has_headers:bool=True,
               with_row_count:bool = True,
               with_preview:bool = False
            ) -> Dict[str, Any]:
    """Extract schema from uploaded file.

    Args:
        file_bytes (bytes): The content of the uploaded file.
        filename (str): The name of the uploaded file.
        has_headers (bool, optional): Whether the file has headers. Defaults to True.

    Returns:
        Dict[str, Any]: The extracted schema.
    """
    header = 0 if has_headers else None
    
    if filename.endswith(".csv"):
        df = pd.read_csv(BytesIO(file_bytes),nrows=None ,header=header)
    elif filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(BytesIO(file_bytes),nrows=None,header=header)
    elif filename.endswith(".json"):
        df = pd.read_json(BytesIO(file_bytes))
    else:
        raise ValueError({"error": "Unsupported file type"})
    
    # Assign default column names if headers are absent
    if not has_headers:
        df.columns = [f"col_{i+1}" for i in range(len(df.columns))]

    cols = []
    used = set()

    for i, col in enumerate(df.columns):
        original = str(cols).strip()
        normalized = original.lower().replace(" ", "_")

        # Handle reserved words or duplicates
        was_reserved = False
        if normalized in SQL_RESERVED or normalized in used:
            was_reserved = True
            normalized = f"{normalized}_{i}"

        used.add(normalized)

        cols.append({
            "original_name": original,
            "normalized_name": normalized,
            "was_reserved": was_reserved,
        })

    # Only rename dataframe columns if *any* column was reserved/changed
    if any(c["was_reserved"] or c["normalized_name"] != c["original_name"] for c in cols):
        df.columns = [c["normalized_name"] for c in cols] 

    schema = []

    for idx, (col, dtype) in enumerate(zip(df.columns, df.dtypes)):
        schema.append({
            "name": col,
            "original_name": cols[idx]["original_name"],
            "inferred_type": str(dtype),
            "nullable": df[col].isnull().any(),
            "is_primary_key": (idx == 0)  # first column as PK if no ID added
        })
        
        errors = validate_schema(schema)

    return {"columns": schema, 
            "row_preview": df.head(5).to_dict(orient="records") if with_preview else None,
            "row_count": int(len(df)) if with_row_count else None,
            "validation_errors": errors
            }
        
           
    