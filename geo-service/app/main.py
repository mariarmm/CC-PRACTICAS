from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db
from .dependencies import UsuarioToken, get_usuario_actual, requiere_roles
from .roles import Rol


# Funcion que se ejecuta al arrancar la app
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# Crea la app
app = FastAPI(title="AgroTrace - Servicio geográfico", lifespan=lifespan)

# Cuando llegue una peticion GET a /health ejecuta esta funcion
@app.get("/health")
def health():
    return {"status": "ok"}


# Endpoint para registrar una parcela
@app.post(
    "/parcelas",
    response_model=schemas.ParcelaOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_parcela(datos: schemas.ParcelaIn, db: Session = Depends(get_db), usuario: UsuarioToken = Depends(requiere_roles(Rol.ADMIN, Rol.ENCARGADO)),):

    # Crea un objeto Parcela en memoria
    parcela = models.Parcela(
        nombre=datos.nombre,
        descripcion=datos.descripcion,
        propietario_id=usuario.id,  # se obtiene del token
    )
    db.add(parcela)

    db.commit() # Ejecuta el INSERT
    db.refresh(parcela) # Recarga el objeto desde la BD para obtener el id

    return parcela # Devuelve el objeto


# Endpoint para listar las parcelas
@app.get("/parcelas", response_model=list[schemas.ParcelaOut])
def listar_parcelas(db: Session = Depends(get_db),usuario: UsuarioToken = Depends(get_usuario_actual),):

    # Consulta para obtener las parcelas registradas
    consulta = select(models.Parcela).order_by(models.Parcela.id)

    if usuario.rol == Rol.ENCARGADO:

        # El encargado solo puede visualizar sus parcelas
        consulta = consulta.where(models.Parcela.propietario_id == usuario.id)

    elif usuario.rol == Rol.TRABAJADOR:

        # Un trabajador ve las parcelas de su encargado
        consulta = consulta.where(models.Parcela.propietario_id == usuario.encargado_id)
        
    # El admin ve todas las parcelas

    return db.scalars(consulta).all()
