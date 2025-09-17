from japick.main import parse, parse_html
from japick.syntax import MASK_SYMBOL


def test_it():
    body = """# これはテストです
こんにちは。
これは文章です。

* リスト
* リスト2と `code` もあります

<section>
  ここは別のパラグラフです。
  Shodo（https://shodo.ink/）とこの次の文字、Xのインデックスを取りましょう。
</section>"""
    paragraphs = list(parse(body))
    assert len(paragraphs) == 5
    assert paragraphs[0].is_head
    assert paragraphs[0].body == "これはテストです"
    assert paragraphs[1].body == "こんにちは。\nこれは文章です。"
    assert paragraphs[2].is_list
    assert paragraphs[2].body == "リスト"
    assert paragraphs[3].is_list
    assert paragraphs[3].body == f"リスト2と {MASK_SYMBOL * 6} もあります"
    assert paragraphs[3].as_original_pos(15) == (5, 17)
    assert paragraphs[3].as_original_index(15) == 51
    assert body[51] == "り"
    assert (
        paragraphs[4].body
        == """\
ここは別のパラグラフです。
Shodo（）とこの次の文字、Xのインデックスを取りましょう。"""
    )
    assert paragraphs[4].as_original_pos(29) == (9, 35)
    assert paragraphs[4].as_original_index(29) == 117
    assert body[117] == "X"


def test_parse_windows_crlf():
    body = "テスト1\r\nテスト2\r\n\r\nテスト3"
    paragraphs = list(parse(body))
    assert len(paragraphs) == 2
    assert paragraphs[0].body == "テスト1\nテスト2"
    assert paragraphs[0].as_original_pos(5) == (1, 0)
    assert paragraphs[0].as_original_index(5) == 6
    assert paragraphs[1].body == "テスト3"


def test_html():
    html = """<h1>これはテストです</h1>
<p>こんにちは。</p>
<ul>
  <li>リスト</li>
  <li>リスト2と <code class="foo">code</code> もあります</li>
</ul>
  <p>
    ここは別のパラ
    グラフです。
  </p>
"""
    paragraphs = list(parse_html(html))
    assert len(paragraphs) == 5
    assert paragraphs[0].is_head
    assert paragraphs[0].body == "これはテストです"
    assert paragraphs[0].as_original_index(3) == 7

    assert not paragraphs[1].is_list
    assert not paragraphs[1].is_head
    assert paragraphs[1].body == "こんにちは。"

    assert paragraphs[2].is_list
    assert paragraphs[2].body == "リスト"

    assert paragraphs[3].is_list
    assert paragraphs[3].body == f"リスト2と {MASK_SYMBOL * 4} もあります"
    assert paragraphs[3].as_original_index(6) == 82
    assert paragraphs[3].as_original_pos(6) == (4, 30)
    assert paragraphs[3].as_original_pos(10, lazy=True) == (4, 34)
    assert paragraphs[3].as_original_pos(10) == (4, 41)

    assert paragraphs[4].body == "\nここは別のパラ\nグラフです。\n"
    assert paragraphs[4].as_original_index(10) == 134
    assert paragraphs[4].as_original_pos(10) == (8, 5)


def test_html_inline_break():
    html = """<p>
  これで<a
  >見れる</a>
</p>"""
    paragraphs = list(parse_html(html))
    assert len(paragraphs) == 1
    assert paragraphs[0].body == "\nこれで見れる\n"
    assert paragraphs[0].as_original_index(4) == 15
    assert paragraphs[0].as_original_pos(4) == (2, 3)
    assert paragraphs[0].as_original_index(4, lazy=True) == 9
    assert paragraphs[0].as_original_pos(4, lazy=True) == (1, 5)


def test_html_inline_breaks_before_the_line():
    html = """
<p class="content">
  <a
  href="http://www.yahoo.co.jp"
  >YAHOO!</a>の検索はこちらから。
  Djangoのインストールは見れる。
</p>
"""

    paragraphs = list(parse_html(html))
    assert len(paragraphs) == 1
    assert paragraphs[0].body == "\nYAHOO!の検索はこちらから。\nDjangoのインストールは見れる。\n"
    assert paragraphs[0].as_original_index(32) == 98


def test_html_inline_breaks_at_the_first():
    html = """  <p><a
    href="http://www.yahoo.co.jp"
    >Djangoのインストールは見れる。
  </a></p>
"""

    paragraphs = list(parse_html(html))
    assert len(paragraphs) == 1
    assert paragraphs[0].body == "Djangoのインストールは見れる。\n"
    assert paragraphs[0].as_original_index(14) == 61


def test_html_inline_breaks_empty_breaks():
    html = """<p><a
    >
    Djangoのインストールは見れる。
  </a></p>
"""

    paragraphs = list(parse_html(html))
    assert len(paragraphs) == 1
    assert paragraphs[0].body == "\nDjangoのインストールは見れる。\n"
    assert paragraphs[0].as_original_index(15) == 30
    assert paragraphs[0].as_original_pos(15) == (2, 18)


def test_html_code():
    html = """<p>
  これは<code
  >KeyWord
   <span/></code>です。
</p>"""
    paragraphs = list(parse_html(html))
    assert len(paragraphs) == 1
    assert paragraphs[0].body == "\nこれは_______\n__________です。\n"
    assert paragraphs[0].as_original_index(4) == 18
    assert paragraphs[0].as_original_pos(4) == (2, 3)
    assert paragraphs[0].as_original_index(4, lazy=True) == 9
    assert paragraphs[0].as_original_pos(4, lazy=True) == (1, 5)


def test_html_upper():
    html = """<P>
  これで見れる
</P>"""
    paragraphs = list(parse_html(html))
    assert len(paragraphs) == 1
    assert paragraphs[0].body == "\nこれで見れる\n"


def test_html_pre_code():
    html = """<pre><code>
  # これはテスト
</code></pre>"""
    assert len(list(parse_html(html))) == 0


def test_windows_crlf():
    html = "<p>テスト1</p>\r\n<p>テスト2</p>\r\n<p>テスト3</p>\r\n<p>テスト4</p>"
    paragraphs = list(parse_html(html))
    assert len(paragraphs) == 4
    assert paragraphs[0].body == "テスト1"
    assert paragraphs[1].body == "テスト2"
    assert paragraphs[1].as_original_pos(3) == (1, 6)
    assert paragraphs[1].as_original_index(3) == 19
    assert paragraphs[2].body == "テスト3"
    assert paragraphs[3].body == "テスト4"
    assert paragraphs[3].as_original_pos(3) == (3, 6)
    assert paragraphs[3].as_original_index(3) == 45


def test_windows_crlf_inside_tag():
    html = "<p>\r\nテスト\r\n1\r\n</p>"
    paragraphs = list(parse_html(html))
    assert len(paragraphs) == 1
    assert paragraphs[0].body == "\nテスト\n1\n"
    assert paragraphs[0].as_original_pos(6) == (2, 1)
    assert paragraphs[0].as_original_index(6) == 11
