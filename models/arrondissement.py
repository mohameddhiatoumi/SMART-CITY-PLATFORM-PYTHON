"""SQLAlchemy model for Arrondissement."""
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from models.base import Base


class Arrondissement(Base):
    """Represents a district (arrondissement) of Neo-Sousse."""

    __tablename__ = "arrondissement"

    ID_Arrondissement = Column("id_arrondissement", Integer, primary_key=True, autoincrement=True)
    Nom = Column("nom", String(100), nullable=False)
    Code_Postal = Column("code_postal", String(10), unique=True, nullable=False)
    Population = Column("population", Integer)
    Superficie = Column("superficie", Numeric(10, 2))

    # Relationships
    zones = relationship("Zone", back_populates="arrondissement", lazy="select")

    def __repr__(self) -> str:
        return f"<Arrondissement(id={self.ID_Arrondissement}, nom='{self.Nom}', code='{self.Code_Postal}')>"
