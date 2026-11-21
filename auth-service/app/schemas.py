from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .roles import Rol

# schemas.py --> contrato de la API (qué JSON acepta y cual no)

# Contrato para el registro
class RegisterIn(BaseModel):
    email: EmailStr # Comprueba que el formato sea de email
    nombre: str = Field(min_length=1, max_length=100) # Establece min y max de caracteres
    password: str = Field(min_length=8, max_length=72)


# Contrato para el login
class LoginIn(BaseModel):
    email: EmailStr # Comprueba formato de correo
    password: str = Field(max_length=72)


# Contrato para mostrar info del usuario en /auth/register
class UsuarioOut(BaseModel):

    # from_attributes permite recuperar la informacion a partir de un objeto del modelo (Usuario)
    model_config = ConfigDict(from_attributes=True)

    # Solo se muestra el id, email y nombre. No se añade la contraseña
    id: int
    email: EmailStr
    nombre: str
    rol: Rol
    encargado_id: int | None = None


# Contrato para devolver el token en /auth/login exitoso
class TokenOut(BaseModel):
    access_token: str   # token
    token_type: str = "bearer"  # Indica que el token lo mandará el cliente en la cabecera Authorization: Bearer <token>
