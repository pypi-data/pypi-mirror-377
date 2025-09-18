from typing import TYPE_CHECKING

from pbi_parsers.dax.tokens import Token, TokenType

from ._base import Expression
from ._utils import lexer_reset

if TYPE_CHECKING:
    from pbi_parsers.dax.parser import Parser


class LiteralStringExpression(Expression):
    """A literal string in DAX.

    Examples:
        "Hello, World!"
        "Another String"

    """

    value: Token

    def __init__(self, value: Token) -> None:
        self.value = value

    def children(self) -> list[Expression]:  # noqa: PLR6301
        """Returns a list of child expressions."""
        return []

    def full_text(self) -> str:
        return self.value.text_slice.full_text

    @classmethod
    @lexer_reset
    def match(cls, parser: "Parser") -> "LiteralStringExpression | None":
        if cls.match_tokens(parser, [TokenType.STRING_LITERAL]):
            value = parser.consume()
            return LiteralStringExpression(value=value)
        return None

    def position(self) -> tuple[int, int]:
        return self.value.text_slice.start, self.value.text_slice.end

    def pprint(self) -> str:
        return f"String ({self.value.text})"
