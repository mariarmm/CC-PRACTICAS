from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Todavía no hay modelos, así que no se crea ninguna tabla.
    # Se crearán aquí cuando se añadan en models.py
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AgroTrace - Servicio de tratamientos", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}
