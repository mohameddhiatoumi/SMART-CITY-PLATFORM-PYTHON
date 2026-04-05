"""SQLAlchemy model for Consultation."""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base import Base


class Consultation(Base):
    """Represents a citizen consultation with the AI system."""

    __tablename__ = "consultation"

    ID_Consultation = Column("id_consultation", Integer, primary_key=True, autoincrement=True)
    ID_Citoyen = Column("id_citoyen", Integer, ForeignKey("citoyen.id_citoyen"))
    ID_Systeme = Column("id_systeme", Integer, ForeignKey("system_ia.id_systeme"))
    Question = Column("question", Text, nullable=False)
    Reponse = Column("reponse", Text)
    Date_Consultation = Column("date_consultation", DateTime, default=func.now())
    Note_Satisfaction = Column("note_satisfaction", Integer)

    # Relationships
    citoyen = relationship("Citoyen", back_populates="consultations")
    systeme = relationship("SystemIA", back_populates="consultations")

    def __repr__(self) -> str:
        return (
            f"<Consultation(id={self.ID_Consultation}, citoyen={self.ID_Citoyen}, "
            f"note={self.Note_Satisfaction})>"
        )
