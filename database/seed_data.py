"""
Seed data generator for Smart City Platform.
Generates 1000+ realistic records for Sousse, Tunisia.
"""
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta, date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DATABASE_URL

try:
    from faker import Faker
    fake = Faker("fr_FR")
    Faker.seed(42)
except ImportError:
    fake = None


# ── Realistic Sousse data ────────────────────────────────────────────────────

ARRONDISSEMENTS = [
    {"nom": "Sousse Ville", "code_postal": "4000", "population": 173047, "superficie": 44.5},
    {"nom": "Hammam Sousse", "code_postal": "4011", "population": 85432, "superficie": 32.1},
    {"nom": "Akouda", "code_postal": "4022", "population": 32178, "superficie": 18.7},
    {"nom": "Kalaa Kebira", "code_postal": "4060", "population": 42891, "superficie": 28.3},
    {"nom": "Msaken", "code_postal": "4070", "population": 61234, "superficie": 36.8},
]

ZONES = [
    # Sousse Ville
    {"arr": 1, "nom": "Médina de Sousse", "type": "MIXED", "pollution": 52.3, "gps": "35.8256,10.6369"},
    {"arr": 1, "nom": "Zone Industrielle Sousse Nord", "type": "INDUSTRIAL", "pollution": 78.4, "gps": "35.8421,10.6201"},
    {"arr": 1, "nom": "Boulevard de la Corniche", "type": "COMMERCIAL", "pollution": 44.1, "gps": "35.8312,10.6445"},
    {"arr": 1, "nom": "Quartier Erriadh", "type": "RESIDENTIAL", "pollution": 28.7, "gps": "35.8189,10.6312"},
    # Hammam Sousse
    {"arr": 2, "nom": "Centre Hammam Sousse", "type": "COMMERCIAL", "pollution": 38.2, "gps": "35.8591,10.5975"},
    {"arr": 2, "nom": "Zone Hôtelière Hammam Sousse", "type": "MIXED", "pollution": 22.5, "gps": "35.8634,10.5821"},
    {"arr": 2, "nom": "Parc Industriel Enfidha Road", "type": "INDUSTRIAL", "pollution": 65.9, "gps": "35.8712,10.5654"},
    {"arr": 2, "nom": "Résidence Al Andalous", "type": "RESIDENTIAL", "pollution": 18.3, "gps": "35.8523,10.6012"},
    # Akouda
    {"arr": 3, "nom": "Centre Akouda", "type": "MIXED", "pollution": 35.6, "gps": "35.8789,10.5723"},
    {"arr": 3, "nom": "Parc Vert Akouda", "type": "GREEN", "pollution": 8.1, "gps": "35.8823,10.5612"},
    {"arr": 3, "nom": "Zone Commerciale Akouda", "type": "COMMERCIAL", "pollution": 41.2, "gps": "35.8756,10.5789"},
    {"arr": 3, "nom": "Cité Universitaire Sousse", "type": "RESIDENTIAL", "pollution": 25.4, "gps": "35.8801,10.5834"},
    # Kalaa Kebira
    {"arr": 4, "nom": "Centre Kalaa Kebira", "type": "MIXED", "pollution": 33.8, "gps": "35.8934,10.5456"},
    {"arr": 4, "nom": "Zone Industrielle Kalaa", "type": "INDUSTRIAL", "pollution": 71.2, "gps": "35.8987,10.5312"},
    {"arr": 4, "nom": "Parc Municipal Kalaa", "type": "GREEN", "pollution": 12.3, "gps": "35.9012,10.5534"},
    # Msaken
    {"arr": 5, "nom": "Centre Msaken", "type": "MIXED", "pollution": 42.6, "gps": "35.7312,10.5834"},
    {"arr": 5, "nom": "Zone Artisanale Msaken", "type": "INDUSTRIAL", "pollution": 58.9, "gps": "35.7267,10.5756"},
    {"arr": 5, "nom": "Parc Industriel Msaken", "type": "INDUSTRIAL", "pollution": 82.1, "gps": "35.7189,10.5623"},
    {"arr": 5, "nom": "Quartier Résidentiel Msaken", "type": "RESIDENTIAL", "pollution": 21.7, "gps": "35.7345,10.5912"},
    {"arr": 5, "nom": "Espace Vert Oued Msaken", "type": "GREEN", "pollution": 9.4, "gps": "35.7423,10.5845"},
]

