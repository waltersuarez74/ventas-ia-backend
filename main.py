from fastapi import FastAPI
import mysql.connector
import os

app = FastAPI()

DB_CONFIG = {
    "host": os.getenv("ventas-ia-mysql.mysql.database.azure.com"),
    "user": os.getenv("wsuarez"),
    "password": os.getenv("Afsmnz78"),
    "database": os.getenv("db_ventas")
}

@app.get("/")
def read_root():
    return {"mensaje": "Backend de ventas-ia funcionando"}
