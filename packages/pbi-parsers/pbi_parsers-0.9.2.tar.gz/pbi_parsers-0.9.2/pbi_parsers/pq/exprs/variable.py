import textwrap
from typing import TYPE_CHECKING

from pbi_parsers.pq.tokens import Token, TokenType

from ._base import Expression
from ._utils import lexer_reset

if TYPE_CHECKING:
    from pbi_parsers.pq.parser import Parser


class VariableExpression(Expression):
    var_name: Token
    statement: Expression

    def __init__(self, var_name: Token, statement: Expression) -> None:
        self.var_name = var_name
        self.statement = statement

    def pprint(self) -> str:
        statement = textwrap.indent(self.statement.pprint(), " " * 17).lstrip()
        return f"""
Variable (
    name: {self.var_name.text},
    statement: {statement}
)
""".strip()

    @classmethod
    @lexer_reset
    def match(cls, parser: "Parser") -> "VariableExpression | None":
        from . import any_expression_match  # noqa: PLC0415

        var_name = parser.consume()
        equal_sign = parser.consume()
        if (
            var_name.tok_type
            not in {TokenType.QUOTED_IDENTIFER, TokenType.UNQUOTED_IDENTIFIER, TokenType.HASH_IDENTIFIER}
            or equal_sign.tok_type != TokenType.EQUAL_SIGN
        ):
            return None

        statement = any_expression_match(parser)
        if statement is None:
            msg = "VariableExpression.match called without valid inner expression"
            raise ValueError(msg)
        return VariableExpression(var_name=var_name, statement=statement)

    def children(self) -> list[Expression]:
        """Returns a list of child expressions."""
        return [self.statement]