SENSOR_TYPES = ["AIR_QUALITY", "TEMPERATURE", "HUMIDITY", "NOISE", "TRAFFIC", "WATER_QUALITY"]
SENSOR_UNITS = {
    "AIR_QUALITY": "AQI",
    "TEMPERATURE": "°C",
    "HUMIDITY": "%",
    "NOISE": "dB",
    "TRAFFIC": "veh/h",
    "WATER_QUALITY": "NTU",
}
SENSOR_MODELS = [
    "Bosch BME680", "Sensirion SCD41", "Siemens SITRANS", "SICK AG TDC-E",
    "ABB AX400", "Honeywell MIDAS", "Vaisala HMP110", "Endress+Hauser",
]
VEHICLE_TYPES = ["AMBULANCE", "POLICE", "FIRE_TRUCK", "GARBAGE", "MAINTENANCE", "BUS"]
SPECIALITES = [
    "Électronique", "Mécanique", "Informatique industrielle", "Réseaux",
    "Hydraulique", "Chimie environnementale", "Génie civil", "Énergie renouvelable",
]
INTERVENTION_TYPES = [
    "Remplacement capteur", "Calibration", "Réparation électronique",
    "Maintenance préventive", "Dépannage urgent", "Mise à jour firmware",
    "Remplacement batterie", "Nettoyage", "Inspection",
]
TUNISIAN_FIRST_NAMES = [
    "Mohamed", "Ahmed", "Ali", "Omar", "Youssef", "Khaled", "Sami", "Rami",
    "Fatma", "Amel", "Sonia", "Ines", "Nadia", "Leila", "Salma", "Rim",
    "Karim", "Tarek", "Bassem", "Walid",
]
TUNISIAN_LAST_NAMES = [
    "Ben Ali", "Trabelsi", "Chaabane", "Amara", "Mbarki", "Hamdi", "Cherni",
    "Turki", "Miled", "Saidi", "Khemiri", "Jebali", "Mansouri", "Ouali",
    "Ghribi", "Elloumi", "Belhaj", "Khelifi", "Zarrouk", "Rekik",
]

random.seed(42)


def get_connection():
    import psycopg2
    return psycopg2.connect(DATABASE_URL)


def seed_arrondissements(cur) -> list[int]:
    ids = []
    for arr in ARRONDISSEMENTS:
        cur.execute(
            """INSERT INTO Arrondissement(Nom, Code_Postal, Population, Superficie)
               VALUES(%s,%s,%s,%s) RETURNING ID_Arrondissement""",
            (arr["nom"], arr["code_postal"], arr["population"], arr["superficie"]),
        )
        ids.append(cur.fetchone()[0])
    print(f"  ✓ {len(ids)} Arrondissements inserted")
    return ids


def seed_zones(cur, arr_ids: list[int]) -> list[int]:
    ids = []
    for z in ZONES:
        arr_id = arr_ids[z["arr"] - 1]
        cur.execute(
            """INSERT INTO Zone(ID_Arrondissement, Nom_Zone, Type_Zone, Indice_Pollution, Coordonnees_GPS)
               VALUES(%s,%s,%s,%s,%s) RETURNING ID_Zone""",
            (arr_id, z["nom"], z["type"], z["pollution"], z["gps"]),
        )
        ids.append(cur.fetchone()[0])
    print(f"  ✓ {len(ids)} Zones inserted")
    return ids


