import textwrap
from typing import TYPE_CHECKING

from pbi_parsers.dax.tokens import Token, TokenType

from ._base import Expression
from ._utils import lexer_reset

if TYPE_CHECKING:
    from pbi_parsers.dax.parser import Parser


class ComparisonExpression(Expression):
    """Represents a boolean comparison expression.

    Examples:
        1 <> 2
        func() = 3
        4 > 5
        6 <= 7

    """

    operator: Token
    left: Expression
    right: Expression

    def __init__(self, operator: Token, left: Expression, right: Expression) -> None:
        self.operator = operator
        self.left = left
        self.right = right

    def children(self) -> list[Expression]:
        """Returns a list of child expressions."""
        return [self.left, self.right]

    def full_text(self) -> str:
        return self.operator.text_slice.full_text

    @classmethod
    @lexer_reset
    def match(cls, parser: "Parser") -> "ComparisonExpression | None":
        from . import EXPRESSION_HIERARCHY, any_expression_match  # noqa: PLC0415

        skip_index = EXPRESSION_HIERARCHY.index(ComparisonExpression)

        left_term = any_expression_match(parser=parser, skip_first=skip_index + 1)
        operator = parser.consume()

        if not left_term:
            return None
        if operator.tok_type not in {
            TokenType.EQUAL_SIGN,
            TokenType.NOT_EQUAL_SIGN,
            TokenType.COMPARISON_OPERATOR,
        }:
            return None

        right_term = any_expression_match(parser=parser, skip_first=skip_index)
        if right_term is None:
            msg = f"Expected a right term after operator {operator.text}, found: {parser.peek()}"
            raise ValueError(msg)
        return ComparisonExpression(operator=operator, left=left_term, right=right_term)

    def position(self) -> tuple[int, int]:
        return self.left.position()[0], self.right.position()[1]

    def pprint(self) -> str:
        left_str = textwrap.indent(self.left.pprint(), " " * 10)[10:]
        right_str = textwrap.indent(self.right.pprint(), " " * 10)[10:]
        return f"""
Bool (
    operator: {self.operator.text},
    left: {left_str},
    right: {right_str}
)""".strip()
