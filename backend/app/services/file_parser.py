import pandas as pd
from typing import Dict, Any
from io import BytesIO
from app.services.schema_infer import normalize_columns, validate_schema

def get_schema(file_bytes: bytes,
               filename: str,
               has_headers:bool=True,
               with_id:bool = False,
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

    #Normalize column names
    normalized = normalize_columns(df.columns.tolist())
    df.columns = [col["normalized"] for col in normalized]

    schema = []
    
    #Optionally add an ID column
    if with_id:
        schema.append({"name": "id",
                       "inferred_type": "integer",
                       "nullable": False,
                       "is_primary_key": True,
                       })

    for idx, (col, dtype) in enumerate(zip(df.columns, df.dtypes)):
        schema.append({
            "name": col,
            "original_name": normalized[idx]["original"],
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
        
           
    