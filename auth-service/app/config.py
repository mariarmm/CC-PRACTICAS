import os

DATABASE_URL = os.environ["DATABASE_URL"] # os.environ[...] lanza un error si la variable no existe.
JWT_SECRET = os.environ["JWT_SECRET"]

JWT_ALGORITHM = "HS256" # Firma simetrica

# Si no se indica, el token expira en 1 hora
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
