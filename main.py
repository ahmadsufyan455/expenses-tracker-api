from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from db.database import engine
from db.models import Base
from routers import auth
from core.common_response import SuccessResponse, ErrorResponse

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
    return SuccessResponse(message="Hello World")

app.include_router(auth.router)