def seed_capteurs(cur, zone_ids: list[int]) -> list[int]:
    ids = []
    statuts = ["ACTIVE", "ACTIVE", "ACTIVE", "INACTIVE", "MAINTENANCE", "FAULTY"]
    etat_dfas = ["ACTIVE", "ACTIVE", "INACTIVE", "SIGNALED", "MAINTENANCE"]
    for i in range(50):
        zone_id = random.choice(zone_ids)
        stype = random.choice(SENSOR_TYPES)
        statut = random.choice(statuts)
        etat = random.choice(etat_dfas)
        install_date = date(2020, 1, 1) + timedelta(days=random.randint(0, 1400))
        cur.execute(
            """INSERT INTO Capteur(ID_Zone, Type_Capteur, Modele, Date_Installation, Statut, etat_dfa)
               VALUES(%s,%s,%s,%s,%s,%s) RETURNING ID_Capteur""",
            (zone_id, stype, random.choice(SENSOR_MODELS), install_date, statut, etat),
        )
        ids.append(cur.fetchone()[0])
    print(f"  ✓ {len(ids)} Capteurs inserted")
    return ids


def seed_citoyens(cur) -> list[int]:
    ids = []
    used_emails = set()
    for i in range(30):
        fname = random.choice(TUNISIAN_FIRST_NAMES)
        lname = random.choice(TUNISIAN_LAST_NAMES)
        email_base = f"{fname.lower()}.{lname.lower().replace(' ', '')}{i}"
        email = f"{email_base}@sousse.tn"
        if email in used_emails:
            email = f"{email_base}_{random.randint(100,999)}@sousse.tn"
        used_emails.add(email)
        phone = f"+216 {random.randint(20,99)} {random.randint(100,999)} {random.randint(100,999)}"
        score = round(random.uniform(20, 95), 2)
        cur.execute(
            """INSERT INTO Citoyen(Nom, Prenom, Email, Telephone, Adresse, Score_Ecologique)
               VALUES(%s,%s,%s,%s,%s,%s) RETURNING ID_Citoyen""",
            (lname, fname, email, phone,
             f"{random.randint(1,99)} Rue {random.choice(['Habib Bourguiba','Ibn Khaldoun','de la République'])}, Sousse",
             score),
        )
        ids.append(cur.fetchone()[0])
    print(f"  ✓ {len(ids)} Citoyens inserted")
    return ids


def seed_vehicules(cur) -> list[int]:
    ids = []
    used_plates = set()
    for i in range(20):
        vtype = random.choice(VEHICLE_TYPES)
        plate = f"{random.randint(100,999)} TUN {random.randint(1000,9999)}"
        while plate in used_plates:
            plate = f"{random.randint(100,999)} TUN {random.randint(1000,9999)}"
        used_plates.add(plate)
        year = random.randint(2015, 2023)
        statut = random.choice(["AVAILABLE", "AVAILABLE", "IN_USE", "MAINTENANCE"])
        models = {"AMBULANCE": "Mercedes Sprinter", "POLICE": "Peugeot 308",
                  "FIRE_TRUCK": "MAN TGM", "GARBAGE": "Renault Maxity",
                  "MAINTENANCE": "Toyota HiLux", "BUS": "Irisbus Crossway"}
        cur.execute(
            """INSERT INTO Vehicule(Immatriculation, Type_Vehicule, Modele, Annee, Statut)
               VALUES(%s,%s,%s,%s,%s) RETURNING ID_Vehicule""",
            (plate, vtype, models.get(vtype, "Inconnu"), year, statut),
        )
        ids.append(cur.fetchone()[0])
    print(f"  ✓ {len(ids)} Vehicules inserted")
    return ids


