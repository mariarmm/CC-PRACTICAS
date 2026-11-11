import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from . import models, security
from .database import get_db
from .roles import Rol


# Extrae el token de la cabecera "Authorization: Bearer <token>"
# auto_error devuelve none si falta el token
bearer = HTTPBearer(auto_error=False)

# Funcion que lee el token de la cabezera, comprueba que la firma es valida y que no ha caducada, busca el usuario en la BD y lo devuelve
def get_usuario_actual(credenciales: HTTPAuthorizationCredentials | None = Depends(bearer),db: Session = Depends(get_db),) -> models.Usuario:
    
    error = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Token no válido o ausente",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credenciales is None:
        raise error
    
    try:
        datos = security.decode_token(credenciales.credentials)
        user_id = int(datos["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise error

    #Busca un usuario por su id
    usuario = db.get(models.Usuario, user_id)

    # Si el usuario ya no existe, el token deja de ser valido
    if usuario is None:
        raise error
    
    return usuario


# Comprueba que el rol del usuario está entre los permitidos
def requiere_roles(*roles: Rol):

    permitidos = {r.value for r in roles}

    def comprobar(usuario: models.Usuario = Depends(get_usuario_actual),)-> models.Usuario:
        if usuario.rol not in permitidos:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permisos para esta acción")

        return usuario

    return comprobar