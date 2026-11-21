import os

# Variables de entorno. Config.py las lee al importarse, si no existen falla
os.environ["DATABASE_URL"] = "sqlite://"    # BD en memoria
os.environ["JWT_SECRET"] = "secreto-de-tests"

#noqa se utiliza para que ruff no se queje de que las importaciones no estan arriba
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():

    # drop.all borra las tablas antes de cada test
    Base.metadata.drop_all(bind=engine)

    # ejecuta el lifespan de main.py que crea las tablas vacias
    with TestClient(app) as c:
        yield c     # Entrega el cliente al test