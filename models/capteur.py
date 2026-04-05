"""SQLAlchemy model for Capteur (Sensor)."""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base


class Capteur(Base):
    """Represents an IoT sensor deployed in the city."""

    __tablename__ = "capteur"

    ID_Capteur = Column("id_capteur", Integer, primary_key=True, autoincrement=True)
    ID_Zone = Column("id_zone", Integer, ForeignKey("zone.id_zone"))
    Type_Capteur = Column("type_capteur", String(50))
    Modele = Column("modele", String(100))
    Date_Installation = Column("date_installation", Date)
    Statut = Column("statut", String(50), default="ACTIVE")
    etat_dfa = Column("etat_dfa", String(50), default="INACTIVE")
    timestamp_derniere_transition = Column(
        "timestamp_derniere_transition", DateTime, default=func.now()
    )

    # Relationships
    zone = relationship("Zone", back_populates="capteurs")
    mesures = relationship("MesureCapteur", back_populates="capteur", lazy="select")
    interventions = relationship("Intervention", back_populates="capteur", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<Capteur(id={self.ID_Capteur}, type='{self.Type_Capteur}', "
            f"statut='{self.Statut}', dfa='{self.etat_dfa}')>"
        )
