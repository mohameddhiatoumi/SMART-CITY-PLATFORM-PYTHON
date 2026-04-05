-- Smart City Platform - Neo-Sousse 2030
-- Database Schema

-- Drop existing tables (in reverse dependency order)
DROP TABLE IF EXISTS Consultation CASCADE;
DROP TABLE IF EXISTS System_IA CASCADE;
DROP TABLE IF EXISTS Mesure_Capteur CASCADE;
DROP TABLE IF EXISTS Affecte CASCADE;
DROP TABLE IF EXISTS Intervention CASCADE;
DROP TABLE IF EXISTS Technicien CASCADE;
DROP TABLE IF EXISTS Trajet CASCADE;
DROP TABLE IF EXISTS Vehicule CASCADE;
DROP TABLE IF EXISTS Capteur CASCADE;
DROP TABLE IF EXISTS Citoyen CASCADE;
DROP TABLE IF EXISTS Zone CASCADE;
DROP TABLE IF EXISTS Arrondissement CASCADE;

-- Drop existing views
DROP VIEW IF EXISTS v_zones_pollution CASCADE;
DROP VIEW IF EXISTS v_capteurs_actifs CASCADE;
DROP VIEW IF EXISTS v_interventions_en_cours CASCADE;

-- ============================================================
-- TABLE: Arrondissement
-- ============================================================
CREATE TABLE Arrondissement (
    ID_Arrondissement SERIAL PRIMARY KEY,
    Nom              VARCHAR(100) NOT NULL,
    Code_Postal      VARCHAR(10)  UNIQUE NOT NULL,
    Population       INTEGER      CHECK(Population >= 0),
    Superficie       DECIMAL(10,2) CHECK(Superficie > 0)
);

-- ============================================================
-- TABLE: Zone
-- ============================================================
CREATE TABLE Zone (
    ID_Zone           SERIAL PRIMARY KEY,
    ID_Arrondissement INTEGER REFERENCES Arrondissement(ID_Arrondissement) ON DELETE SET NULL,
    Nom_Zone          VARCHAR(100) NOT NULL,
    Type_Zone         VARCHAR(50)  CHECK(Type_Zone IN ('RESIDENTIAL','COMMERCIAL','INDUSTRIAL','GREEN','MIXED')),
    Indice_Pollution  DECIMAL(5,2) DEFAULT 0,
    Coordonnees_GPS   VARCHAR(100)
);

