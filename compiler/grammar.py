"""
Grammar definitions for the Smart City NL-to-SQL compiler.
Defines token patterns, query patterns, and mapping tables.
"""
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Token patterns (ordered – first match wins)
# ---------------------------------------------------------------------------
TOKEN_PATTERNS: List[Tuple[str, str]] = [
    # Multi-word operators (must come before single-word)
    ("OPERATOR", r"(?i)\b(greater than or equal to|less than or equal to|greater than|less than|equal to|not equal to|more than|at least|at most|at most|no more than|no less than)\b"),
    # Aggregators
    ("AGGREGATOR", r"(?i)\b(count|average|avg|sum|total|max|maximum|min|minimum)\b"),
    # Comparators (query starters)
    ("COMPARATOR", r"(?i)\b(show|list|find|display|get|fetch|retrieve|which|what|who)\b"),
    ("QUANTIFIER", r"(?i)\b(how many|how much)\b"),
    # Keywords
    ("KEYWORD", r"(?i)\b(the|most|least|top|bottom|all|any|each|every|of|in|by|with|from|where|having|order|group|limit|between|and|or|not|is|are|have|has|been|be)\b"),
    # Adjectives
    ("ADJECTIVE", r"(?i)\b(polluted|clean|active|inactive|available|unavailable|busy|idle|critical|high|medium|low|completed|pending|validated|assigned|faulty|broken|new|recent|old|latest)\b"),
    # Entities
    ("ENTITY", r"(?i)\b(sensors?|capteurs?|zones?|interventions?|vehicles?|vehicules?|citizens?|citoyens?|technicians?|techniciens?|measurements?|mesures?|consultations?|arrondissements?|districts?|trajets?|routes?)\b"),
    # Fields
    ("FIELD", r"(?i)\b(pollution|indice_pollution|score|score_ecologique|ecological score|type|status|statut|priority|priorite|date|timestamp|value|valeur|quality|qualite|level|niveau|model|modele|name|nom|zone|arrondissement|email|telephone|specialite|specialty)\b"),
    # Locations
    ("LOCATION", r"(?i)\b(sousse|hammam sousse|akouda|kalaa kebira|msaken|medina|corniche|zone industrielle|zone commerciale)\b"),
    # Numbers
    ("NUMBER", r"\b\d+(\.\d+)?\b"),
    # Comparison operators
    ("OPERATOR", r"(>=|<=|!=|>|<|=)"),
    # Quoted strings
    ("STRING", r"'[^']*'|\"[^\"]*\""),
    # Identifiers (catch-all for words)
    ("IDENTIFIER", r"[a-zA-Z_àâäéèêëîïôùûü][a-zA-Z0-9_àâäéèêëîïôùûü]*"),
    # Punctuation
    ("PUNCTUATION", r"[,;:\(\)\[\]]"),
]

# ---------------------------------------------------------------------------
# Formal grammar rules (context-free grammar notation)
# ---------------------------------------------------------------------------
GRAMMAR: Dict[str, List[str]] = {
    "query": [
        "show_query",
        "list_query",
        "count_query",
        "average_query",
        "group_query",
        "filter_query",
    ],
    "show_query": [
        "COMPARATOR NUMBER ADJECTIVE? ENTITY filter_clause? order_clause? limit_clause?",
        "COMPARATOR KEYWORD? ADJECTIVE? ENTITY filter_clause? order_clause? limit_clause?",
    ],
    "list_query": [
        "COMPARATOR KEYWORD? ADJECTIVE? ENTITY location_clause?",
        "COMPARATOR KEYWORD? ENTITY ADJECTIVE?",
    ],
    "count_query": [
        "QUANTIFIER ENTITY ADJECTIVE?",
        "AGGREGATOR ENTITY KEYWORD? FIELD",
    ],
    "average_query": [
        "AGGREGATOR FIELD KEYWORD? ENTITY",
    ],
    "group_query": [
        "AGGREGATOR ENTITY KEYWORD? FIELD",
    ],
    "filter_clause": [
        "KEYWORD? FIELD OPERATOR NUMBER",
        "KEYWORD? FIELD OPERATOR STRING",
        "KEYWORD? ADJECTIVE",
    ],
    "order_clause": [
        "KEYWORD FIELD (KEYWORD)?",
    ],
    "limit_clause": [
        "KEYWORD NUMBER",
    ],
    "location_clause": [
        "KEYWORD LOCATION",
    ],
}

