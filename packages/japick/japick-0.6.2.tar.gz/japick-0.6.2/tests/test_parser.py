from japick.parser import html_parser


def test_h1():
    tags = html_parser("<h1>これはテストです</h1>")
    assert tags == [
        {
            "tag": "h1",
            "start": 0,
            "end": 17,
            "body": "<h1>これはテストです</h1>",
            "pos": (0, 0),
            "pos_end": (0, 17),
        },
    ]


def test_li_with_p():
    tags = html_parser("<ul><li><p>リスト</p></li></ul>")
    assert tags == [
        {
            "tag": "li",
            "start": 4,
            "end": 23,
            "body": "<li><p>リスト</p></li>",
            "pos": (0, 4),
            "pos_end": (0, 23),
        },
    ]


def test_tag_close_tag_text():
    tags = html_parser('<h1 data-example=">">これはテストです</h1>')
    assert tags == [
        {
            "tag": "h1",
            "start": 0,
            "end": 34,
            "body": '<h1 data-example=">">これはテストです</h1>',
            "pos": (0, 0),
            "pos_end": (0, 34),
        },
    ]


def test_with_spaces():
    tags = html_parser(
        """
    <section>
      これがセクションです。
    </section>
"""
    )
    assert tags == [
        {
            "tag": "section",
            "start": 5,
            "end": 47,
            "body": "<section>\n      これがセクションです。\n    </section>",
            "pos": (1, 4),
            "pos_end": (3, 14),
        }
    ]


def test_nested():
    tags = html_parser(
        """
    <section>
      これがセクションです。
      <div>
          子供です。
          <p>これが段落です。</p>
          子供の後ろです。
      </div>
    </section>
"""
    )
    assert tags == [
        {
            "tag": "section",
            "start": 5,
            "end": 39,
            "body": "<section>\n      これがセクションです。\n      ",
            "pos": (1, 4),
            "pos_end": (3, 6),
        },
        {
            "tag": "div",
            "start": 39,
            "end": 71,
            "body": "<div>\n          子供です。\n          ",
            "pos": (3, 6),
            "pos_end": (5, 10),
        },
        {
            "tag": "p",
            "start": 71,
            "end": 86,
            "body": "<p>これが段落です。</p>",
            "pos": (5, 10),
            "pos_end": (5, 25),
        },
        {
            "tag": "div",
            "start": 86,
            "end": 118,
            "body": "\n          子供の後ろです。\n      </div>",
            "pos": (5, 25),
            "pos_end": (7, 12),
        },
    ]


def test_nested_brother():
    tags = html_parser(
        """
    <section>
      <h1>見出しです</h1>
      <p>これが段落です。</p>
    </section>
"""
    )
    assert tags == [
        {
            "tag": "h1",
            "start": 21,
            "end": 35,
            "body": "<h1>見出しです</h1>",
            "pos": (2, 6),
            "pos_end": (2, 20),
        },
        {
            "tag": "p",
            "start": 42,
            "end": 57,
            "body": "<p>これが段落です。</p>",
            "pos": (3, 6),
            "pos_end": (3, 21),
        },
    ]


def test_self_closing_tag():
    tags = html_parser("<div/>")
    assert tags == []


def test_naked_text():
    tags = html_parser("これはテストです")
    assert tags == []


def test_windows_return():
    tags = html_parser("<p>テスト1</p>\r\n<p>テスト2</p>")
    assert tags == [
        {
            "tag": "p",
            "start": 0,
            "end": 11,
            "body": "<p>テスト1</p>",
            "pos": (0, 0),
            "pos_end": (0, 11),
        },
        {
            "tag": "p",
            "start": 13,
            "end": 24,
            "body": "<p>テスト2</p>",
            "pos": (1, 0),
            "pos_end": (1, 11),
        },
    ]
