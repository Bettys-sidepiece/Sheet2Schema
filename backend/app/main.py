from fastapi import FastAPI # type: ignore
from app.api import routes as api_routes
from app.core import routes as core_routes
from app.core.config import (TITLE, VERSION,)

app = FastAPI(title=TITLE, version=VERSION)

# Include routers
app.include_router(api_routes.app, prefix="/api", tags=["api"])
app.include_router(core_routes.router, tags=["core"])
