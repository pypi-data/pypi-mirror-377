from typing import TYPE_CHECKING

from pbi_parsers.pq.tokens import TokenType

from ._base import Expression
from ._utils import lexer_reset

if TYPE_CHECKING:
    from pbi_parsers.pq.parser import Parser


class EllipsisExpression(Expression):
    def __init__(self) -> None:
        pass

    def pprint(self) -> str:  # noqa: PLR6301  # This is ignored because we want to match the interface
        return "Ellipsis ()"

    @classmethod
    @lexer_reset
    def match(cls, parser: "Parser") -> "EllipsisExpression | None":
        if parser.consume().tok_type != TokenType.ELLIPSIS:
            return None
        return EllipsisExpression()

    def children(self) -> list[Expression]:  # noqa: PLR6301
        """Returns a list of child expressions."""
        return []
