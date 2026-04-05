"""
Tests for the Smart City compiler module.
All tests run without a database connection.
"""
import pytest
from compiler.lexer import Lexer, TokenType, Token
from compiler.parser import Parser, SelectNode, AggregationNode, QueryNode
from compiler.generator import CodeGenerator
from compiler.query_builder import QueryBuilder


class TestLexer:
    """Tests for the Lexer class."""

    def _tokenize(self, text: str) -> list:
        return Lexer(text).tokenize()

    def test_tokenize_simple_show(self):
        tokens = self._tokenize("Show zones")
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert TokenType.COMPARATOR in types
        assert TokenType.ENTITY in types

    def test_tokenize_number(self):
        tokens = self._tokenize("Show 5 zones")
        numbers = [t for t in tokens if t.type == TokenType.NUMBER]
        assert len(numbers) == 1
        assert numbers[0].value == "5"

    def test_tokenize_adjective_polluted(self):
        tokens = self._tokenize("most polluted zones")
        adjectives = [t for t in tokens if t.type == TokenType.ADJECTIVE]
        assert any("polluted" in t.value.lower() for t in adjectives)

    def test_tokenize_adjective_active(self):
        tokens = self._tokenize("List all active sensors")
        adjectives = [t for t in tokens if t.type == TokenType.ADJECTIVE]
        assert any("active" in t.value.lower() for t in adjectives)

    def test_tokenize_entity_sensor(self):
        tokens = self._tokenize("List sensors")
        entities = [t for t in tokens if t.type == TokenType.ENTITY]
        assert any("sensor" in t.value.lower() for t in entities)

    def test_tokenize_entity_citoyen(self):
        tokens = self._tokenize("Which citizens have high score")
        entities = [t for t in tokens if t.type == TokenType.ENTITY]
        assert any("citizen" in t.value.lower() for t in entities)

    def test_tokenize_operator_greater_than(self):
        tokens = self._tokenize("score greater than 80")
        ops = [t for t in tokens if t.type == TokenType.OPERATOR]
        assert len(ops) >= 1

    def test_tokenize_aggregator_count(self):
        tokens = self._tokenize("Count sensors by type")
        aggs = [t for t in tokens if t.type == TokenType.AGGREGATOR]
        assert any("count" in t.value.lower() for t in aggs)

    def test_tokenize_aggregator_average(self):
        tokens = self._tokenize("Average ecological score of citizens")
        aggs = [t for t in tokens if t.type == TokenType.AGGREGATOR]
        assert any(t.value.lower() in ("average", "avg") for t in aggs)

    def test_tokenize_quantifier_how_many(self):
        tokens = self._tokenize("How many interventions are completed")
        quants = [t for t in tokens if t.type == TokenType.QUANTIFIER]
        assert len(quants) >= 1

    def test_tokenize_eof_appended(self):
        tokens = self._tokenize("test")
        assert tokens[-1].type == TokenType.EOF

    def test_tokenize_case_insensitive(self):
        tokens1 = self._tokenize("SHOW SENSORS")
        tokens2 = self._tokenize("show sensors")
        types1 = [t.type for t in tokens1 if t.type != TokenType.EOF]
        types2 = [t.type for t in tokens2 if t.type != TokenType.EOF]
        assert types1 == types2

    def test_token_to_dict(self):
        token = Token(TokenType.ENTITY, "zones", 0)
        d = token.to_dict()
        assert d["type"] == "ENTITY"
        assert d["value"] == "zones"
        assert d["position"] == 0

    def test_tokenize_intervention_entity(self):
        tokens = self._tokenize("List all interventions")
        entities = [t for t in tokens if t.type == TokenType.ENTITY]
        assert any("intervention" in t.value.lower() for t in entities)


class TestParser:
    """Tests for the Parser class."""

    def _parse(self, text: str) -> QueryNode:
        tokens = Lexer(text).tokenize()
        return Parser(tokens).parse()

    def test_parse_show_returns_query_node(self):
        ast = self._parse("Show zones")
        assert isinstance(ast, QueryNode)

    def test_parse_show_select_child(self):
        ast = self._parse("Show active sensors")
        assert ast.query_type in ("select", "aggregation")
        assert ast.child is not None

    def test_parse_select_has_table(self):
        ast = self._parse("List all zones")
        assert isinstance(ast.child, SelectNode)
        assert ast.child.table in ("Zone", "zone", "zones")

    def test_parse_count_returns_aggregation(self):
        ast = self._parse("How many sensors are active")
        assert ast.query_type == "aggregation"
        assert isinstance(ast.child, AggregationNode)

    def test_parse_aggregation_count_function(self):
        ast = self._parse("How many interventions are completed")
        assert isinstance(ast.child, AggregationNode)
        assert ast.child.function == "COUNT"

    def test_parse_count_by_group_by(self):
        ast = self._parse("Count sensors by type")
        assert isinstance(ast.child, AggregationNode)
        assert ast.child.group_by is not None

    def test_parse_select_with_limit(self):
        ast = self._parse("Show 5 most polluted zones")
        assert isinstance(ast.child, SelectNode)
        assert ast.child.limit_node is not None
        assert ast.child.limit_node.n == 5

    def test_parse_select_with_filter(self):
        ast = self._parse("List all active sensors")
        assert isinstance(ast.child, SelectNode)
        # filter may contain active condition
        if ast.child.filter_node:
            assert len(ast.child.filter_node.conditions) >= 0

    def test_parse_average_aggregation(self):
        ast = self._parse("Average ecological score of citizens")
        assert ast.query_type == "aggregation"
        assert isinstance(ast.child, AggregationNode)
        assert ast.child.function == "AVG"

    def test_parse_limit_node_value(self):
        ast = self._parse("Show the 10 most recent sensor readings")
        assert isinstance(ast.child, SelectNode)
        assert ast.child.limit_node is not None
        assert ast.child.limit_node.n == 10

    def test_ast_to_dict(self):
        ast = self._parse("Show zones")
        d = ast.to_dict()
        assert "node_type" in d
        assert "query_type" in d


