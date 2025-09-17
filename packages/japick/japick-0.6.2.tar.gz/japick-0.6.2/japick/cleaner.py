import re
from typing import Callable

from .syntax import (
    CODE_REGEX,
    CODE_TAG_REGEX,
    HEAD_REGEX,
    HTML_REGEX,
    INLINE_RETURN_SYMBOL,
    LINK_REGEX,
    LIST_REGEX,
    MASK_SYMBOL,
    NAROU_POINTS,
    NAROU_RUBY,
    NULL_SYMBOL,
    QUOTE_REGEX,
    SYMBOL_REGEX,
    URL_REGEX,
)

NOT_RET_REGEX = re.compile(r"[^\n]")


def fill(symbol: str) -> Callable:
    def _runner(matched) -> str:
        return symbol * len(matched[0])

    return _runner


def clean(line):
    """
    * Remove URL
    * Remove Markdown symbols and fill by spaces.
        * List * - 1. * [ ] ...
        * Quote > ...
        * Heading # ...
        * Link and Image [...]()
        * Bold * _
        * Strikethrough ~
    * Mask texts inside Codes `...`
    """
    line.body = LIST_REGEX.sub(fill(" "), line.body)
    line.body = QUOTE_REGEX.sub(fill(" "), line.body)
    line.body = HEAD_REGEX.sub(fill(" "), line.body)
    line.body = LINK_REGEX.sub(
        lambda m: NULL_SYMBOL * len(m[1]) + m[2] + NULL_SYMBOL * len(m[3]), line.body
    )
    line.body = HTML_REGEX.sub(fill(NULL_SYMBOL), line.body)
    line.body = URL_REGEX.sub(fill(NULL_SYMBOL), line.body)
    line.body = SYMBOL_REGEX.sub(fill(NULL_SYMBOL), line.body)
    line.body = CODE_REGEX.sub(fill(MASK_SYMBOL), line.body)
    line.body = NAROU_RUBY.sub(
        lambda m: f" {m['text']} {' ' * len(m['ruby'])} ",
        line.body,
    )
    line.body = NAROU_POINTS.sub(
        lambda m: f"  {m['text']}  ",
        line.body,
    )
    return line


def fill_null_symbols(b):
    b = b.replace(INLINE_RETURN_SYMBOL, "o")
    b = NOT_RET_REGEX.sub(NULL_SYMBOL, b)
    b = b.replace("\n", INLINE_RETURN_SYMBOL)
    return b


def unescape_html(body: str):
    body = (
        body.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&apos;", "'")
        .replace("&nbsp;", " ")
        .replace("&amp;", "&")
    )
    return body


def clean_html(body: str):
    body = CODE_TAG_REGEX.sub(
        lambda m: fill_null_symbols(m[1])
        + NOT_RET_REGEX.sub(MASK_SYMBOL, m[2])
        + fill_null_symbols(m[3]),
        body,
    )
    body = HTML_REGEX.sub(lambda m: fill_null_symbols(m[0]), body)
    return unescape_html(body)


def clean_lines(lines):
    for line in lines:
        if not line.is_ignore:
            clean(line)
        yield line


def clean_cr_lf(body: str) -> str:
    return body.replace("\r\n", " \n").replace("\r", "\n")
