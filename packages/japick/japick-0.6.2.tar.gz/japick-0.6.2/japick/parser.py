from html.parser import HTMLParser

from .syntax import HTML_REGEX

# https://developer.mozilla.org/ja/docs/Web/HTML/Element
TARGET_TAGS = [
    "title",
    "article",
    "header",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "main",
    "section",
    "search",
    "blockquote",
    "dd",
    "div",
    "dt",
    "figcaption",
    "figure",
    # "li",
    "p",
    "pre",
    "caption",
    "td",
    "th",
    "button",
    "label",
    "textarea",
    "details",
    "dialog",
    "summary",
]


class IndexHTMLParser(HTMLParser):
    """HTMLからTARGET_TAGSに指定された要素を抜き出し、その位置情報を保持する

    結果は入れ子構造を持たず、親は子供のテキストもすべて含む形で返し、子要素も同様に結果に含まれる
    ただしliタグは例外で、liタグ内の要素はliタグの範囲のみ処理される（子要素は含まれない）
    """

    def __init__(self, raw_html):
        super().__init__()
        self.raw_html = raw_html
        self.tags = []
        self.current_tags = []
        self.in_li = False

    def handle_starttag(self, tag, attrs):
        if tag == "li":
            # liタグ内の場合、他の要素を無視しliタグの範囲で処理
            # （<li><p>...</p></li> などがあり得るため）
            self.current_tags.append((tag, self.getpos_zero()))
            self.in_li = True
        elif tag in TARGET_TAGS and not self.in_li:
            self.current_tags.append((tag, self.getpos_zero()))

    def append_tag(self, tag=None):
        if not self.current_tags:
            return

        current_tag, pos = self.current_tags.pop()
        start = self.pos_to_index(pos)
        end = self.pos_to_index(self.getpos_zero())

        # 閉じタグの終了位置を取得する
        m = HTML_REGEX.search(self.raw_html[end:])
        if m:
            end += m.end()

        self.tags.append(
            {
                "tag": tag or current_tag,
                "start": start,
                "end": end,
                "body": self.raw_html[start:end],
                "pos": pos,
                "pos_end": self.index_to_pos(end),
            }
        )

    def handle_endtag(self, tag):
        if tag == "li" and self.in_li:
            self.append_tag("li")
            self.in_li = False
        elif self.current_tags and tag == self.current_tags[-1][0] and not self.in_li:
            self.append_tag()

    def getpos_zero(self):
        line, ch = self.getpos()
        return line - 1, ch

    def pos_to_index(self, pos):
        # (Line, Column) -> Index
        lines = self.raw_html.splitlines(keepends=True)
        return sum(len(line) for line in lines[: pos[0]]) + pos[1]

    def index_to_pos(self, index):
        lines = self.raw_html.splitlines(keepends=True)
        char_count = 0
        for line_num, line in enumerate(lines):
            line_length = len(line)
            if char_count + line_length > index:
                column = index - char_count
                return line_num, column
            char_count += line_length
        return len(lines) - 1, len(lines[-1].rstrip("\r\n"))


def split_nested_elements(elements):
    """入れ子構造を持つ要素を分割して返す関数

    たとえば以下のようなタグ要素があるとする：

        [
            {'start': 0, 'end': 23, 'body': '<div>A<p>Text</p></div>'},
            {'start': 6, 'end': 17, 'body': '<p>Text</p>'},
        ]

    この場合、1要素目のbodyに2要素目の結果がそのまま含まれてしまう。
    この関数はこのような入れ子構造を持つ要素を分割して返す：

        [
            {'start': 0, 'end': 6, 'body': '<div>A'},
            {'start': 6, 'end': 17, 'body': '<p>Text</p>'},
        ]

    ただし結果が空文字かHTML要素しか含まない場合は除外される
    """

    def split_parent(parent, child):
        # 親要素を子要素の前後で2つに分割する
        before_child = {
            **parent,
            "start": parent["start"],
            "end": child["start"],
            "pos": parent["pos"],
            "pos_end": child["pos"],
            "body": parent["body"][: child["start"] - parent["start"]],
        }
        after_child = {
            **parent,
            "start": child["end"],
            "end": parent["end"],
            "pos": child["pos_end"],
            "pos_end": parent["pos_end"],
            "body": parent["body"][child["end"] - parent["start"] :],
        }
        return before_child, after_child

    elements = sorted(elements, key=lambda x: (x["start"], x["end"]))
    new_elements = {}
    i = 0
    # 要素のすべてをループしつつ、自身の以降の要素と比較し入れ子かどうかを確認
    # 入れ子がある場合は、親要素を分割して新しい要素を作成し、分割した後半は再度処理する
    while i < len(elements):
        parent = elements[i]
        nested_found = False
        # 子要素の探索
        for j in range(i + 1, len(elements)):
            child = elements[j]
            if parent["start"] < child["start"] and child["end"] < parent["end"]:
                nested_found = True
                # 親要素を分割し、前半と子供を返す一覧に追加
                before_child, after_child = split_parent(parent, child)
                new_elements[(before_child["start"], before_child["end"])] = before_child
                # 親要素の後半をリストに追加してもう一回処理
                elements[i] = after_child
                break
        if not nested_found:
            new_elements[(parent["start"], parent["end"])] = parent
            i += 1  # 入れ子がない場合のみインクリメント

    new_elements = [el for el in new_elements.values() if HTML_REGEX.sub("", el["body"]).strip()]
    return sorted(new_elements, key=lambda x: (x["start"], x["end"]))


def html_parser(html: str):
    parser = IndexHTMLParser(html)
    parser.feed(html)
    return split_nested_elements(parser.tags)
