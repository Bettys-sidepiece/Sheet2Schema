from fastapi import APIRouter # type: ignore

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Sheet2Schema API"}

@router.get("/credits")
def get_credits():
    return {
        "Developer": "Kuzipa Mumba",
        "Version": "0.2.0",
        "Repository": "https://github.com/Bettys-sidepiece/Sheet2Schema",
        "License": "GNU GPL v3.0",
        "Website": "https://sheet2schema.com",
        "Year": "2025"
    }
