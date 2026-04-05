"""SQLAlchemy model for Trajet (Vehicle Route)."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base


class Trajet(Base):
    """Represents a vehicle route/trajectory."""

    __tablename__ = "trajet"

    ID_Trajet = Column("id_trajet", Integer, primary_key=True, autoincrement=True)
    ID_Vehicule = Column("id_vehicule", Integer, ForeignKey("vehicule.id_vehicule"))
    Point_Depart = Column("point_depart", String(200))
    Point_Arrivee = Column("point_arrivee", String(200))
    Heure_Depart = Column("heure_depart", DateTime)
    Heure_Arrivee = Column("heure_arrivee", DateTime)
    Distance = Column("distance", Numeric(10, 2))
    Statut = Column("statut", String(50), default="PLANNED")
    etat_dfa = Column("etat_dfa", String(50), default="PARKED")
    timestamp_derniere_transition = Column(
        "timestamp_derniere_transition", DateTime, default=func.now()
    )

    # Relationships
    vehicule = relationship("Vehicule", back_populates="trajets")

    def __repr__(self) -> str:
        return (
            f"<Trajet(id={self.ID_Trajet}, depart='{self.Point_Depart}', "
            f"arrivee='{self.Point_Arrivee}', dfa='{self.etat_dfa}')>"
        )
