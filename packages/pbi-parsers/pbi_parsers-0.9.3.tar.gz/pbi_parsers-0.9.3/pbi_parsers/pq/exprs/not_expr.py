from typing import TYPE_CHECKING

from pbi_parsers.pq.tokens import TokenType

from ._base import Expression
from ._utils import lexer_reset

if TYPE_CHECKING:
    from pbi_parsers.pq.parser import Parser


class NotExpression(Expression):
    expr: Expression

    def __init__(
        self,
        expr: Expression,
    ) -> None:
        self.expr = expr

    def pprint(self) -> str:
        return f"Not ({self.expr.pprint()})"

    @classmethod
    @lexer_reset
    def match(cls, parser: "Parser") -> "NotExpression | None":
        from . import any_expression_match  # noqa: PLC0415

        if parser.consume().tok_type != TokenType.NOT:
            return None

        expr = any_expression_match(parser)
        if expr is None:
            return None
        return NotExpression(expr=expr)

    def children(self) -> list[Expression]:
        """Returns a list of child expressions."""
        return [self.expr]
