"""SQLAlchemy model for Vehicule."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base


class Vehicule(Base):
    """Represents a city service vehicle."""

    __tablename__ = "vehicule"

    ID_Vehicule = Column("id_vehicule", Integer, primary_key=True, autoincrement=True)
    Immatriculation = Column("immatriculation", String(20), unique=True, nullable=False)
    Type_Vehicule = Column("type_vehicule", String(50))
    Modele = Column("modele", String(100))
    Annee = Column("annee", Integer)
    Statut = Column("statut", String(50), default="AVAILABLE")

    # Relationships
    trajets = relationship("Trajet", back_populates="vehicule", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<Vehicule(id={self.ID_Vehicule}, immat='{self.Immatriculation}', "
            f"type='{self.Type_Vehicule}', statut='{self.Statut}')>"
        )
