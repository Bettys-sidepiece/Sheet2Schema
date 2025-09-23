from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="Sheet2Schema API", version="0.0.1")

@app.get("/")

def root():
    return {"message": "Sheet2Schema API"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    #TODO: Process the uploaded file save file temporarily and pass to parser
    return {"filename": file.filename
            , "content_type": file.content_type
            , "size": len(await file.read())
            , "status": "File received successfully"}

@app.get("/preview/{file_id}")
async def preview_output(file_id: str):
    #TODO: return processed schema JSON
    return {"file_id": file_id, "schema": "Sample schema preview"}

@app.get("/download/{file_id}")
async def download_output(file_id: str):
    #TODO: return processed schema file
    return {"file_id": file_id, "status": "Download link generated"}

@app.get("/credits")
async def get_credits():
    return {"credits": "Developed by Kuzipa Mumba"}