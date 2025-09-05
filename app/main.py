from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import engine
from app.models import Base
from app.api.v1.router import api_router
from app.core.exceptions import BaseError
from app.core.responses import SuccessResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BaseError)
async def base_error_handler(_: Request, exc: BaseError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": exc.message
        }
    )


@app.get("/")
def read_root():
    return SuccessResponse(
        message="Welcome to the API",
        data={
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "A simple API for managing personal finances"
        }
    )


app.include_router(api_router)
