from fastapi import FastAPI # type: ignore
from  fastapi.middleware.cors import CORSMiddleware # type: ignore
from app.api import routes as api_routes
from app.core import routes as core_routes
from app.core.config import (TITLE, VERSION,)

app = FastAPI(title=TITLE, version=VERSION)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_routes.router, prefix="/api", tags=["api"])
app.include_router(core_routes.router, prefix="/core", tags=["core"])
