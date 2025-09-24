from fastapi import FastAPI, UploadFile, File, Query, HTTPException, status #type: ignore
from fastapi.responses import JSONResponse, PlainTextResponse #type: ignore
from app.services.file_parser import get_schema
from app.services.sql_generator import generate_sql
from app.services.orm_generator import generate_orm
from typing import List
from pydantic import BaseModel #type: ignore
import uuid
from io import BytesIO

from app.core.config import (TITLE, VERSION,)

from app.services.link_suggester import (
    suggest_links_by_name,
    boost_links_by_type,
    validate_links_by_overlap,
)

from app.services.schema_infer import (
    ensure_primary_key,
    validate_schema,
)
#Literals
SESSIONS = {}

#Model Request Bodies
class LinkModel(BaseModel):
    session_id:str
    from_field:str
    to_field:str
    
#Endpoints
app = FastAPI(title=TITLE, version=VERSION)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Query(None),
    has_headers: bool = Query(True),
    with_id: bool = Query(False),
    with_row_count: bool = Query(False),
    with_preview: bool = Query(False),
    deep_check: bool = Query(False, description="Enable statistical validation for link suggestions?")
):
    """
    Upload a file (CSV/Excel/JSON), infer schema, normalize, and
    add to a session. Returns schema + suggested links.
    """
    try:
        file_bytes = await file.read()
        schema_info = get_schema(
            file_bytes,
            file.filename,
            has_headers=has_headers,
            with_id=with_id,
            with_row_count=with_row_count,
            with_preview=with_preview
        )
        
        schema,pk_warnings = ensure_primary_key(schema_info["columns"])
        warn = validate_schema(schema)
        schema_info["columns"] = schema
        schema_info["validation_warnings"] = pk_warnings + warn

        if not session_id:
            session_id = str(uuid.uuid4())
            SESSIONS[session_id] = {"tables": [], "links": [], "suggested_links": [], "dfs": {}}

        # store schema + dataframe
        table_name = file.filename.split(".")[0]
        schema_info["name"] = table_name
        SESSIONS[session_id]["tables"].append(schema_info)

        import pandas as pd
        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(file_bytes), header=0 if has_headers else None)
        elif file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(BytesIO(file_bytes), header=0 if has_headers else None)
        elif file.filename.endswith(".json"):
            df = pd.read_json(BytesIO(file_bytes))
        else:
            df = None
        if df is not None and not has_headers:
            df.columns = [f"col_{i+1}" for i in range(len(df.columns))]
        if df is not None:
            SESSIONS[session_id]["dfs"][table_name] = df

        # run suggestion pipeline
        existing_tables = [t for t in SESSIONS[session_id]["tables"] if t["name"] != table_name]
        suggestions = suggest_links_by_name(schema_info, existing_tables)
        suggestions = boost_links_by_type(suggestions, SESSIONS[session_id]["tables"])

        if deep_check and df is not None:
            suggestions = validate_links_by_overlap(
                schema_info, 
                SESSIONS[session_id]["dfs"], 
                suggestions
            )

        SESSIONS[session_id]["suggested_links"].extend(suggestions)

        return JSONResponse(
            content={
                "session_id": session_id,
                "table_added": table_name,
                "schema": schema_info,
                "suggested_links": suggestions
            },
            status_code=status.HTTP_201_CREATED if len(SESSIONS[session_id]["tables"]) == 1 else status.HTTP_200_OK
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accept_link")
def accept_link(link: LinkModel):
    session = SESSIONS.get(link.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # find if link exists in suggested_links
    match = None
    for s in session["suggested_links"]:
        if s["from"] == link.from_field and s["to"] == link.to_field:
            match = s
            break

    if not match:
        raise HTTPException(status_code=404, detail="Suggested link not found")

    # move it into confirmed links
    session["links"].append(match)
    session["suggested_links"].remove(match)

    return JSONResponse(
        content={
            "session_id": link.session_id,
            "accepted_link": match,
            "links": session["links"],
            "remaining_suggestions": session["suggested_links"]
        },
        status_code=status.HTTP_201_CREATED
    )


@app.post("/reject_link")
def reject_link(link: LinkModel):
    session = SESSIONS.get(link.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # find if link exists in suggested_links
    match = None
    for s in session["suggested_links"]:
        if s["from"] == link.from_field and s["to"] == link.to_field:
            match = s
            break

    if not match:
        raise HTTPException(status_code=404, detail="Suggested link not found")

    # remove from suggestions
    session["suggested_links"].remove(match)

    return JSONResponse(
        content={
            "session_id": link.session_id,
            "rejected_link": match,
            "remaining_suggestions": session["suggested_links"]
        },
        status_code=status.HTTP_200_OK
    )


@app.get("/session/{session_id}")
def get_session(session_id: str):
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
    
@app.post("/link")
def add_link(link: LinkModel):
    session = SESSIONS.get(link.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session["links"].append({"from": link.from_field,"to": link.to_field})
    return JSONResponse(
        content={
            "session_id": link.session_id, "links": session["links"]
        },
        status_code=status.HTTP_201_CREATED
        )

@app.get("/generate/{session_id}")
def generate_artifacts(
    session_id: str,
    format: str = Query("sql", enum=["sql", "orm"]),
    as_json: bool = Query(False, description="Return result as JSON instead of plain text?")
):
    ##example: /generate/1234?format=sql&as_json=true

    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if format == "sql":
        result = generate_sql(session)
    else:
        result = generate_orm(session)

    if as_json:
        # Return as {"sql": [...]} or {"orm": [...]}
        return JSONResponse({format: result})
    else:
        # Return as plain text, line-joined
        return PlainTextResponse("\n".join(result))


@app.get("/download/{file_id}")
async def download_output(file_id: str):
    #TODO: return processed schema file
    return {"file_id": file_id, "status": "Download link generated"}


##Session Management
@app.delete("/reset_session/{session_id}")
def reset_session(session_id:str):
    if session_id in SESSIONS:
        temp_id = session_id
        del SESSIONS[session_id]
        return JSONResponse(
            content = {"status": f"Session {temp_id} reset successfully"},
            status_code = status.HTTP_200_OK
        )
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/reset_all_sessions")
def reset_all_sessions():
    if not SESSIONS:
        raise HTTPException(status_code=404, detail="No active sessions to reset")
    SESSIONS.clear()
    return JSONResponse(
        content={"status": "All sessions reset successfully"},
        status_code=status.HTTP_200_OK
    )

@app.get("/list_sessions")
async def list_sessions():

    if not SESSIONS:
        return JSONResponse(content={"sessions": []}, status_code=status.HTTP_200_OK)  # No active sessions

    return JSONResponse(
        content={
            "sessions": [
                {
                    "session_id": sid,
                    "table_count": len(data["tables"]),
                    "link_count": len(data["links"]),
                    "suggested_link_count": len(data["suggested_links"])
                } for sid, data in SESSIONS.items()
            ]
        },
        status_code=status.HTTP_200_OK
    )