# ---------------------------------------------------------------------------
# Query patterns – (description, regex, sql_template)
# ---------------------------------------------------------------------------
QUERY_PATTERNS: List[Dict] = [
    {
        "name": "show_top_n_most_adjective_entity",
        "description": 'Show the N most/least [adjective] [entity]',
        "regex": r"(?i)(?:show|display|get|list)\s+(?:the\s+)?(\d+)\s+(?:most|least|top|bottom)\s+(\w+)\s+(\w+s?)",
        "template": "SELECT * FROM {table} ORDER BY {order_col} {order_dir} LIMIT {n}",
    },
    {
        "name": "filter_numeric",
        "description": 'Which [entity] have [field] [operator] [value]',
        "regex": r"(?i)(?:which|what|find|show)\s+(\w+s?)\s+(?:have|has|with|where)?\s+(\w+(?:\s+\w+)?)\s+(>|<|=|>=|<=|greater than|less than|equal to|more than)\s*(\d+(?:\.\d+)?)",
        "template": "SELECT * FROM {table} WHERE {column} {operator} {value}",
    },
    {
        "name": "list_adjective_entity",
        "description": 'List all [adjective] [entity]',
        "regex": r"(?i)(?:list|show|display|get)\s+(?:all\s+)?(\w+)\s+(\w+s?)",
        "template": "SELECT * FROM {table} WHERE {condition}",
    },
    {
        "name": "count_entity_adjective",
        "description": 'How many [entity] are [adjective]',
        "regex": r"(?i)how\s+many\s+(\w+s?)\s+(?:are|is|have been|were)\s+(\w+)",
        "template": "SELECT COUNT(*) FROM {table} WHERE {condition}",
    },
    {
        "name": "count_by_field",
        "description": 'Count [entity] by [field]',
        "regex": r"(?i)(?:count|group)\s+(\w+s?)\s+by\s+(\w+)",
        "template": "SELECT {group_col}, COUNT(*) AS total FROM {table} GROUP BY {group_col} ORDER BY total DESC",
    },
    {
        "name": "average_field",
        "description": 'Average [field] of [entity]',
        "regex": r"(?i)(?:average|avg)\s+(\w+(?:\s+\w+)?)\s+(?:of|for|in)?\s+(\w+s?)",
        "template": "SELECT AVG({column}) AS average_{col_name} FROM {table}",
    },
    {
        "name": "show_recent",
        "description": 'Show the N most recent [entity]',
        "regex": r"(?i)(?:show|list|display)\s+(?:the\s+)?(\d+)\s+most\s+recent\s+(\w+s?)",
        "template": "SELECT * FROM {table} ORDER BY {date_col} DESC LIMIT {n}",
    },
    {
        "name": "entity_in_location",
        "description": 'List [entity] in [location]',
        "regex": r"(?i)(?:list|show|find)\s+(?:all\s+)?(\w+s?)\s+in\s+(.+)",
        "template": "SELECT {table}.* FROM {table} JOIN Zone ON {table}.ID_Zone = Zone.ID_Zone WHERE Zone.Nom_Zone ILIKE '%{location}%'",
    },
]