def seed_trajets(cur, vehicule_ids: list[int]) -> list[int]:
    ids = []
    locations = [
        "Hôpital Farhat Hached", "Commissariat Central", "Mairie de Sousse",
        "Zone Industrielle Nord", "Médina", "Corniche", "Gare SNCFT",
        "Aéroport Enfidha", "Campus Universitaire", "Marché Central",
    ]
    for _ in range(40):
        vid = random.choice(vehicule_ids)
        depart = random.choice(locations)
        arrivee = random.choice([l for l in locations if l != depart])
        h_depart = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        h_arrivee = h_depart + timedelta(minutes=random.randint(10, 120))
        distance = round(random.uniform(1.5, 45.0), 2)
        statut = random.choice(["PLANNED", "IN_PROGRESS", "COMPLETED", "COMPLETED", "CANCELLED"])
        etat = {"PLANNED": "PARKED", "IN_PROGRESS": "EN_ROUTE",
                "COMPLETED": "ARRIVED", "CANCELLED": "PARKED"}.get(statut, "PARKED")
        cur.execute(
            """INSERT INTO Trajet(ID_Vehicule, Point_Depart, Point_Arrivee,
                                  Heure_Depart, Heure_Arrivee, Distance, Statut, etat_dfa)
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s) RETURNING ID_Trajet""",
            (vid, depart, arrivee, h_depart, h_arrivee, distance, statut, etat),
        )
        ids.append(cur.fetchone()[0])
    print(f"  ✓ {len(ids)} Trajets inserted")
    return ids


def seed_techniciens(cur) -> list[int]:
    ids = []
    used_emails = set()
    for i in range(20):
        fname = random.choice(TUNISIAN_FIRST_NAMES)
        lname = random.choice(TUNISIAN_LAST_NAMES)
        email = f"tech.{fname.lower()}{i}@maintenance.sousse.tn"
        while email in used_emails:
            email = f"tech.{fname.lower()}{i}_{random.randint(10,99)}@maintenance.sousse.tn"
        used_emails.add(email)
        cur.execute(
            """INSERT INTO Technicien(Nom, Prenom, Email, Specialite, Niveau_Experience, Disponible)
               VALUES(%s,%s,%s,%s,%s,%s) RETURNING ID_Technicien""",
            (lname, fname, email, random.choice(SPECIALITES),
             random.randint(1, 5), random.choice([True, True, True, False])),
        )
        ids.append(cur.fetchone()[0])
    print(f"  ✓ {len(ids)} Techniciens inserted")
    return ids


def seed_interventions(cur, capteur_ids: list[int], zone_ids: list[int]) -> list[int]:
    ids = []
    priorites = ["LOW", "MEDIUM", "MEDIUM", "HIGH", "CRITICAL"]
    etats = ["DEMAND", "TECH1_ASSIGNED", "TECH2_VALIDATED", "AI_VALIDATED", "COMPLETED"]
    for _ in range(50):
        cap_id = random.choice(capteur_ids)
        zone_id = random.choice(zone_ids)
        priorite = random.choice(priorites)
        etat = random.choice(etats)
        date_demande = datetime.now() - timedelta(days=random.randint(0, 60))
        date_completion = (date_demande + timedelta(days=random.randint(1, 10))
                           if etat == "COMPLETED" else None)
        valide_ia = etat in ("AI_VALIDATED", "COMPLETED")
        cur.execute(
            """INSERT INTO Intervention(ID_Capteur, ID_Zone, Type_Intervention, Description,
                                         Priorite, Date_Demande, Date_Completion, Valide_IA, etat_dfa)
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING ID_Intervention""",
            (cap_id, zone_id, random.choice(INTERVENTION_TYPES),
             f"Intervention sur capteur zone - {random.choice(INTERVENTION_TYPES)}",
             priorite, date_demande, date_completion, valide_ia, etat),
        )
        ids.append(cur.fetchone()[0])
    print(f"  ✓ {len(ids)} Interventions inserted")
    return ids


def seed_affecte(cur, intervention_ids: list[int], technicien_ids: list[int]):
    count = 0
    roles = ["TECH1", "TECH2", "SUPERVISOR"]
    assigned = set()
    attempts = 0
    while count < 100 and attempts < 500:
        attempts += 1
        int_id = random.choice(intervention_ids)
        tech_id = random.choice(technicien_ids)
        key = (int_id, tech_id)
        if key in assigned:
            continue
        assigned.add(key)
        role = random.choice(roles)
        try:
            cur.execute(
                """INSERT INTO Affecte(ID_Intervention, ID_Technicien, Role_Technicien)
                   VALUES(%s,%s,%s)""",
                (int_id, tech_id, role),
            )
            count += 1
        except Exception:
            pass
    print(f"  ✓ {count} Affecte records inserted")


