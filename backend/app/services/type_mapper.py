# Map SQL data types to their corresponding SQLAlchemy types

def map_sql_type(dtype: str) -> str:
    if "int" in dtype:
        return "INTEGER" #Use INTEGER for integer types
    if "float" in dtype or "double" in dtype:
        return "FLOAT"# Use FLOAT for floating point types
    if "bool" in dtype:
        return "BOOLEAN"# Use BOOLEAN for boolean types
    if "date" in dtype or "time" in dtype or "datetime" in dtype:
        return "TIMESTAMP" # Use TIMESTAMP for date/time types
    return "TEXT" # Default to TEXT for other types

def map_to_orm(dtype: str) -> str:
    if "int" in dtype:
        return "Integer"
    if "float" in dtype or "double" in dtype:
        return "Float"
    if "bool" in dtype:
        return "Boolean"
    if "date" in dtype or "time" in dtype or "datetime" in dtype:
        return "DateTime"
    return "String"