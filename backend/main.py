from fastapi import FastAPI
from redis_client import get_redis
from api import emitenti, bilansi, odgovor

app = FastAPI(
    title="Emitenti AI Asistent",
    description="API aplikacija za analizu finansijskih izvještaja sa Banjalučke berze koristeći AI.",
    version="1.0.0",
    contact={
        "name": "FPE tim",
        "url": "https://www.fpe.ues.rs.ba",
        "email": "nic@fpe.ues.rs.ba",
    })

# Učitavanje ruta
app.include_router(emitenti.router, prefix="/api")
app.include_router(bilansi.router, prefix="/api")
app.include_router(odgovor.router, prefix="/api")

@app.get("/api/ping")
def ping():
    return {"message": "Backend radi 🎉"}
