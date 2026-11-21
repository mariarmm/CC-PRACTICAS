from pydantic import BaseModel, ConfigDict, Field

# schemas.py --> contrato de la API (qué JSON acepta y cual no)

# Contrato para el registro
class ParcelaIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=500)

# Contrato para mostrar info de la parcela
class ParcelaOut(BaseModel):

    # from_attributes permite recuperar la informacion a partir de un objeto del modelo (Parcela)
    model_config = ConfigDict(from_attributes=True)

    # Se muestra el id, nombre, descripcion y propietario_id.
    id: int
    nombre: str
    descripcion: str | None
    propietario_id: int
