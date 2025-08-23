from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.base_response import ErrorResponse, SuccessResponse
from db.database import engine
from db.models import Base
from routers import auth

app = FastAPI()

Base.metadata.create_all(bind=engine)


# Exception handler for custom ErrorResponse exceptions
# This function catches all ErrorResponse exceptions thrown throughout the application
# and converts them to proper HTTP responses with consistent error format
@app.exception_handler(ErrorResponse)
async def error_handler(_: Request, exc: ErrorResponse):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message, "error": exc.error})


@app.get("/")
def read_root():
    return SuccessResponse(
        message="Welcome to the API",
        data={
            "name": "Finance Tracker API",
            "version": "1.0.0",
            "description": "A simple API for managing personal finances",
            "author": "Ahmad Sufyan",
            "email": "ahmadsuufyan514@gmail.com",
            "github": "https://github.com/ahmadsufyan455"
        }
    )


app.include_router(auth.router)
