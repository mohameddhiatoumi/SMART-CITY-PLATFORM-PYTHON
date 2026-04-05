"""SQLAlchemy model for Affecte (Technician Assignment)."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base


class Affecte(Base):
    """Represents the assignment of a technician to an intervention."""

    __tablename__ = "affecte"

    ID_Affecte = Column("id_affecte", Integer, primary_key=True, autoincrement=True)
    ID_Intervention = Column("id_intervention", Integer, ForeignKey("intervention.id_intervention"))
    ID_Technicien = Column("id_technicien", Integer, ForeignKey("technicien.id_technicien"))
    Role_Technicien = Column("role_technicien", String(50))
    Date_Affectation = Column("date_affectation", DateTime, default=func.now())

    # Relationships
    intervention = relationship("Intervention", back_populates="affectations")
    technicien = relationship("Technicien", back_populates="affectations")

    def __repr__(self) -> str:
        return (
            f"<Affecte(intervention={self.ID_Intervention}, "
            f"technicien={self.ID_Technicien}, role='{self.Role_Technicien}')>"
        )
