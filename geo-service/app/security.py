import jwt

from .config import JWT_ALGORITHM, JWT_SECRET


# Función para decodificar el token
def decode_token(token: str) -> dict:

    # Comprueba la firma y la caducidad. Si algo falla lanza excepción
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
