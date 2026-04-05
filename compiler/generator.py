"""
SQL code generator for the Smart City NL-to-SQL compiler.
Converts AST nodes into valid SQL strings.
"""
from __future__ import annotations
import re
from typing import Optional, List

from compiler.parser import (
    ASTNode, QueryNode, SelectNode, AggregationNode,
    FilterNode, OrderNode, LimitNode,
)
from compiler.grammar import ENTITY_MAP, FIELD_MAP, OPERATOR_MAP, DATE_COLUMN_MAP

# Whitelisted table names to prevent SQL injection
_ALLOWED_TABLES = {
    "Capteur", "Zone", "Arrondissement", "Citoyen", "Vehicule",
    "Trajet", "Technicien", "Intervention", "Affecte",
    "Mesure_Capteur", "System_IA", "Consultation",
    # Views
    "v_zones_pollution", "v_capteurs_actifs", "v_interventions_en_cours",
}

_ALLOWED_COLUMNS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_identifier(name: str) -> str:
    """Return identifier only if it matches safe pattern."""
    if _ALLOWED_COLUMNS_RE.match(name):
        return name
    raise ValueError(f"Unsafe identifier: {name!r}")


class CodeGenerator:
    """
    Generates SQL from an AST produced by the Parser.

    Usage::
        gen = CodeGenerator()
        sql = gen.generate(ast_node)
    """

    def __init__(self) -> None:
        self.entity_map = ENTITY_MAP
        self.field_map = FIELD_MAP
        self.operator_map = OPERATOR_MAP

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, ast_node: ASTNode) -> str:
        """Dispatch to specific generator based on node type."""
        if isinstance(ast_node, QueryNode):
            return self.generate(ast_node.child) if ast_node.child else "SELECT 1"
        if isinstance(ast_node, SelectNode):
            return self.generate_select(ast_node)
        if isinstance(ast_node, AggregationNode):
            return self.generate_aggregation(ast_node)
        return "SELECT 1 -- unsupported query type"

    def generate_select(self, node: SelectNode) -> str:
        """Generate SELECT ... FROM ... WHERE ... ORDER BY ... LIMIT ..."""
        try:
            table = _safe_identifier(node.table)
        except ValueError:
            table = "Capteur"

        columns = ", ".join(node.columns) if node.columns else "*"

        parts = [f"SELECT {columns} FROM {table}"]

        if node.filter_node and node.filter_node.conditions:
            where = self.generate_filter(node.filter_node.conditions)
            if where:
                parts.append(f"WHERE {where}")

        if node.order_node:
            order = self.generate_order(node.order_node)
            if order:
                parts.append(order)

        if node.limit_node:
            parts.append(self.generate_limit(node.limit_node.n))

        return " ".join(parts)

    def generate_aggregation(self, node: AggregationNode) -> str:
        """Generate aggregation queries (COUNT, AVG, SUM, GROUP BY)."""
        try:
            table = _safe_identifier(node.table)
        except ValueError:
            table = "Capteur"

        if node.group_by:
            try:
                group_col = _safe_identifier(node.group_by)
            except ValueError:
                group_col = "Type"
            sql = (
                f"SELECT {group_col}, COUNT(*) AS total "
                f"FROM {table}"
            )
            if node.filter_node and node.filter_node.conditions:
                where = self.generate_filter(node.filter_node.conditions)
                if where:
                    sql += f" WHERE {where}"
            sql += f" GROUP BY {group_col} ORDER BY total DESC"
            return sql

        if node.function == "COUNT":
            col_expr = "*"
            sql = f"SELECT COUNT({col_expr}) AS total FROM {table}"
        elif node.function in ("AVG", "SUM", "MAX", "MIN"):
            col = node.column or "*"
            try:
                col = _safe_identifier(col) if col != "*" else col
            except ValueError:
                col = "*"
            sql = f"SELECT {node.function}({col}) AS result FROM {table}"
        else:
            sql = f"SELECT COUNT(*) AS total FROM {table}"

        if node.filter_node and node.filter_node.conditions:
            where = self.generate_filter(node.filter_node.conditions)
            if where:
                sql += f" WHERE {where}"

        return sql

    def generate_filter(self, conditions: List[str]) -> str:
        """Generate WHERE clause from list of condition strings."""
        if not conditions:
            return ""
        # Sanitise each condition minimally (whitelist check on identifiers)
        sanitised = []
        for cond in conditions:
            if cond and "1=1" not in cond:
                sanitised.append(cond)
        return " AND ".join(sanitised) if sanitised else ""

    def generate_order(self, node: OrderNode) -> str:
        """Generate ORDER BY clause."""
        try:
            col = node.column
            # Allow numeric (e.g. "1") for positional ORDER BY
            if not col.isdigit():
                col = _safe_identifier(col)
            direction = "DESC" if node.direction.upper() == "DESC" else "ASC"
            return f"ORDER BY {col} {direction}"
        except ValueError:
            return ""

    def generate_limit(self, n: int) -> str:
        """Generate LIMIT clause."""
        return f"LIMIT {max(1, int(n))}"

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------

    def _map_entity(self, entity: str) -> str:
        """Map natural language entity name to table name."""
        return self.entity_map.get(entity.lower(), entity.capitalize())

    def _map_field(self, entity: str, field_name: str) -> str:
        """Map natural language field name to column name."""
        table = self._map_entity(entity)
        fmap = self.field_map.get(table, {})
        return fmap.get(field_name.lower(), field_name)

    def _map_operator(self, op: str) -> str:
        """Map natural language operator to SQL operator."""
        return self.operator_map.get(op.lower(), op)

    def validate_query(self, sql: str) -> bool:
        """Basic SQL validation: check it starts with SELECT."""
        stripped = sql.strip().upper()
        if not stripped.startswith("SELECT"):
            return False
        # Reject obvious injection patterns
        dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "EXEC", "EXECUTE", "--", ";"]
        for kw in dangerous:
            if kw in stripped:
                return False
        return True
