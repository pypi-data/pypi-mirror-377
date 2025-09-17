import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

from .lines import Line
from .syntax import INLINE_RETURN_SYMBOL, NULL_SYMBOL

NULL_MATCH_REGEX = re.compile(f"({re.escape(NULL_SYMBOL)}+)")


@dataclass
class Pos:
    """Line number and column position.
    These numbers starts from Zero.
    """

    line: int
    ch: int

    def __eq__(self, other) -> bool:
        if isinstance(other, tuple):
            return self.line == other[0] and self.ch == other[1]
        else:
            return self.line == other.line and self.ch == other.ch

    def __repr__(self) -> str:
        return f"Pos({self.line}, {self.ch})"


@dataclass
class Paragraph:
    pos: Pos
    index: int
    lines: List[str]
    is_head: bool = False
    is_list: bool = False
    _body: Optional[str] = None

    def __eq__(self, other):
        return (
            self.pos == other.pos
            and self.index == other.index
            and self.lines == other.lines
            and self.is_head is other.is_head
            and self.is_list is other.is_list
        )

    @property
    def body(self):
        if self._body is not None:
            return self._body
        self._body = "\n".join(
            line.strip().replace(INLINE_RETURN_SYMBOL, "").replace(NULL_SYMBOL, "")
            for line in self.lines
        )
        return self._body

    def as_original_pos(self, index, lazy=False) -> Pos:
        """Convert index number of self.body into original text position."""
        # Convert index to cleaned body position.
        # .splitlines("") will be [], so use split("\n")
        body_lines = self.body[:index].split("\n")
        pos = Pos(
            len(body_lines) - 1,
            len(body_lines[-1]),
        )

        # Convert column number to original (self.lines) position.
        line = self.lines[pos.line]
        left_margin = len(line) - len(line.lstrip())

        # Count null symbols before the body position.
        chunks = NULL_MATCH_REGEX.split(
            line[left_margin:].replace(INLINE_RETURN_SYMBOL, NULL_SYMBOL)
        )
        body_chunks = chunks[::2]
        null_chunks = chunks[1::2]
        current = 0
        for i, chunk in enumerate(body_chunks):
            current += len(chunk)
            if (not lazy and pos.ch < current) or (lazy and pos.ch <= current):
                break
        num_null_symbols = sum(len(c) for c in null_chunks[:i])

        # Adjust column number to original position
        pos.ch += left_margin + num_null_symbols

        # Add inline breaks before this line.
        pos.line += sum(li.count(INLINE_RETURN_SYMBOL) for li in self.lines[: pos.line])

        # Add inline breaks on this line and adjust column number.
        inline_break_lines = line[: pos.ch].split(INLINE_RETURN_SYMBOL)
        if len(inline_break_lines) > 1:
            pos.line += len(inline_break_lines) - 1
            pos.ch = len(inline_break_lines[-1])

        # Add relative position to this paragraph to make it absolute of original text.
        pos.ch += self.pos.ch if pos.line == 0 else 0
        pos.line += self.pos.line

        return pos

    def as_original_index(self, index: int, lazy=False) -> int:
        """Convert index number of self.body into original text index."""
        pos = self.as_original_pos(index, lazy=lazy)
        num_lines = pos.line - self.pos.line
        lines = [li for line in self.lines for li in line.split(INLINE_RETURN_SYMBOL)]
        before_index = sum(len(line) for line in lines[:num_lines]) + num_lines
        return self.index + before_index + pos.ch - (self.pos.ch if num_lines == 0 else 0)

    def __str__(self) -> str:
        return self.body

    def __repr__(self) -> str:
        body = self.body
        if self.is_head:
            body = "# " + body
        elif self.is_list:
            body = "* " + body
        return f"Paragraph({self.pos.line},{self.pos.ch}. ({self.index}) {body})"

    def append(self, line: str):
        self.lines.append(line)

    def __bool__(self) -> bool:
        return bool(self.lines)


def parse_paragraph(lines: Iterable[Line]) -> Iterable[Paragraph]:
    """
    Combine multiple lines into one Paragraph.
    Each paragraphs has chunks.
    """
    paragraph = Paragraph(Pos(0, 0), 0, [])
    index = 0
    for i, line in enumerate(lines):
        next_index = index + len(line.body) + 1

        if line.is_ignore or line.is_head or line.is_list:
            if paragraph:
                yield paragraph
            paragraph = Paragraph(Pos(i + 1, 0), next_index, [])

        if line.is_head or line.is_list:
            # Yield my self as 1 line paragraph.
            yield Paragraph(
                Pos(i, 0),
                index,
                [line.body],
                is_head=line.is_head,
                is_list=line.is_list,
            )
        elif not line.is_ignore:
            paragraph.append(line.body)

        index = next_index

    if paragraph:
        yield paragraph
