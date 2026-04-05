"""SQLAlchemy model for Mesure_Capteur (Sensor Reading)."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base


class MesureCapteur(Base):
    """Represents a sensor measurement reading."""

    __tablename__ = "mesure_capteur"

    ID_Mesure = Column("id_mesure", Integer, primary_key=True, autoincrement=True)
    ID_Capteur = Column("id_capteur", Integer, ForeignKey("capteur.id_capteur"))
    Valeur = Column("valeur", Numeric(10, 4), nullable=False)
    Unite = Column("unite", String(20))
    Timestamp_Mesure = Column("timestamp_mesure", DateTime, default=func.now())
    Qualite_Signal = Column("qualite_signal", Numeric(3, 2), default=1.0)

    # Relationships
    capteur = relationship("Capteur", back_populates="mesures")

    def __repr__(self) -> str:
        return (
            f"<MesureCapteur(id={self.ID_Mesure}, capteur={self.ID_Capteur}, "
            f"valeur={self.Valeur} {self.Unite})>"
        )
