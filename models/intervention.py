"""SQLAlchemy model for Intervention."""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base


class Intervention(Base):
    """Represents a maintenance/repair intervention."""

    __tablename__ = "intervention"

    ID_Intervention = Column("id_intervention", Integer, primary_key=True, autoincrement=True)
    ID_Capteur = Column("id_capteur", Integer, ForeignKey("capteur.id_capteur"))
    ID_Zone = Column("id_zone", Integer, ForeignKey("zone.id_zone"))
    Type_Intervention = Column("type_intervention", String(100))
    Description = Column("description", Text)
    Priorite = Column("priorite", String(20), default="MEDIUM")
    Date_Demande = Column("date_demande", DateTime, default=func.now())
    Date_Completion = Column("date_completion", DateTime)
    Valide_IA = Column("valide_ia", Boolean, default=False)
    etat_dfa = Column("etat_dfa", String(50), default="DEMAND")
    timestamp_derniere_transition = Column(
        "timestamp_derniere_transition", DateTime, default=func.now()
    )

    # Relationships
    capteur = relationship("Capteur", back_populates="interventions")
    zone = relationship("Zone", back_populates="interventions")
    affectations = relationship("Affecte", back_populates="intervention", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<Intervention(id={self.ID_Intervention}, type='{self.Type_Intervention}', "
            f"priorite='{self.Priorite}', dfa='{self.etat_dfa}')>"
        )
