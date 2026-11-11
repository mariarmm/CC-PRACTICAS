from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import DATABASE_URL

# Elegir el motor. engine gestiona un pool (conjunto de conexiones abiertas con la bd para reutilizarlas)
if DATABASE_URL.startswith("sqlite"):
     
    # Para tests: un BD SQLite en memoria compartida entre conexiones, desaparece al cerrar la conexion
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # permite usarla desde los hilos del servidor de pruebas
        poolclass=StaticPool,   #fuerza a reutilizar siempre la misma conexion
    )

else:

    # Utiliza PostgreSQL. pool_pre_ping comprueba que la conexion sigue viva antes de usarla.
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)


# Fabrica de sesiones (SesssionLocal). Una sesion es una conversacion con la BD. 
# autoflush=False: no envia cambios automaticamente
SessionLocal = sessionmaker(bind=engine, autoflush=False)


# Padre de todos los modelos
class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:    #se ejecuta al terminar
        db.close()
