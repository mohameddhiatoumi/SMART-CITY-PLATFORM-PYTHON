"""SQLAlchemy model for Technicien."""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from models.base import Base


class Technicien(Base):
    """Represents a maintenance technician."""

    __tablename__ = "technicien"

    ID_Technicien = Column("id_technicien", Integer, primary_key=True, autoincrement=True)
    Nom = Column("nom", String(100), nullable=False)
    Prenom = Column("prenom", String(100), nullable=False)
    Email = Column("email", String(200), unique=True, nullable=False)
    Specialite = Column("specialite", String(100))
    Niveau_Experience = Column("niveau_experience", Integer, default=1)
    Disponible = Column("disponible", Boolean, default=True)

    # Relationships
    affectations = relationship("Affecte", back_populates="technicien", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<Technicien(id={self.ID_Technicien}, nom='{self.Nom}', "
            f"specialite='{self.Specialite}', disponible={self.Disponible})>"
        )