# ---------------------------------------------------------------------------
# Entity → table mapping
# ---------------------------------------------------------------------------
ENTITY_MAP: Dict[str, str] = {
    # English
    "sensor": "Capteur",
    "sensors": "Capteur",
    "zone": "Zone",
    "zones": "Zone",
    "intervention": "Intervention",
    "interventions": "Intervention",
    "vehicle": "Vehicule",
    "vehicles": "Vehicule",
    "citizen": "Citoyen",
    "citizens": "Citoyen",
    "technician": "Technicien",
    "technicians": "Technicien",
    "measurement": "Mesure_Capteur",
    "measurements": "Mesure_Capteur",
    "reading": "Mesure_Capteur",
    "readings": "Mesure_Capteur",
    "consultation": "Consultation",
    "consultations": "Consultation",
    "route": "Trajet",
    "routes": "Trajet",
    "trajectory": "Trajet",
    "trajectories": "Trajet",
    "district": "Arrondissement",
    "districts": "Arrondissement",
    "arrondissement": "Arrondissement",
    "arrondissements": "Arrondissement",
    # French
    "capteur": "Capteur",
    "capteurs": "Capteur",
    "vehicule": "Vehicule",
    "vehicules": "Vehicule",
    "citoyen": "Citoyen",
    "citoyens": "Citoyen",
    "technicien": "Technicien",
    "techniciens": "Technicien",
    "mesure": "Mesure_Capteur",
    "mesures": "Mesure_Capteur",
    "trajet": "Trajet",
    "trajets": "Trajet",
}

# ---------------------------------------------------------------------------
# Field → column mapping  {entity: {field: column}}
# ---------------------------------------------------------------------------
FIELD_MAP: Dict[str, Dict[str, str]] = {
    "Capteur": {
        "type": "Type_Capteur",
        "status": "Statut",
        "statut": "Statut",
        "model": "Modele",
        "modele": "Modele",
        "state": "etat_dfa",
        "etat": "etat_dfa",
        "zone": "ID_Zone",
        "date": "Date_Installation",
    },
    "Zone": {
        "pollution": "Indice_Pollution",
        "indice_pollution": "Indice_Pollution",
        "type": "Type_Zone",
        "name": "Nom_Zone",
        "nom": "Nom_Zone",
        "coordinates": "Coordonnees_GPS",
    },
    "Citoyen": {
        "score": "Score_Ecologique",
        "ecological score": "Score_Ecologique",
        "score_ecologique": "Score_Ecologique",
        "name": "Nom",
        "nom": "Nom",
        "email": "Email",
        "phone": "Telephone",
        "address": "Adresse",
        "date": "Date_Inscription",
    },
    "Intervention": {
        "type": "Type_Intervention",
        "priority": "Priorite",
        "priorite": "Priorite",
        "status": "etat_dfa",
        "state": "etat_dfa",
        "date": "Date_Demande",
        "validated": "Valide_IA",
        "ai_validated": "Valide_IA",
    },
    "Vehicule": {
        "type": "Type_Vehicule",
        "status": "Statut",
        "model": "Modele",
        "year": "Annee",
        "plate": "Immatriculation",
    },
    "Technicien": {
        "specialty": "Specialite",
        "specialite": "Specialite",
        "level": "Niveau_Experience",
        "niveau": "Niveau_Experience",
        "available": "Disponible",
        "disponible": "Disponible",
        "name": "Nom",
    },
    "Mesure_Capteur": {
        "value": "Valeur",
        "valeur": "Valeur",
        "unit": "Unite",
        "quality": "Qualite_Signal",
        "date": "Timestamp_Mesure",
        "timestamp": "Timestamp_Mesure",
    },
    "Trajet": {
        "status": "Statut",
        "state": "etat_dfa",
        "distance": "Distance",
        "departure": "Point_Depart",
        "arrival": "Point_Arrivee",
        "date": "Heure_Depart",
    },
}

# Date column per entity (used for "most recent" queries)
DATE_COLUMN_MAP: Dict[str, str] = {
    "Capteur": "Date_Installation",
    "Zone": "ID_Zone",
    "Citoyen": "Date_Inscription",
    "Intervention": "Date_Demande",
    "Vehicule": "ID_Vehicule",
    "Mesure_Capteur": "Timestamp_Mesure",
    "Trajet": "Heure_Depart",
    "Consultation": "Date_Consultation",
    "Technicien": "ID_Technicien",
    "Arrondissement": "ID_Arrondissement",
}

