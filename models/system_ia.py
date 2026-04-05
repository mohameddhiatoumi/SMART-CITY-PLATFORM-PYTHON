"""SQLAlchemy model for System_IA."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from sqlalchemy.orm import relationship
from models.base import Base


class SystemIA(Base):
    """Represents an AI system version used for consultations."""

    __tablename__ = "system_ia"

    ID_Systeme = Column("id_systeme", Integer, primary_key=True, autoincrement=True)
    Version = Column("version", String(50))
    Seuil_Confiance = Column("seuil_confiance", Numeric(3, 2))
    Date_Maj = Column("date_maj", DateTime, default=func.now())
    Modele_Utilise = Column("modele_utilise", String(100))
    Nb_Predictions = Column("nb_predictions", Integer, default=0)

    # Relationships
    consultations = relationship("Consultation", back_populates="systeme", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<SystemIA(id={self.ID_Systeme}, version='{self.Version}', "
            f"modele='{self.Modele_Utilise}')>"
        )
