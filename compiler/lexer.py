"""
Lexer for the Smart City NL-to-SQL compiler.
Tokenizes natural language queries into structured tokens.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional

from compiler.grammar import TOKEN_PATTERNS


class TokenType(Enum):
    """Enumeration of all token types."""
    KEYWORD = auto()
    ENTITY = auto()
    FIELD = auto()
    NUMBER = auto()
    STRING = auto()
    OPERATOR = auto()
    ADJECTIVE = auto()
    COMPARATOR = auto()
    QUANTIFIER = auto()
    AGGREGATOR = auto()
    LOCATION = auto()
    CONJUNCTION = auto()
    PUNCTUATION = auto()
    IDENTIFIER = auto()
    EOF = auto()


@dataclass
class Token:
    """Represents a single lexical token."""
    type: TokenType
    value: str
    position: int

    def to_dict(self) -> dict:
        return {"type": self.type.name, "value": self.value, "position": self.position}

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, pos={self.position})"


# Map grammar pattern names → TokenType
_TYPE_MAP: dict[str, TokenType] = {
    "KEYWORD": TokenType.KEYWORD,
    "ENTITY": TokenType.ENTITY,
    "FIELD": TokenType.FIELD,
    "NUMBER": TokenType.NUMBER,
    "STRING": TokenType.STRING,
    "OPERATOR": TokenType.OPERATOR,
    "ADJECTIVE": TokenType.ADJECTIVE,
    "COMPARATOR": TokenType.COMPARATOR,
    "QUANTIFIER": TokenType.QUANTIFIER,
    "AGGREGATOR": TokenType.AGGREGATOR,
    "LOCATION": TokenType.LOCATION,
    "CONJUNCTION": TokenType.CONJUNCTION,
    "PUNCTUATION": TokenType.PUNCTUATION,
    "IDENTIFIER": TokenType.IDENTIFIER,
    "EOF": TokenType.EOF,
}

# Pre-compile patterns
_COMPILED_PATTERNS = [
    (name, re.compile(pattern))
    for name, pattern in TOKEN_PATTERNS
]

# Multi-word phrases to normalise before tokenisation
_MULTI_WORD_OPERATORS = [
    ("greater than or equal to", ">="),
    ("less than or equal to", "<="),
    ("greater than", ">"),
    ("less than", "<"),
    ("equal to", "="),
    ("not equal to", "!="),
    ("more than", ">"),
    ("at least", ">="),
    ("at most", "<="),
    ("how many", "HOWMANY"),
    ("how much", "HOWMUCH"),
    ("ai validated", "ai_validated"),
    ("ecological score", "score_ecologique"),
]


def _normalise(text: str) -> str:
    """Replace multi-word phrases with single tokens."""
    result = text
    for phrase, replacement in _MULTI_WORD_OPERATORS:
        result = re.sub(re.escape(phrase), replacement, result, flags=re.IGNORECASE)
    return result


class Lexer:
    """
    Tokenises a natural language query string into a list of Token objects.

    Usage::
        lexer = Lexer("Show the 5 most polluted zones")
        tokens = lexer.tokenize()
    """

    def __init__(self, text: str) -> None:
        self.original_text = text
        self.text = _normalise(text)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def tokenize(self) -> List[Token]:
        """Return list of tokens for the input query."""
        tokens: List[Token] = []
        pos = 0
        text = self.text

        while pos < len(text):
            # Skip whitespace
            ws = re.match(r"\s+", text[pos:])
            if ws:
                pos += ws.end()
                continue

            token = self._match_token(text, pos)
            if token is None:
                # Unknown character – skip
                pos += 1
                continue

            # Filter out noise-only tokens (single-char punctuation we don't need)
            tokens.append(token)
            pos += len(token.value)

        tokens.append(Token(TokenType.EOF, "", pos))
        return tokens

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _match_token(self, text: str, pos: int) -> Optional[Token]:
        """Try each compiled pattern and return the first match at *pos*."""
        remaining = text[pos:]

        # Restore HOWMANY / HOWMUCH before creating token value
        def restore(s: str) -> str:
            s = s.replace("HOWMANY", "how many")
            s = s.replace("HOWMUCH", "how much")
            return s

        for type_name, pattern in _COMPILED_PATTERNS:
            m = pattern.match(remaining)
            if m:
                raw_value = m.group(0)
                value = restore(raw_value)
                token_type = _TYPE_MAP.get(type_name, TokenType.IDENTIFIER)

                # Special handling: HOWMANY → QUANTIFIER
                if raw_value.upper() in ("HOWMANY", "HOWMUCH"):
                    token_type = TokenType.QUANTIFIER

                return Token(token_type, value, pos)

        return None
