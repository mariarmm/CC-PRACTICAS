from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

# Tabla Parcela
class Parcela(Base):

    #Nombre de la tabla
    __tablename__ = "parcelas"

    # Atributos
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Id del encargado dueño de la parcela. Sin clave foránea porque esa tabla está en otra bd
    propietario_id: Mapped[int] = mapped_column(index=True)

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
