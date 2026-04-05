"""
Tests for the database models.
All tests run without a live database connection (use mock/in-memory).
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, date


class TestModelInstantiation:
    """Test that models can be instantiated without a DB connection."""

    def test_arrondissement_instantiation(self):
        from models.arrondissement import Arrondissement
        obj = Arrondissement()
        obj.Nom = "Sousse Ville"
        obj.Code_Postal = "4000"
        obj.Population = 173047
        assert obj.Nom == "Sousse Ville"
        assert obj.Code_Postal == "4000"
        assert obj.Population == 173047

    def test_arrondissement_repr(self):
        from models.arrondissement import Arrondissement
        obj = Arrondissement()
        obj.ID_Arrondissement = 1
        obj.Nom = "Sousse Ville"
        obj.Code_Postal = "4000"
        r = repr(obj)
        assert "Arrondissement" in r

    def test_zone_instantiation(self):
        from models.zone import Zone
        obj = Zone()
        obj.Nom_Zone = "Médina"
        obj.Type_Zone = "MIXED"
        obj.Indice_Pollution = 52.3
        assert obj.Nom_Zone == "Médina"
        assert obj.Type_Zone == "MIXED"

    def test_zone_repr(self):
        from models.zone import Zone
        obj = Zone()
        obj.ID_Zone = 1
        obj.Nom_Zone = "Médina"
        obj.Type_Zone = "MIXED"
        assert "Zone" in repr(obj)

    def test_capteur_instantiation(self):
        from models.capteur import Capteur
        obj = Capteur()
        obj.Type_Capteur = "AIR_QUALITY"
        obj.Statut = "ACTIVE"
        obj.etat_dfa = "ACTIVE"
        assert obj.Type_Capteur == "AIR_QUALITY"
        assert obj.etat_dfa == "ACTIVE"

    def test_capteur_dfa_column(self):
        from models.capteur import Capteur
        obj = Capteur()
        obj.etat_dfa = "SIGNALED"
        assert obj.etat_dfa == "SIGNALED"

    def test_citoyen_instantiation(self):
        from models.citoyen import Citoyen
        obj = Citoyen()
        obj.Nom = "Ben Ali"
        obj.Prenom = "Mohamed"
        obj.Email = "mohamed@test.tn"
        obj.Score_Ecologique = 75.5
        assert obj.Nom == "Ben Ali"
        assert obj.Score_Ecologique == 75.5

    def test_vehicule_instantiation(self):
        from models.vehicule import Vehicule
        obj = Vehicule()
        obj.Immatriculation = "123 TUN 4567"
        obj.Type_Vehicule = "AMBULANCE"
        obj.Statut = "AVAILABLE"
        assert obj.Type_Vehicule == "AMBULANCE"
        assert obj.Statut == "AVAILABLE"

    def test_technicien_instantiation(self):
        from models.technicien import Technicien
        obj = Technicien()
        obj.Nom = "Trabelsi"
        obj.Prenom = "Sami"
        obj.Email = "sami@tech.tn"
        obj.Specialite = "Electronique"
        obj.Disponible = True
        assert obj.Disponible is True
        assert obj.Specialite == "Electronique"

    def test_intervention_instantiation(self):
        from models.intervention import Intervention
        obj = Intervention()
        obj.Type_Intervention = "Calibration"
        obj.Priorite = "HIGH"
        obj.etat_dfa = "DEMAND"
        obj.Valide_IA = False
        assert obj.Priorite == "HIGH"
        assert obj.etat_dfa == "DEMAND"

    def test_trajet_instantiation(self):
        from models.trajet import Trajet
        obj = Trajet()
        obj.Point_Depart = "Médina"
        obj.Point_Arrivee = "Zone Industrielle"
        obj.etat_dfa = "PARKED"
        assert obj.etat_dfa == "PARKED"

    def test_affecte_instantiation(self):
        from models.affecte import Affecte
        obj = Affecte()
        obj.ID_Intervention = 1
        obj.ID_Technicien = 2
        obj.Role_Technicien = "TECH1"
        assert obj.Role_Technicien == "TECH1"

    def test_mesure_capteur_instantiation(self):
        from models.mesure_capteur import MesureCapteur
        obj = MesureCapteur()
        obj.Valeur = 45.7
        obj.Unite = "AQI"
        obj.Qualite_Signal = 0.95
        assert obj.Valeur == 45.7
        assert obj.Unite == "AQI"

    def test_system_ia_instantiation(self):
        from models.system_ia import SystemIA
        obj = SystemIA()
        obj.Version = "2.0.0"
        obj.Seuil_Confiance = 0.85
        obj.Modele_Utilise = "GPT-4"
        assert obj.Version == "2.0.0"

    def test_consultation_instantiation(self):
        from models.consultation import Consultation
        obj = Consultation()
        obj.Question = "Quelle est la qualite de l'air ?"
        obj.Reponse = "La qualite est bonne."
        obj.Note_Satisfaction = 4
        assert obj.Note_Satisfaction == 4


class TestModelAttributes:
    """Test model attribute definitions."""

    def test_capteur_has_etat_dfa(self):
        from models.capteur import Capteur
        assert hasattr(Capteur, "etat_dfa")

    def test_intervention_has_etat_dfa(self):
        from models.intervention import Intervention
        assert hasattr(Intervention, "etat_dfa")

    def test_trajet_has_etat_dfa(self):
        from models.trajet import Trajet
        assert hasattr(Trajet, "etat_dfa")

    def test_intervention_has_valide_ia(self):
        from models.intervention import Intervention
        assert hasattr(Intervention, "Valide_IA")

    def test_citoyen_has_score_ecologique(self):
        from models.citoyen import Citoyen
        assert hasattr(Citoyen, "Score_Ecologique")

    def test_zone_has_indice_pollution(self):
        from models.zone import Zone
        assert hasattr(Zone, "Indice_Pollution")

    def test_arrondissement_has_population(self):
        from models.arrondissement import Arrondissement
        assert hasattr(Arrondissement, "Population")

    def test_technicien_has_disponible(self):
        from models.technicien import Technicien
        assert hasattr(Technicien, "Disponible")


class TestModelTableNames:
    """Test that models use correct table names."""

    def test_arrondissement_tablename(self):
        from models.arrondissement import Arrondissement
        assert Arrondissement.__tablename__ == "arrondissement"

    def test_zone_tablename(self):
        from models.zone import Zone
        assert Zone.__tablename__ == "zone"

    def test_capteur_tablename(self):
        from models.capteur import Capteur
        assert Capteur.__tablename__ == "capteur"

    def test_citoyen_tablename(self):
        from models.citoyen import Citoyen
        assert Citoyen.__tablename__ == "citoyen"

    def test_vehicule_tablename(self):
        from models.vehicule import Vehicule
        assert Vehicule.__tablename__ == "vehicule"

    def test_intervention_tablename(self):
        from models.intervention import Intervention
        assert Intervention.__tablename__ == "intervention"

    def test_trajet_tablename(self):
        from models.trajet import Trajet
        assert Trajet.__tablename__ == "trajet"

    def test_technicien_tablename(self):
        from models.technicien import Technicien
        assert Technicien.__tablename__ == "technicien"


class TestBaseModule:
    """Test the base module functions."""

    def test_base_is_importable(self):
        from models.base import Base, get_engine, get_session_factory, get_session
        assert Base is not None

    def test_models_init_importable(self):
        from models import (
            Arrondissement, Zone, Capteur, Citoyen, Vehicule, Trajet,
            Technicien, Intervention, Affecte, MesureCapteur, SystemIA, Consultation
        )
        assert Arrondissement is not None
        assert Zone is not None
        assert Capteur is not None

    def test_get_engine_with_mock_url(self):
        from models.base import get_engine
        engine = get_engine("sqlite:///:memory:")
        assert engine is not None

    def test_get_session_factory_with_mock_url(self):
        from models.base import get_session_factory
        factory = get_session_factory("sqlite:///:memory:")
        assert factory is not None