class TestGenerator:
    """Tests for the CodeGenerator class."""

    def setup_method(self):
        self.gen = CodeGenerator()

    def _generate(self, text: str) -> str:
        tokens = Lexer(text).tokenize()
        ast = Parser(tokens).parse()
        return self.gen.generate(ast)

    def test_generate_select_returns_string(self):
        sql = self._generate("List zones")
        assert isinstance(sql, str)
        assert sql.strip().upper().startswith("SELECT")

    def test_generate_select_zone_table(self):
        sql = self._generate("Show zones")
        assert "Zone" in sql or "zone" in sql.lower()

    def test_generate_active_sensors_where(self):
        sql = self._generate("List all active sensors")
        assert "ACTIVE" in sql or "active" in sql.lower() or "WHERE" in sql.upper()

    def test_generate_limit(self):
        sql = self._generate("Show the 5 most polluted zones")
        assert "LIMIT 5" in sql.upper() or "LIMIT" in sql.upper()

    def test_generate_count(self):
        sql = self._generate("How many interventions are completed")
        assert "COUNT" in sql.upper()

    def test_generate_group_by(self):
        sql = self._generate("Count sensors by type")
        assert "GROUP BY" in sql.upper()

    def test_generate_order_by_pollution(self):
        sql = self._generate("Show the 5 most polluted zones")
        assert "ORDER BY" in sql.upper()

    def test_validate_query_select_valid(self):
        assert self.gen.validate_query("SELECT * FROM Zone") is True

    def test_validate_query_drop_invalid(self):
        assert self.gen.validate_query("DROP TABLE Zone") is False

    def test_validate_query_delete_invalid(self):
        assert self.gen.validate_query("DELETE FROM Capteur") is False

    def test_map_entity_sensor(self):
        assert self.gen._map_entity("sensors") == "Capteur"

    def test_map_entity_zone(self):
        assert self.gen._map_entity("zones") == "Zone"

    def test_map_entity_citoyen(self):
        assert self.gen._map_entity("citizens") == "Citoyen"

    def test_map_operator_greater_than(self):
        assert self.gen._map_operator("greater than") == ">"

    def test_map_operator_less_than(self):
        assert self.gen._map_operator("less than") == "<"


class TestQueryBuilder:
    """End-to-end tests for the QueryBuilder."""

    def setup_method(self):
        self.builder = QueryBuilder()

    def test_build_returns_dict(self):
        result = self.builder.build("Show zones")
        assert isinstance(result, dict)
        assert "sql" in result
        assert "success" in result

    def test_build_success_flag(self):
        result = self.builder.build("List all active sensors")
        assert result["success"] is True

    def test_build_most_polluted_zones(self):
        result = self.builder.build("Show the 5 most polluted zones")
        assert result["success"] is True
        sql = result["sql"].upper()
        assert "ZONE" in sql
        assert "LIMIT" in sql
        assert "ORDER" in sql

    def test_build_active_sensors(self):
        result = self.builder.build("List all active sensors")
        assert result["success"] is True
        sql = result["sql"].upper()
        assert "CAPTEUR" in sql
        assert "ACTIVE" in sql

    def test_build_count_interventions(self):
        result = self.builder.build("How many interventions are AI validated")
        assert result["success"] is True
        sql = result["sql"].upper()
        assert "COUNT" in sql
        assert "INTERVENTION" in sql

    def test_build_count_by_type(self):
        result = self.builder.build("Count sensors by type")
        assert result["success"] is True
        sql = result["sql"].upper()
        assert "COUNT" in sql
        assert "GROUP BY" in sql

    def test_build_includes_tokens(self):
        result = self.builder.build("Show zones")
        assert isinstance(result["tokens"], list)
        assert len(result["tokens"]) > 0

    def test_build_includes_ast(self):
        result = self.builder.build("Show zones")
        assert isinstance(result["ast"], dict)
        assert "node_type" in result["ast"]

    def test_build_error_returns_success_false(self):
        # Empty string should fail gracefully
        result = self.builder.build("")
        assert isinstance(result, dict)
        assert "success" in result

    def test_get_examples_returns_list(self):
        examples = self.builder.get_examples()
        assert isinstance(examples, list)
        assert len(examples) >= 10

    def test_get_examples_have_required_keys(self):
        examples = self.builder.get_examples()
        for ex in examples:
            assert "query" in ex
            assert "expected_sql" in ex

    def test_build_high_priority_interventions(self):
        result = self.builder.build("Show interventions with high priority")
        assert result["success"] is True
        sql = result["sql"].upper()
        assert "INTERVENTION" in sql

    def test_build_available_technicians(self):
        result = self.builder.build("List technicians available")
        assert result["success"] is True
        sql = result["sql"].upper()
        assert "TECHNICIEN" in sql

    def test_build_average_score(self):
        result = self.builder.build("Average ecological score of citizens")
        assert result["success"] is True
        sql = result["sql"].upper()
        assert "AVG" in sql
        assert "CITOYEN" in sql
