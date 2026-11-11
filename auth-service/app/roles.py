from enum import Enum

# Enum de rol
class Rol(str, Enum):
    ADMIN = "admin"
    ENCARGADO = "encargado"
    TRABAJADOR = "trabajador"
