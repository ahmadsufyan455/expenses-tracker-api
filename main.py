from fastapi import FastAPI
from db.database import engine
from db.models import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Hello World"}