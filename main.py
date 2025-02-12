from fastapi import FastAPI
import mysql.connector
import os

app = FastAPI()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

@app.get("/")
def read_root():
    return {"mensaje": "Backend de ventas-ia funcionando"}
