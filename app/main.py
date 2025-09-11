from fastapi import FastAPI

app = FastAPI(title="Sistema de Inventario API")

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API del Sistema de Inventario"}
