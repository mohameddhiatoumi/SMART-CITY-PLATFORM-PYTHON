"""
AST parser for the Smart City NL-to-SQL compiler.
Builds an Abstract Syntax Tree from a token list.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any

from compiler.lexer import Token, TokenType


# ---------------------------------------------------------------------------
# AST node hierarchy
# ---------------------------------------------------------------------------

@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    node_type: str = field(default="", init=False)

    def to_dict(self) -> dict:
        return {"node_type": self.node_type}


@dataclass
class LimitNode(ASTNode):
    """LIMIT N clause."""
    n: int

    def __post_init__(self) -> None:
        self.node_type = "LIMIT"

    def to_dict(self) -> dict:
        return {"node_type": self.node_type, "n": self.n}


@dataclass
class OrderNode(ASTNode):
    """ORDER BY clause."""
    column: str
    direction: str = "ASC"

    def __post_init__(self) -> None:
        self.node_type = "ORDER"

    def to_dict(self) -> dict:
        return {"node_type": self.node_type, "column": self.column, "direction": self.direction}


@dataclass
class FilterNode(ASTNode):
    """WHERE clause condition."""
    conditions: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.node_type = "FILTER"

    def to_dict(self) -> dict:
        return {"node_type": self.node_type, "conditions": self.conditions}


@dataclass
class SelectNode(ASTNode):
    """SELECT query."""
    entity: str
    table: str
    columns: List[str] = field(default_factory=lambda: ["*"])
    filter_node: Optional[FilterNode] = None
    order_node: Optional[OrderNode] = None
    limit_node: Optional[LimitNode] = None

    def __post_init__(self) -> None:
        self.node_type = "SELECT"

    def to_dict(self) -> dict:
        return {
            "node_type": self.node_type,
            "entity": self.entity,
            "table": self.table,
            "columns": self.columns,
            "filter": self.filter_node.to_dict() if self.filter_node else None,
            "order": self.order_node.to_dict() if self.order_node else None,
            "limit": self.limit_node.to_dict() if self.limit_node else None,
        }


@dataclass
class AggregationNode(ASTNode):
    """Aggregation query (COUNT, AVG, SUM, etc.)."""
    function: str
    entity: str
    table: str
    column: Optional[str] = None
    group_by: Optional[str] = None
    filter_node: Optional[FilterNode] = None

    def __post_init__(self) -> None:
        self.node_type = "AGGREGATION"

    def to_dict(self) -> dict:
        return {
            "node_type": self.node_type,
            "function": self.function,
            "entity": self.entity,
            "table": self.table,
            "column": self.column,
            "group_by": self.group_by,
            "filter": self.filter_node.to_dict() if self.filter_node else None,
        }


@dataclass
class QueryNode(ASTNode):
    """Root query node."""
    query_type: str
    child: Optional[ASTNode] = None

    def __post_init__(self) -> None:
        self.node_type = "QUERY"

    def to_dict(self) -> dict:
        return {
            "node_type": self.node_type,
            "query_type": self.query_type,
            "child": self.child.to_dict() if self.child else None,
        }


@dataclass
class JoinNode(ASTNode):
    """JOIN clause."""
    left_table: str
    right_table: str
    on_clause: str

    def __post_init__(self) -> None:
        self.node_type = "JOIN"

    def to_dict(self) -> dict:
        return {
            "node_type": self.node_type,
            "left_table": self.left_table,
            "right_table": self.right_table,
            "on": self.on_clause,
        }


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """
    Recursive-descent parser that converts a token list into an AST.

    Usage::
        from compiler.lexer import Lexer
        tokens = Lexer("Show 5 most polluted zones").tokenize()
        ast = Parser(tokens).parse()
    """

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self) -> QueryNode:
        """Entry point – returns root QueryNode."""
        return self.parse_query()

    # ------------------------------------------------------------------
    # Internal parse methods
    # ------------------------------------------------------------------

    def parse_query(self) -> QueryNode:
        """Determine and dispatch to specific query parser."""
        tok = self.current_token()

        if tok.type == TokenType.QUANTIFIER or (
            tok.type == TokenType.AGGREGATOR and tok.value.lower() in ("count",)
        ):
            child = self.parse_aggregation()
            return QueryNode(query_type="aggregation", child=child)

        if tok.type == TokenType.AGGREGATOR:
            child = self.parse_aggregation()
            return QueryNode(query_type="aggregation", child=child)

        if tok.type == TokenType.COMPARATOR:
            child = self.parse_select()
            return QueryNode(query_type="select", child=child)

        # Fallback: try to parse as select
        child = self.parse_select()
        return QueryNode(query_type="select", child=child)

    def parse_select(self) -> SelectNode:
        """Parse 'Show / List / Find' style queries."""
        from compiler.grammar import ENTITY_MAP, ADJECTIVE_MAP, ORDER_MAP, DATE_COLUMN_MAP

        # Consume comparator
        if self.current_token().type == TokenType.COMPARATOR:
            self.advance()

        limit_node: Optional[LimitNode] = None
        order_node: Optional[OrderNode] = None
        filter_node: Optional[FilterNode] = None
        entity_token: Optional[Token] = None
        adjective_value: Optional[str] = None

        # Consume optional "the"
        while self.current_token().type == TokenType.KEYWORD and self.current_token().value.lower() in ("the", "all", "a", "an"):
            self.advance()

        # Check for number (LIMIT)
        if self.current_token().type == TokenType.NUMBER:
            limit_node = self.parse_limit()

        # Skip "most" / "least" / "top" / "bottom"
        if self.current_token().type == TokenType.KEYWORD and self.current_token().value.lower() in ("most", "least", "top", "bottom"):
            direction = "DESC" if self.current_token().value.lower() in ("most", "top") else "ASC"
            self.advance()
        else:
            direction = "DESC"

        # Adjective
        if self.current_token().type == TokenType.ADJECTIVE:
            adjective_value = self.current_token().value.lower()
            self.advance()

        # Skip filler keywords
        while self.current_token().type == TokenType.KEYWORD and self.current_token().value.lower() in ("the", "all", "a", "an", "with", "of"):
            self.advance()

        # Entity
        if self.current_token().type == TokenType.ENTITY:
            entity_token = self.current_token()
            self.advance()
        elif self.current_token().type == TokenType.IDENTIFIER:
            entity_token = self.current_token()
            self.advance()

        entity_str = entity_token.value.lower() if entity_token else "capteur"
        table = ENTITY_MAP.get(entity_str, entity_str.capitalize())

        # Build filter from adjective
        conditions: List[str] = []
        if adjective_value:
            adj_conditions = ADJECTIVE_MAP.get(adjective_value, {})
            cond = adj_conditions.get(table, adj_conditions.get("_default", ""))
            if cond and "ORDER BY" not in cond:
                conditions.append(cond)

            # Set order from adjective
            if adjective_value in ORDER_MAP:
                col, _dir = ORDER_MAP[adjective_value]
                order_node = OrderNode(column=col, direction=direction if direction != "ASC" else _dir)
            elif adjective_value == "recent":
                date_col = DATE_COLUMN_MAP.get(table, "ID_" + table)
                order_node = OrderNode(column=date_col, direction="DESC")

        # Parse further filter/order after entity
        filter_node = self._parse_trailing_filter(table, conditions)

        if filter_node is None and conditions:
            filter_node = FilterNode(conditions=conditions)

        # Default order if none set
        if order_node is None and limit_node is not None:
            # Order by primary key descending for deterministic results
            order_node = OrderNode(column="1", direction="DESC")

        return SelectNode(
            entity=entity_str,
            table=table,
            filter_node=filter_node,
            order_node=order_node,
            limit_node=limit_node,
        )

    def parse_aggregation(self) -> AggregationNode:
        """Parse COUNT / AVG / SUM / HOW MANY queries."""
        from compiler.grammar import ENTITY_MAP, FIELD_MAP, ADJECTIVE_MAP

        func_name = "COUNT"
        column: Optional[str] = None
        group_by: Optional[str] = None
        filter_conditions: List[str] = []

        tok = self.current_token()

        # QUANTIFIER: "how many"
        if tok.type == TokenType.QUANTIFIER:
            func_name = "COUNT"
            self.advance()
        elif tok.type == TokenType.AGGREGATOR:
            func_map = {
                "count": "COUNT", "average": "AVG", "avg": "AVG",
                "sum": "SUM", "total": "SUM", "max": "MAX", "maximum": "MAX",
                "min": "MIN", "minimum": "MIN",
            }
            func_name = func_map.get(tok.value.lower(), "COUNT")
            self.advance()

        # Skip "the"
        while self.current_token().type == TokenType.KEYWORD and self.current_token().value.lower() in ("the", "all", "a", "an"):
            self.advance()

        # Field (for AVG/SUM)
        if func_name in ("AVG", "SUM", "MAX", "MIN") and self.current_token().type == TokenType.FIELD:
            self.advance()
            # "of / for" → entity
            while self.current_token().type == TokenType.KEYWORD and self.current_token().value.lower() in ("of", "for", "in", "from"):
                self.advance()

        # Entity
        entity_token: Optional[Token] = None
        if self.current_token().type == TokenType.ENTITY:
            entity_token = self.current_token()
            self.advance()
        elif self.current_token().type == TokenType.IDENTIFIER:
            entity_token = self.current_token()
            self.advance()

        entity_str = entity_token.value.lower() if entity_token else "capteur"
        table = ENTITY_MAP.get(entity_str, entity_str.capitalize())

        # Check for "by <field>" → GROUP BY
        while self.current_token().type == TokenType.KEYWORD and self.current_token().value.lower() in ("are", "is", "have", "by", "with", "per"):
            keyword = self.current_token().value.lower()
            self.advance()
            if keyword == "by" and self.current_token().type in (TokenType.FIELD, TokenType.IDENTIFIER):
                field_tok = self.current_token()
                self.advance()
                # Map field name to column
                fmap = FIELD_MAP.get(table, {})
                group_by = fmap.get(field_tok.value.lower(), field_tok.value)
                break

        # Adjective → WHERE condition
        if self.current_token().type == TokenType.ADJECTIVE:
            adj = self.current_token().value.lower()
            self.advance()
            adj_conds = ADJECTIVE_MAP.get(adj, {})
            cond = adj_conds.get(table, adj_conds.get("_default", ""))
            if cond:
                filter_conditions.append(cond)

        # For AVG – determine column
        if func_name in ("AVG", "SUM", "MAX", "MIN"):
            fmap = FIELD_MAP.get(table, {})
            # Try to infer from what we already saw
            if "score" in self.original_query().lower() or "ecological" in self.original_query().lower():
                column = fmap.get("score", fmap.get("score_ecologique", "*"))
            elif "pollution" in self.original_query().lower():
                column = fmap.get("pollution", fmap.get("indice_pollution", "*"))
            else:
                # Default to first numeric column
                column = next(iter(fmap.values()), "*")

        filter_node = FilterNode(conditions=filter_conditions) if filter_conditions else None

        return AggregationNode(
            function=func_name,
            entity=entity_str,
            table=table,
            column=column,
            group_by=group_by,
            filter_node=filter_node,
        )

    def parse_limit(self) -> LimitNode:
        """Parse NUMBER token into LimitNode."""
        try:
            n = int(float(self.current_token().value))
        except ValueError:
            n = 10
        self.advance()
        return LimitNode(n=n)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _parse_trailing_filter(self, table: str, existing_conditions: List[str]) -> Optional[FilterNode]:
        """Parse any trailing WHERE conditions (field operator value)."""
        from compiler.grammar import FIELD_MAP, OPERATOR_MAP, ADJECTIVE_MAP

        conditions = list(existing_conditions)

        while self.current_token().type != TokenType.EOF:
            tok = self.current_token()

            # "with / where / having" keyword
            if tok.type == TokenType.KEYWORD and tok.value.lower() in ("with", "where", "having", "that", "which"):
                self.advance()
                continue

            # field operator value
            if tok.type == TokenType.FIELD:
                field_val = tok.value.lower()
                self.advance()
                fmap = FIELD_MAP.get(table, {})
                column = fmap.get(field_val, field_val)

                if self.current_token().type == TokenType.OPERATOR:
                    op_raw = self.current_token().value.lower()
                    op = OPERATOR_MAP.get(op_raw, op_raw)
                    self.advance()

                    if self.current_token().type == TokenType.NUMBER:
                        val = self.current_token().value
                        self.advance()
                        conditions.append(f"{column} {op} {val}")
                    elif self.current_token().type == TokenType.STRING:
                        val = self.current_token().value
                        self.advance()
                        conditions.append(f"{column} {op} {val}")
                    elif self.current_token().type in (TokenType.ADJECTIVE, TokenType.IDENTIFIER):
                        val = self.current_token().value
                        self.advance()
                        conditions.append(f"{column} {op} '{val}'")
                continue

            # adjective after entity
            if tok.type == TokenType.ADJECTIVE:
                adj = tok.value.lower()
                self.advance()
                adj_conds = ADJECTIVE_MAP.get(adj, {})
                cond = adj_conds.get(table, adj_conds.get("_default", ""))
                if cond and "ORDER BY" not in cond:
                    conditions.append(cond)
                continue

            # operator directly (e.g. "> 80")
            if tok.type == TokenType.OPERATOR:
                op_raw = tok.value.lower()
                op = OPERATOR_MAP.get(op_raw, op_raw)
                self.advance()
                if self.current_token().type == TokenType.NUMBER:
                    val = self.current_token().value
                    self.advance()
                    # Use last seen field if any
                    conditions.append(f"Score_Ecologique {op} {val}")
                continue

            # NUMBER alone (likely value)
            if tok.type == TokenType.NUMBER and conditions:
                self.advance()
                continue

            self.advance()

        return FilterNode(conditions=conditions) if conditions else None

    def current_token(self) -> Token:
        """Return the current token without advancing."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, "", -1)

    def advance(self) -> Token:
        """Advance to the next token and return the previous one."""
        tok = self.current_token()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def peek(self, offset: int = 1) -> Token:
        """Look ahead by offset tokens."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token(TokenType.EOF, "", -1)

    def expect(self, token_type: TokenType) -> Token:
        """Assert current token is of given type, then advance."""
        tok = self.current_token()
        if tok.type != token_type:
            raise SyntaxError(f"Expected {token_type.name}, got {tok.type.name} ({tok.value!r}) at pos {tok.position}")
        return self.advance()

    def original_query(self) -> str:
        """Reconstruct original query from tokens for context-sensitive lookups."""
        return " ".join(t.value for t in self.tokens if t.type != TokenType.EOF)
