from app.services.type_mapper import map_to_orm as map_orm_type

def generate_orm(session: dict) -> list[str]:
    lines = [
        "from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey",
        "from sqlalchemy.orm import relationship",
        "from sqlalchemy.ext.declarative import declarative_base",
        "",
        "Base = declarative_base()",
        ""
    ]

    for table in session["tables"]:
        class_name = table["name"].capitalize()
        lines.append(f"class {class_name}(Base):")
        lines.append(f"    __tablename__ = '{table['name']}'")

        for col in table["columns"]:
            sa_type = map_orm_type(col["inferred_type"])
            col_def = f"Column({sa_type}"
            if col.get("is_primary_key"):
                col_def += ", primary_key=True"
            if not col["nullable"]:
                col_def += ", nullable=False"
            col_def += ")"
            lines.append(f"    {col['name']} = {col_def}")

        # Add relationships
        for link in session["links"]:
            if link["from"].startswith(table["name"] + "."):
                _, local_col = link["from"].split(".")
                ref_table, _ = link["to"].split(".")
                ref_class = ref_table.capitalize()
                lines.append(f"    {ref_table} = relationship('{ref_class}')")

        lines.append("")  # spacing between classes

    return lines
