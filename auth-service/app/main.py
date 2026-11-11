from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas, security
from .database import Base, engine, get_db
from .roles import Rol
from .dependencies import get_usuario_actual

# Funcion que se ejecuta al arrancar la app
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine) # mira todos los modelos que heredan de Base y crea sus tablas si no existen
    yield


# Crea la app
app = FastAPI(title="AgroTrace - Servicio de autenticacion", lifespan=lifespan)

# Cuando llegue una peticion GET a /health ejecuta esta funcion
@app.get("/health")
def health():
    return {"status": "ok"}



# Endpoint de registro
@app.post(
    "/auth/register",
    response_model=schemas.UsuarioOut,  # Filtra la respuesta, para evitar que se muestre password_hash
    status_code=status.HTTP_201_CREATED,
)
# FastAPI lee el JSON del cuerpo y lo valida. Si los datos no cumplen el formato, no se ejecuta la función
# FastAPI llama a get_db para obtener la sesion y la cierra al terminar
def register(datos: schemas.RegisterIn, db: Session = Depends(get_db)):

    # Crea un objeto Usuario en memoria
    usuario = models.Usuario(
        email=datos.email.lower(),
        nombre=datos.nombre,

        #contraseña se convierte en hash antes de guardarla
        password_hash=security.hash_password(datos.password),

        rol = Rol.ENCARGADO.value,  # el endpoint público siempre crea encargados
    )
    db.add(usuario)
    try:
        db.commit() # Ejecuta el INSERT

    #Si el email ya existe, BD lanza IntegrityError por la restriccion unique
    except IntegrityError: 

        db.rollback() # Deshace la transaccion fallida
        raise HTTPException(status.HTTP_409_CONFLICT, "El email ya está registrado")
    
    db.refresh(usuario) # Recarga el objeto desde la BD para obtener el id

    return usuario # Devuelve el objeto 



#Endpoint de login
@app.post("/auth/login", response_model=schemas.TokenOut)
def login(datos: schemas.LoginIn, db: Session = Depends(get_db)):

    usuario = db.scalar(
        # Consulta para comprobar si el usuario está registrado
        select(models.Usuario).where(models.Usuario.email == datos.email.lower())
    )

    # Si no existe o la contraseña no es correcta
    if usuario is None or not security.verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales incorrectas")

    # Devuelve el token con el id y el email
    return schemas.TokenOut(access_token=security.create_token(usuario.id, usuario.email, usuario.rol, usuario.encargado_id))


# Endpoint que devuelve los datos del dueño del token
@app.get("/auth/me", response_model=schemas.UsuarioOut)
def me(usuario: models.Usuario = Depends(get_usuario_actual)):
    return usuario