def seed_mesures(cur, capteur_ids: list[int]):
    count = 0
    for _ in range(1000):
        cap_id = random.choice(capteur_ids)
        # Determine unit based on sensor type (simplified: random plausible values)
        valeur = round(random.uniform(0, 200), 4)
        unite = random.choice(["AQI", "°C", "%", "dB", "veh/h", "NTU"])
        ts = datetime.now() - timedelta(hours=random.randint(0, 720))
        qualite = round(random.uniform(0.6, 1.0), 2)
        cur.execute(
            """INSERT INTO Mesure_Capteur(ID_Capteur, Valeur, Unite, Timestamp_Mesure, Qualite_Signal)
               VALUES(%s,%s,%s,%s,%s)""",
            (cap_id, valeur, unite, ts, qualite),
        )
        count += 1
    print(f"  ✓ {count} Mesure_Capteur records inserted")


def seed_system_ia(cur) -> list[int]:
    ids = []
    systems = [
        ("1.0.0", 0.75, "GPT-3.5-turbo", 1234),
        ("2.0.0", 0.85, "GPT-4-turbo", 3891),
    ]
    for v, seuil, modele, nb in systems:
        cur.execute(
            """INSERT INTO System_IA(Version, Seuil_Confiance, Modele_Utilise, Nb_Predictions)
               VALUES(%s,%s,%s,%s) RETURNING ID_Systeme""",
            (v, seuil, modele, nb),
        )
        ids.append(cur.fetchone()[0])
    print(f"  ✓ {len(ids)} System_IA records inserted")
    return ids


def seed_consultations(cur, citoyen_ids: list[int], systeme_ids: list[int]):
    questions = [
        "Quelle est la qualité de l'air dans mon quartier ?",
        "Quand aura lieu la prochaine collecte des déchets ?",
        "Y a-t-il des pannes de capteurs signalées ?",
        "Quel est l'indice de pollution dans la zone industrielle ?",
        "Comment améliorer mon score écologique ?",
        "Quelles interventions sont en cours dans ma zone ?",
        "Quels sont les horaires de transport en commun ?",
        "Comment signaler un problème environnemental ?",
        "Quelles zones sont les plus polluées aujourd'hui ?",
        "Quels capteurs sont en maintenance ?",
    ]
    count = 0
    for _ in range(30):
        cit_id = random.choice(citoyen_ids)
        sys_id = random.choice(systeme_ids)
        q = random.choice(questions)
        reponse = f"Réponse automatique générée par le système IA version {random.choice(['1.0', '2.0'])}."
        note = random.randint(3, 5)
        cur.execute(
            """INSERT INTO Consultation(ID_Citoyen, ID_Systeme, Question, Reponse, Note_Satisfaction)
               VALUES(%s,%s,%s,%s,%s)""",
            (cit_id, sys_id, q, reponse, note),
        )
        count += 1
    print(f"  ✓ {count} Consultation records inserted")


def main():
    """Main seed function."""
    print("Starting data seeding for Smart City Platform - Neo-Sousse 2030")
    print("=" * 60)
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 not installed.")
        sys.exit(1)

    try:
        conn = get_connection()
        conn.autocommit = False
        cur = conn.cursor()

        arr_ids = seed_arrondissements(cur)
        zone_ids = seed_zones(cur, arr_ids)
        cap_ids = seed_capteurs(cur, zone_ids)
        cit_ids = seed_citoyens(cur)
        veh_ids = seed_vehicules(cur)
        seed_trajets(cur, veh_ids)
        tech_ids = seed_techniciens(cur)
        int_ids = seed_interventions(cur, cap_ids, zone_ids)
        seed_affecte(cur, int_ids, tech_ids)
        seed_mesures(cur, cap_ids)
        sys_ids = seed_system_ia(cur)
        seed_consultations(cur, cit_ids, sys_ids)

        conn.commit()
        cur.close()
        conn.close()
        print("=" * 60)
        print("✓ Data seeding complete!")
    except Exception as e:
        print(f"ERROR during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
