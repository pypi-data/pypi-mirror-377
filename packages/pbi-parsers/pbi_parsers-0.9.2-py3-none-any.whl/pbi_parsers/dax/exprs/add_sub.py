import textwrap
from typing import TYPE_CHECKING

from pbi_parsers.dax.tokens import Token, TokenType

from ._base import Expression
from ._utils import lexer_reset

if TYPE_CHECKING:
    from pbi_parsers.dax.parser import Parser


class AddSubExpression(Expression):
    """Represents an addition or subtraction expression.

    Examples:
        1 + 2
        func() - 3

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
    def match(cls, parser: "Parser") -> "AddSubExpression | None":
        from . import EXPRESSION_HIERARCHY, any_expression_match  # noqa: PLC0415

        skip_index = EXPRESSION_HIERARCHY.index(AddSubExpression)

        left_term = any_expression_match(parser=parser, skip_first=skip_index + 1)
        operator = parser.consume()

        if not left_term:
            return None
        if operator.tok_type not in {
            TokenType.PLUS_SIGN,
            TokenType.MINUS_SIGN,
        }:
            return None

        right_term = any_expression_match(parser=parser, skip_first=skip_index)
        if right_term is None:
            msg = f"Expected a right term after operator {operator.text}, found: {parser.peek()}"
            raise ValueError(msg)
        return AddSubExpression(operator=operator, left=left_term, right=right_term)

    def position(self) -> tuple[int, int]:
        return self.left.position()[0], self.right.position()[1]

    def pprint(self) -> str:
        op_str = "Add" if self.operator.text == "+" else "Sub"
        left_str = textwrap.indent(self.left.pprint(), " " * 10).lstrip()
        right_str = textwrap.indent(self.right.pprint(), " " * 11).lstrip()
        return f"""
{op_str} (
    left: {left_str},
    right: {right_str}
)""".strip()
