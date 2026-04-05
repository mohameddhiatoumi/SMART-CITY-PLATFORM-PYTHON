"""SQLAlchemy model for Zone."""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Zone(Base):
    """Represents a geographic zone within an arrondissement."""

    __tablename__ = "zone"

    ID_Zone = Column("id_zone", Integer, primary_key=True, autoincrement=True)
    ID_Arrondissement = Column("id_arrondissement", Integer, ForeignKey("arrondissement.id_arrondissement"))
    Nom_Zone = Column("nom_zone", String(100), nullable=False)
    Type_Zone = Column("type_zone", String(50))
    Indice_Pollution = Column("indice_pollution", Numeric(5, 2), default=0)
    Coordonnees_GPS = Column("coordonnees_gps", String(100))

    # Relationships
    arrondissement = relationship("Arrondissement", back_populates="zones")
    capteurs = relationship("Capteur", back_populates="zone", lazy="select")
    interventions = relationship("Intervention", back_populates="zone", lazy="select")

    def __repr__(self) -> str:
        return f"<Zone(id={self.ID_Zone}, nom='{self.Nom_Zone}', type='{self.Type_Zone}')>"
