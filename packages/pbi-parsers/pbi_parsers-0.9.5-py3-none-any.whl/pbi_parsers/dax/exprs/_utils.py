from collections.abc import Callable
from typing import ParamSpec, TypeVar

from pbi_parsers.dax.exprs._base import Expression
from pbi_parsers.dax.parser import Parser
from pbi_parsers.dax.tokens import TokenType

P = ParamSpec("P")  # Represents the parameters of the decorated function
R = TypeVar("R")  # Represents the return type of the decorated function


def lexer_reset(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to reset the lexer state before and after parsing an expression.

    This decorator performs the following actions:
    1. Collects pre-comments before parsing.
    2. Caches the result of the parsing function to avoid redundant parsing.
    3. Collects post-comments after parsing.

    The caching is required since the operator precedence otherwise leads to all other expressions being
    called multiple times.
    """

    def lexer_reset_inner(*args: P.args, **kwargs: P.kwargs) -> R:
        parser = args[1]
        if not isinstance(parser, Parser):
            msg = f"Expected the second argument to be a Parser instance, got {type(parser)}"
            raise TypeError(msg)
        idx = parser.index

        pre_comments = []
        while parser.peek().tok_type in {TokenType.SINGLE_LINE_COMMENT, TokenType.MULTI_LINE_COMMENT}:
            pre_comments.append(parser.consume())

        # Speed up of a bazillion
        cached_val, cached_index = parser.cache.get((idx, id(func)), (None, -1))
        if cached_val is not None:
            parser.index = cached_index
            return cached_val

        ret = func(*args, **kwargs)

        post_comments = []
        while parser.peek().tok_type in {TokenType.SINGLE_LINE_COMMENT, TokenType.MULTI_LINE_COMMENT}:
            post_comments.append(parser.consume())

        if isinstance(ret, Expression):
            ret.pre_comments = pre_comments
            ret.post_comments = post_comments

        parser.cache[idx, id(func)] = (ret, parser.index)
        if ret is None:
            parser.index = idx
        return ret

    return lexer_reset_inner
