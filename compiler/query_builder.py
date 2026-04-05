"""
High-level query builder combining Lexer → Parser → Generator.
"""
from __future__ import annotations
from typing import Optional

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.generator import CodeGenerator


class QueryBuilder:
    """
    Converts natural language queries to SQL.

    Usage::
        builder = QueryBuilder()
        result = builder.build("Show the 5 most polluted zones")
        print(result['sql'])
    """

    def __init__(self) -> None:
        self.lexer_class = Lexer
        self.parser_class = Parser
        self.generator = CodeGenerator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self, natural_language_query: str) -> dict:
        """
        Main entry point.

        Returns::
            {
                'sql': str,
                'tokens': list[dict],
                'ast': dict,
                'success': bool,
                'error': str | None,
            }
        """
        try:
            sql = self.parse_and_generate(natural_language_query)
            lexer = self.lexer_class(natural_language_query)
            tokens = [t.to_dict() for t in lexer.tokenize()]
            parser = self.parser_class(self.lexer_class(natural_language_query).tokenize())
            ast = parser.parse()
            return {
                "sql": sql,
                "tokens": tokens,
                "ast": ast.to_dict(),
                "success": True,
                "error": None,
            }
        except Exception as exc:
            return {
                "sql": "",
                "tokens": [],
                "ast": {},
                "success": False,
                "error": str(exc),
            }

    def parse_and_generate(self, query: str) -> str:
        """Lex → parse → generate SQL."""
        lexer = self.lexer_class(query)
        tokens = lexer.tokenize()
        parser = self.parser_class(tokens)
        ast = parser.parse()
        sql = self.generator.generate(ast)
        return sql

    def get_examples(self) -> list[dict]:
        """Return example queries with expected SQL for documentation/testing."""
        return [
            {
                "query": "Show the 5 most polluted zones",
                "expected_sql": "SELECT * FROM Zone ORDER BY Indice_Pollution DESC LIMIT 5",
                "description": "Top N ordered by pollution index",
            },
            {
                "query": "Which citizens have an ecological score greater than 80",
                "expected_sql": "SELECT * FROM Citoyen WHERE Score_Ecologique > 80",
                "description": "Filter with numeric comparison",
            },
            {
                "query": "List all active sensors",
                "expected_sql": "SELECT * FROM Capteur WHERE Statut = 'ACTIVE'",
                "description": "Filter by status adjective",
            },
            {
                "query": "How many interventions are AI validated",
                "expected_sql": "SELECT COUNT(*) AS total FROM Intervention WHERE Valide_IA = TRUE",
                "description": "COUNT with condition",
            },
            {
                "query": "Count sensors by type",
                "expected_sql": "SELECT Type_Capteur, COUNT(*) AS total FROM Capteur GROUP BY Type_Capteur ORDER BY total DESC",
                "description": "GROUP BY aggregation",
            },
            {
                "query": "Show interventions with high priority",
                "expected_sql": "SELECT * FROM Intervention WHERE Priorite = 'HIGH'",
                "description": "Filter by priority adjective",
            },
            {
                "query": "List technicians available",
                "expected_sql": "SELECT * FROM Technicien WHERE Disponible = TRUE",
                "description": "Filter available technicians",
            },
            {
                "query": "Average ecological score of citizens",
                "expected_sql": "SELECT AVG(Score_Ecologique) AS result FROM Citoyen",
                "description": "Average aggregation",
            },
            {
                "query": "Show the 10 most recent sensor readings",
                "expected_sql": "SELECT * FROM Mesure_Capteur ORDER BY Timestamp_Mesure DESC LIMIT 10",
                "description": "Top N most recent records",
            },
            {
                "query": "List all faulty sensors",
                "expected_sql": "SELECT * FROM Capteur WHERE Statut = 'FAULTY'",
                "description": "Filter by faulty status",
            },
            {
                "query": "How many vehicles are available",
                "expected_sql": "SELECT COUNT(*) AS total FROM Vehicule WHERE Statut = 'AVAILABLE'",
                "description": "Count with adjective filter",
            },
            {
                "query": "Show critical interventions",
                "expected_sql": "SELECT * FROM Intervention WHERE Priorite = 'CRITICAL'",
                "description": "Critical priority filter",
            },
        ]