-- ============================================================
-- TABLE: Citoyen
-- ============================================================
CREATE TABLE Citoyen (
    ID_Citoyen       SERIAL PRIMARY KEY,
    Nom              VARCHAR(100) NOT NULL,
    Prenom           VARCHAR(100) NOT NULL,
    Email            VARCHAR(200) UNIQUE NOT NULL,
    Telephone        VARCHAR(20),
    Adresse          TEXT,
    Score_Ecologique DECIMAL(5,2) DEFAULT 50
                     CHECK(Score_Ecologique >= 0 AND Score_Ecologique <= 100),
    Date_Inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Capteur
-- ============================================================
CREATE TABLE Capteur (
    ID_Capteur                   SERIAL PRIMARY KEY,
    ID_Zone                      INTEGER REFERENCES Zone(ID_Zone) ON DELETE SET NULL,
    Type_Capteur                 VARCHAR(50)
                                 CHECK(Type_Capteur IN ('AIR_QUALITY','TEMPERATURE','HUMIDITY','NOISE','TRAFFIC','WATER_QUALITY')),
    Modele                       VARCHAR(100),
    Date_Installation            DATE,
    Statut                       VARCHAR(50) DEFAULT 'ACTIVE'
                                 CHECK(Statut IN ('ACTIVE','INACTIVE','MAINTENANCE','FAULTY')),
    etat_dfa                     VARCHAR(50) DEFAULT 'INACTIVE'
                                 CHECK(etat_dfa IN ('INACTIVE','ACTIVE','SIGNALED','MAINTENANCE','OUT_OF_SERVICE')),
    timestamp_derniere_transition TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Vehicule
-- ============================================================
CREATE TABLE Vehicule (
    ID_Vehicule    SERIAL PRIMARY KEY,
    Immatriculation VARCHAR(20) UNIQUE NOT NULL,
    Type_Vehicule  VARCHAR(50)
                   CHECK(Type_Vehicule IN ('AMBULANCE','POLICE','FIRE_TRUCK','GARBAGE','MAINTENANCE','BUS')),
    Modele         VARCHAR(100),
    Annee          INTEGER CHECK(Annee >= 1900 AND Annee <= 2100),
    Statut         VARCHAR(50) DEFAULT 'AVAILABLE'
                   CHECK(Statut IN ('AVAILABLE','IN_USE','MAINTENANCE','OUT_OF_SERVICE'))
);

-- ============================================================
-- TABLE: Trajet
-- ============================================================
CREATE TABLE Trajet (
    ID_Trajet                    SERIAL PRIMARY KEY,
    ID_Vehicule                  INTEGER REFERENCES Vehicule(ID_Vehicule) ON DELETE CASCADE,
    Point_Depart                 VARCHAR(200),
    Point_Arrivee                VARCHAR(200),
    Heure_Depart                 TIMESTAMP,
    Heure_Arrivee                TIMESTAMP,
    Distance                     DECIMAL(10,2),
    Statut                       VARCHAR(50) DEFAULT 'PLANNED'
                                 CHECK(Statut IN ('PLANNED','IN_PROGRESS','COMPLETED','CANCELLED')),
    etat_dfa                     VARCHAR(50) DEFAULT 'PARKED'
                                 CHECK(etat_dfa IN ('PARKED','EN_ROUTE','BROKEN_DOWN','ARRIVED')),
    timestamp_derniere_transition TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Technicien
-- ============================================================
CREATE TABLE Technicien (
    ID_Technicien     SERIAL PRIMARY KEY,
    Nom               VARCHAR(100) NOT NULL,
    Prenom            VARCHAR(100) NOT NULL,
    Email             VARCHAR(200) UNIQUE NOT NULL,
    Specialite        VARCHAR(100),
    Niveau_Experience INTEGER DEFAULT 1
                      CHECK(Niveau_Experience >= 1 AND Niveau_Experience <= 5),
    Disponible        BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- TABLE: Intervention
-- ============================================================
CREATE TABLE Intervention (
    ID_Intervention              SERIAL PRIMARY KEY,
    ID_Capteur                   INTEGER REFERENCES Capteur(ID_Capteur) ON DELETE SET NULL,
    ID_Zone                      INTEGER REFERENCES Zone(ID_Zone) ON DELETE SET NULL,
    Type_Intervention            VARCHAR(100),
    Description                  TEXT,
    Priorite                     VARCHAR(20) DEFAULT 'MEDIUM'
                                 CHECK(Priorite IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    Date_Demande                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Date_Completion              TIMESTAMP,
    Valide_IA                    BOOLEAN DEFAULT FALSE,
    etat_dfa                     VARCHAR(50) DEFAULT 'DEMAND'
                                 CHECK(etat_dfa IN ('DEMAND','TECH1_ASSIGNED','TECH2_VALIDATED','AI_VALIDATED','COMPLETED')),
    timestamp_derniere_transition TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: Affecte
-- ============================================================
CREATE TABLE Affecte (
    ID_Affecte        SERIAL PRIMARY KEY,
    ID_Intervention   INTEGER REFERENCES Intervention(ID_Intervention) ON DELETE CASCADE,
    ID_Technicien     INTEGER REFERENCES Technicien(ID_Technicien) ON DELETE CASCADE,
    Role_Technicien   VARCHAR(50) CHECK(Role_Technicien IN ('TECH1','TECH2','SUPERVISOR')),
    Date_Affectation  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ID_Intervention, ID_Technicien)
);

-- ============================================================
-- TABLE: Mesure_Capteur
-- ============================================================
CREATE TABLE Mesure_Capteur (
    ID_Mesure          SERIAL PRIMARY KEY,
    ID_Capteur         INTEGER REFERENCES Capteur(ID_Capteur) ON DELETE CASCADE,
    Valeur             DECIMAL(10,4) NOT NULL,
    Unite              VARCHAR(20),
    Timestamp_Mesure   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Qualite_Signal     DECIMAL(3,2) DEFAULT 1.0
                       CHECK(Qualite_Signal >= 0 AND Qualite_Signal <= 1)
);

-- ============================================================
-- TABLE: System_IA
-- ============================================================
CREATE TABLE System_IA (
    ID_Systeme       SERIAL PRIMARY KEY,
    Version          VARCHAR(50),
    Seuil_Confiance  DECIMAL(3,2) CHECK(Seuil_Confiance >= 0 AND Seuil_Confiance <= 1),
    Date_Maj         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Modele_Utilise   VARCHAR(100),
    Nb_Predictions   INTEGER DEFAULT 0
);

-- ============================================================
-- TABLE: Consultation
-- ============================================================
CREATE TABLE Consultation (
    ID_Consultation   SERIAL PRIMARY KEY,
    ID_Citoyen        INTEGER REFERENCES Citoyen(ID_Citoyen) ON DELETE SET NULL,
    ID_Systeme        INTEGER REFERENCES System_IA(ID_Systeme) ON DELETE SET NULL,
    Question          TEXT NOT NULL,
    Reponse           TEXT,
    Date_Consultation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Note_Satisfaction INTEGER CHECK(Note_Satisfaction >= 1 AND Note_Satisfaction <= 5)
);

-- ============================================================
-- VIEWS
-- ============================================================

CREATE OR REPLACE VIEW v_zones_pollution AS
    SELECT
        z.ID_Zone,
        z.Nom_Zone,
        z.Type_Zone,
        z.Indice_Pollution,
        a.Nom         AS Arrondissement,
        COUNT(c.ID_Capteur) AS Nb_Capteurs
    FROM Zone z
    LEFT JOIN Arrondissement a ON z.ID_Arrondissement = a.ID_Arrondissement
    LEFT JOIN Capteur c        ON c.ID_Zone = z.ID_Zone
    GROUP BY z.ID_Zone, z.Nom_Zone, z.Type_Zone, z.Indice_Pollution, a.Nom
    ORDER BY z.Indice_Pollution DESC;

CREATE OR REPLACE VIEW v_capteurs_actifs AS
    SELECT
        c.ID_Capteur,
        c.Type_Capteur,
        c.Modele,
        c.Statut,
        c.etat_dfa,
        z.Nom_Zone,
        a.Nom AS Arrondissement,
        c.timestamp_derniere_transition
    FROM Capteur c
    LEFT JOIN Zone z          ON c.ID_Zone = z.ID_Zone
    LEFT JOIN Arrondissement a ON z.ID_Arrondissement = a.ID_Arrondissement
    WHERE c.Statut = 'ACTIVE';

CREATE OR REPLACE VIEW v_interventions_en_cours AS
    SELECT
        i.ID_Intervention,
        i.Type_Intervention,
        i.Priorite,
        i.etat_dfa,
        i.Date_Demande,
        i.Valide_IA,
        z.Nom_Zone,
        c.Type_Capteur,
        COUNT(af.ID_Technicien) AS Nb_Techniciens
    FROM Intervention i
    LEFT JOIN Zone z    ON i.ID_Zone = z.ID_Zone
    LEFT JOIN Capteur c ON i.ID_Capteur = c.ID_Capteur
    LEFT JOIN Affecte af ON af.ID_Intervention = i.ID_Intervention
    WHERE i.etat_dfa NOT IN ('COMPLETED')
    GROUP BY i.ID_Intervention, i.Type_Intervention, i.Priorite,
             i.etat_dfa, i.Date_Demande, i.Valide_IA, z.Nom_Zone, c.Type_Capteur;

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_zone_arrondissement   ON Zone(ID_Arrondissement);
CREATE INDEX IF NOT EXISTS idx_zone_pollution        ON Zone(Indice_Pollution DESC);
CREATE INDEX IF NOT EXISTS idx_capteur_zone          ON Capteur(ID_Zone);
CREATE INDEX IF NOT EXISTS idx_capteur_statut        ON Capteur(Statut);
CREATE INDEX IF NOT EXISTS idx_capteur_etat_dfa      ON Capteur(etat_dfa);
CREATE INDEX IF NOT EXISTS idx_mesure_capteur        ON Mesure_Capteur(ID_Capteur);
CREATE INDEX IF NOT EXISTS idx_mesure_timestamp      ON Mesure_Capteur(Timestamp_Mesure DESC);
CREATE INDEX IF NOT EXISTS idx_intervention_zone     ON Intervention(ID_Zone);
CREATE INDEX IF NOT EXISTS idx_intervention_etat     ON Intervention(etat_dfa);
CREATE INDEX IF NOT EXISTS idx_intervention_priorite ON Intervention(Priorite);
CREATE INDEX IF NOT EXISTS idx_trajet_vehicule       ON Trajet(ID_Vehicule);
CREATE INDEX IF NOT EXISTS idx_affecte_intervention  ON Affecte(ID_Intervention);
CREATE INDEX IF NOT EXISTS idx_affecte_technicien    ON Affecte(ID_Technicien);
CREATE INDEX IF NOT EXISTS idx_consultation_citoyen  ON Consultation(ID_Citoyen);
