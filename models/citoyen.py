"""SQLAlchemy model for Citoyen (Citizen)."""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from models.base import Base


class Citoyen(Base):
    """Represents a citizen of Neo-Sousse."""

    __tablename__ = "citoyen"

    ID_Citoyen = Column("id_citoyen", Integer, primary_key=True, autoincrement=True)
    Nom = Column("nom", String(100), nullable=False)
    Prenom = Column("prenom", String(100), nullable=False)
    Email = Column("email", String(200), unique=True, nullable=False)
    Telephone = Column("telephone", String(20))
    Adresse = Column("adresse", Text)
    Score_Ecologique = Column("score_ecologique", Numeric(5, 2), default=50)
    Date_Inscription = Column("date_inscription", DateTime, default=func.now())

    # Relationships
    consultations = relationship("Consultation", back_populates="citoyen", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<Citoyen(id={self.ID_Citoyen}, nom='{self.Nom}', "
            f"prenom='{self.Prenom}', score={self.Score_Ecologique})>"
        )
