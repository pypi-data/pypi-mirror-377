"""
Text Parser:
1. Split body line by line
2. Detect Japanese inside each lines
3. Detect line types
    * Header
    * List
    * General
4. Clean up Japanese lines
    * Remove URLs
    * Remove ASCII symbols
5. Detect Paragraphs and wrap by models

HTML Parser:
1. Parse HTML tags
2. Detect Japanese inside tags
"""

from typing import Iterable

from .cleaner import clean_cr_lf, clean_html, clean_lines
from .lines import parse_lines
from .paragraph import Paragraph, Pos, parse_paragraph
from .parser import html_parser
from .syntax import JA_REGEX


def parse(body: str) -> Iterable[Paragraph]:
    body = clean_cr_lf(body)
    lines = parse_lines(body)
    lines = clean_lines(lines)
    return parse_paragraph(lines)


def parse_html(html: str) -> Iterable[Paragraph]:
    html = clean_cr_lf(html)
    tags = html_parser(html)
    for tag in tags:
        lines = clean_html(tag["body"]).splitlines()
        if all(JA_REGEX.search(line) is None for line in lines):
            continue

        p = Paragraph(
            Pos(tag["pos"][0], tag["pos"][1]),
            tag["start"],
            lines,
            is_head=tag["tag"].startswith("h"),
            is_list=tag["tag"] == "li",
        )
        if p.body.strip():
            yield p
