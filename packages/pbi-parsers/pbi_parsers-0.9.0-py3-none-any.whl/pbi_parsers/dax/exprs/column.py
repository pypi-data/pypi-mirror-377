from typing import TYPE_CHECKING

from pbi_parsers.dax.tokens import Token, TokenType

from ._base import Expression
from ._utils import lexer_reset

if TYPE_CHECKING:
    from pbi_parsers.dax.parser import Parser


class ColumnExpression(Expression):
    """Represents a column of a table in DAX.

    Examples:
        Table[Column]
        'Table Name'[Column Name]

    """

    table: Token
    column: Token

    def __init__(self, table: Token, column: Token) -> None:
        self.table = table
        self.column = column

    def children(self) -> list[Expression]:  # noqa: PLR6301
        """Returns a list of child expressions."""
        return []

    def full_text(self) -> str:
        return self.table.text_slice.full_text

    @classmethod
    @lexer_reset
    def match(cls, parser: "Parser") -> "ColumnExpression | None":
        table, column = parser.consume(), parser.consume()
        if table.tok_type not in {
            TokenType.SINGLE_QUOTED_IDENTIFIER,
            TokenType.UNQUOTED_IDENTIFIER,
        }:
            return None
        if column.tok_type != TokenType.BRACKETED_IDENTIFIER:
            return None
        return ColumnExpression(table=table, column=column)

    def position(self) -> tuple[int, int]:
        return self.table.text_slice.start, self.column.text_slice.end

    def pprint(self) -> str:
        return f"""
Column (
    {self.table.text},
    {self.column.text}
)""".strip()
