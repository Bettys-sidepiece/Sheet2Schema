from app.services.type_mapper import map_sql_type

def generate_sql(session: dict) -> list[str]:
    stmts = []
    for table in session["tables"]:
        cols = []
        for col in table["columns"]:
            col_def = f"{col['name']} {map_sql_type(col['inferred_type'])}"
            if not col["nullable"]:
                col_def += " NOT NULL"
            if col.get("is_primary_key"):
                col_def += " PRIMARY KEY"
            cols.append(col_def)

        # add foreign keys
        for link in session["links"]:
            if link["from"].startswith(table["name"] + "."):
                _, col_name = link["from"].split(".")
                ref_table, ref_col = link["to"].split(".")
                cols.append(f"FOREIGN KEY ({col_name}) REFERENCES {ref_table}({ref_col})")

        # turn into a CREATE TABLE statement (line by line)
        stmt_lines = [f"CREATE TABLE {table['name']} ("]
        stmt_lines += [f"  {c}," for c in cols[:-1]]  # all but last with comma
        stmt_lines.append(f"  {cols[-1]}")            # last without comma
        stmt_lines.append(");")
        stmts += stmt_lines + [""]  # add blank line after each table

    return stmts
