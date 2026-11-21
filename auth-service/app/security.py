from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET

# Función para aplicar hash a una contraseña
def hash_password(password: str) -> str:

    # Utiliza una sal aleatoria y la guarda dentro del hash
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# Función para comprobar si la contraseña introducida es correcta
def verify_password(password: str, password_hash: str) -> bool:

    #checkpw saca la sal del hash guardado y calcula el hash de la contraseña introducida con esa sal, para comparar las dos contraseñas
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# Función para crear el token
def create_token(user_id: int, email: str, rol: str, encargado_id: int | None = None) -> str:
    ahora = datetime.now(timezone.utc)

    # datos del token
    payload = {
        "sub": str(user_id), # A quién pertenece
        "email": email,
        "rol" : rol,         
        "iat": ahora,        # Cuándo se emitió
        "exp": ahora + timedelta(minutes=JWT_EXPIRE_MINUTES), # Cuándo expira
    }

    # Solo los trabajadores tienen encargado
    if encargado_id is not None:
        payload["encargado_id"] = encargado_id

    # Firma con JWT_SECRET
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Función para decodificar el token
def decode_token(token: str) -> dict:

    #Comprueba la firma y caducidad. Si algo falla, lanza excepción
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])