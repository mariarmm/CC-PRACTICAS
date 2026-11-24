from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import security
from .roles import Rol


# Extrae el token de la cabecera "Authorization: Bearer <token>"
# auto_error devuelve none si falta el token
bearer = HTTPBearer(auto_error=False)


@dataclass
class UsuarioToken:
    # Los datos del usuario salen del propio token, sin consultar ninguna BD
    id: int
    email: str
    rol: Rol
    encargado_id: int | None


# Funcion que lee el token de la cabezera, comprueba que la firma es valida y que no ha caducado
def get_usuario_actual(credenciales: HTTPAuthorizationCredentials | None = Depends(bearer),) -> UsuarioToken:

    error = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Token no válido o ausente",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credenciales is None:
        raise error
    
    try:
        datos = security.decode_token(credenciales.credentials)
        return UsuarioToken(id=int(datos["sub"]),email=datos["email"],rol=Rol(datos["rol"]),encargado_id=datos.get("encargado_id"),)
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise error


# Comprueba que el rol del usuario está entre los permitidos
def requiere_roles(*roles: Rol):

    permitidos = set(roles)

    def comprobar(usuario: UsuarioToken = Depends(get_usuario_actual)) -> UsuarioToken:
        if usuario.rol not in permitidos:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permisos para esta acción")
        return usuario

    return comprobar