# ---------------------------------------------------------------------------
# Adjective → WHERE condition mapping
# ---------------------------------------------------------------------------
ADJECTIVE_MAP: Dict[str, Dict[str, str]] = {
    # Generic
    "active":     {"Capteur": "Statut = 'ACTIVE'",      "Vehicule": "Statut = 'AVAILABLE'", "_default": "Statut = 'ACTIVE'"},
    "inactive":   {"Capteur": "Statut = 'INACTIVE'",    "_default": "Statut = 'INACTIVE'"},
    "available":  {"Vehicule": "Statut = 'AVAILABLE'",  "Technicien": "Disponible = TRUE", "_default": "Statut = 'AVAILABLE'"},
    "unavailable":{"Technicien": "Disponible = FALSE",  "_default": "Statut != 'AVAILABLE'"},
    "critical":   {"Intervention": "Priorite = 'CRITICAL'", "_default": "Priorite = 'CRITICAL'"},
    "high":       {"Intervention": "Priorite = 'HIGH'", "_default": "Priorite = 'HIGH'"},
    "medium":     {"Intervention": "Priorite = 'MEDIUM'","_default": "Priorite = 'MEDIUM'"},
    "low":        {"Intervention": "Priorite = 'LOW'",  "_default": "Priorite = 'LOW'"},
    "completed":  {"Intervention": "etat_dfa = 'COMPLETED'", "Trajet": "Statut = 'COMPLETED'", "_default": "Statut = 'COMPLETED'"},
    "pending":    {"Intervention": "etat_dfa = 'DEMAND'", "_default": "etat_dfa = 'DEMAND'"},
    "validated":  {"Intervention": "Valide_IA = TRUE",  "_default": "Valide_IA = TRUE"},
    "ai validated":{"Intervention": "Valide_IA = TRUE", "_default": "Valide_IA = TRUE"},
    "assigned":   {"Intervention": "etat_dfa = 'TECH1_ASSIGNED'", "_default": "etat_dfa = 'TECH1_ASSIGNED'"},
    "faulty":     {"Capteur": "Statut = 'FAULTY'",      "_default": "Statut = 'FAULTY'"},
    "polluted":   {"Zone": "Indice_Pollution > 50",     "_default": "Indice_Pollution > 50"},
    "clean":      {"Zone": "Indice_Pollution < 20",     "_default": "Indice_Pollution < 20"},
    "recent":     {"_default": "1=1 ORDER BY ID DESC"},
    "maintenance":{"Capteur": "Statut = 'MAINTENANCE'", "Vehicule": "Statut = 'MAINTENANCE'", "_default": "Statut = 'MAINTENANCE'"},
}

# ---------------------------------------------------------------------------
# Adjective → ORDER BY mapping (for "most X")
# ---------------------------------------------------------------------------
ORDER_MAP: Dict[str, Tuple[str, str]] = {
    "polluted":  ("Indice_Pollution", "DESC"),
    "clean":     ("Indice_Pollution", "ASC"),
    "recent":    ("Timestamp_Mesure", "DESC"),
    "active":    ("ID_Capteur", "ASC"),
    "critical":  ("Priorite", "DESC"),
    "high":      ("Priorite", "DESC"),
    "old":       ("Date_Installation", "ASC"),
    "new":       ("Date_Installation", "DESC"),
    "latest":    ("Timestamp_Mesure", "DESC"),
    "score":     ("Score_Ecologique", "DESC"),
}

# ---------------------------------------------------------------------------
# Operator mapping
# ---------------------------------------------------------------------------
OPERATOR_MAP: Dict[str, str] = {
    "greater than or equal to": ">=",
    "less than or equal to": "<=",
    "greater than": ">",
    "less than": "<",
    "equal to": "=",
    "not equal to": "!=",
    "more than": ">",
    "at least": ">=",
    "at most": "<=",
    "no more than": "<=",
    "no less than": ">=",
    ">": ">",
    "<": "<",
    "=": "=",
    ">=": ">=",
    "<=": "<=",
    "!=": "!=",
}
