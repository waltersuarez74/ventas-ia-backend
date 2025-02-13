from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import openai
from typing import List, Dict
import uvicorn

# Configuración de la API de Azure OpenAI
AZURE_OPENAI_KEY = "9kUCQ1ItOwvz5kwf5eSCuG26O9pZGxGuNAVak6jY8MmzRSGv8c4cJQQJ99BBACR0EKYXJ3w3AAABACOGrRQv"
AZURE_ENDPOINT = "https://ventas-ia-openia.openai.azure.com/"
DEPLOYMENT_ID = "9kUCQ1ItOwvz5kwf5eSCuG26O9pZGxGuNAVak6jY8MmzRSGv8c4cJQQJ99BBACR0EKYXJ3w3AAABACOGrRQv"

openai.api_type = "azure"
openai.api_base = AZURE_ENDPOINT
openai.api_version = "2024-08-01-preview"
openai.api_key = AZURE_OPENAI_KEY

# Conexión a MySQL
def connect_db():
    return mysql.connector.connect(
        host="ventas-ia-mysql.mysql.database.azure.com",
        user="wsuarez",
        password="Afsmnz78",
        database="ventas_db"
    )

# Modelo de entrada para las solicitudes de consulta
class QueryRequest(BaseModel):
    customer_id: str
    query: str

# Inicializar FastAPI
app = FastAPI()

# Obtener información del cliente desde MySQL
@app.get("/customer/{customer_id}")
def get_customer_data(customer_id: str):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT producto, SUM(cantidad) AS total_comprado, SUM(monto) AS total_monto
        FROM ventas
        WHERE cliente_id = %s
        GROUP BY producto
    """, (customer_id,))
    sales_data = cursor.fetchall()
    
    cursor.execute("""
        SELECT SUM(monto_pagado) AS total_pagado, SUM(monto_credito) AS total_credito, SUM(monto_credito) - SUM(monto_pagado) AS saldo_pendiente
        FROM cobranzas
        WHERE cliente_id = %s
    """, (customer_id,))
    payment_data = cursor.fetchone() or {"total_pagado": 0, "total_credito": 0, "saldo_pendiente": 0}
    
    cursor.execute("""
        SELECT monto_pagado, dias_atraso, fecha_pago
        FROM cobranzas
        WHERE cliente_id = %s
    """, (customer_id,))
    payment_history = cursor.fetchall()
    
    conn.close()
    return {"ventas": sales_data, "cobranzas": payment_data, "historial_pagos": payment_history}

# Generar respuesta con OpenAI
@app.post("/generate-response")
def generate_response(data: QueryRequest):
    customer_data = get_customer_data(data.customer_id)
    
    context = f"""
    Cliente ID: {data.customer_id}
    Ventas: {customer_data['ventas']}
    Cobranzas: {customer_data['cobranzas']}
    Historial de Pagos: {customer_data['historial_pagos']}
    """
    
    prompt_final = f"""Con base en la siguiente información, responde la consulta del usuario:
    {context}
    
    Pregunta del usuario: {data.query}
    """
    
    response = openai.ChatCompletion.create(
        engine=DEPLOYMENT_ID,
        messages=[
            {"role": "system", "content": "Eres un asistente que analiza ventas y pagos de clientes."},
            {"role": "user", "content": prompt_final}
        ]
    )
    
    return {"respuesta": response["choices"][0]["message"]["content"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
