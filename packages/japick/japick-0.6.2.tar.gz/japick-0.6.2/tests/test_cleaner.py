from japick.cleaner import clean_lines
from japick.lines import Line, parse_lines
from japick.syntax import MASK_SYMBOL, NULL_SYMBOL


def call_target(body):
    lines = parse_lines(body)
    return list(clean_lines(lines))


def test_clean_list():
    actual = call_target(
        """* リスト1
* リスト2
    - リスト3
    - [ ] リスト4"""
    )
    assert actual == [
        Line("  リスト1", is_list=True),
        Line("  リスト2", is_list=True),
        Line("      リスト3", is_list=True),
        Line("          リスト4", is_list=True),
    ]


def test_clean_quote():
    actual = call_target(
        """> テスト
> テスト2"""
    )
    assert actual == [
        Line("  テスト"),
        Line("  テスト2"),
    ]


def test_clean_head():
    actual = call_target(
        """# 見出し1
## 見出し2
"""
    )
    assert actual == [
        Line("  見出し1", is_head=True),
        Line("   見出し2", is_head=True),
    ]


def test_clean_link():
    actual = call_target(
        """これは ![テスト](https://foobar.com/) です。
実際には[リンク](https://shodo.ink/)となります。
難しいことはありません [1]。"""
    )
    assert actual == [
        Line(f"これは {NULL_SYMBOL * 2}テスト{NULL_SYMBOL * 22} です。"),
        Line(f"実際には{NULL_SYMBOL}リンク{NULL_SYMBOL * 21}となります。"),
        Line("難しいことはありません [1]。"),
    ]


def test_clean_html():
    actual = call_target(
        """<section>
    テスト</section>
これは <a href="#">リンク</a> のテスト。"""
    )
    assert actual == [
        Line("<section>", is_ignore=True),
        Line(f"    テスト{NULL_SYMBOL * 10}"),
        Line(f"これは {NULL_SYMBOL * 12}リンク{NULL_SYMBOL * 4} のテスト。"),
    ]


def test_clean_html_close_tag_text():
    actual = call_target("""<a data-example=">">テスト</a>""")
    assert actual == [
        Line(f"{NULL_SYMBOL * 20}テスト{NULL_SYMBOL * 4}"),
    ]


def test_clean_url():
    actual = call_target(
        """次は https://shodo.ink/ でお会いしましょう。
URLに https://foobar.com/日本語/ が入っている場合。
括弧書きは（https://foobar.com/）機能します。
"""
    )
    assert actual == [
        Line(f"次は {NULL_SYMBOL * 18} でお会いしましょう。"),
        Line(f"URLに {NULL_SYMBOL * 19}日本語/ が入っている場合。"),
        Line(f"括弧書きは（{NULL_SYMBOL * 19}）機能します。"),
    ]


def test_clean_symbol():
    actual = call_target(
        """**太字** の場合。
__別の太字__ もある。
間に test_foo と入る。
他に,論文っぽい読点は許容する (半角カッコも) .
"""
    )
    assert actual == [
        Line(f"{NULL_SYMBOL * 2}太字{NULL_SYMBOL * 2} の場合。"),
        Line(f"{NULL_SYMBOL * 2}別の太字{NULL_SYMBOL * 2} もある。"),
        Line("間に test_foo と入る。"),
        Line("他に,論文っぽい読点は許容する (半角カッコも) ."),
    ]


def test_mask_code():
    actual = call_target(
        """コード表記は `mask` される。
理由は単純で、コードを形態素解析 `しない` ため。"""
    )
    assert actual == [
        Line(f"コード表記は {MASK_SYMBOL * 6} される。"),
        Line(f"理由は単純で、コードを形態素解析 {MASK_SYMBOL * 5} ため。"),
    ]


def test_it():
    actual = call_target(
        """
# 見出し1
## 見出し2
### 見出し3

- リスト1
    - ネスト リスト1_1
        - ネスト リスト1_1_1
    - ネスト リスト1_2
- リスト2

1. 番号付きリスト1
    1. 番号付きリスト1_1
1. 番号付きリスト2

> ご連絡いただいた
> お世話になります！
>> お世話になります。

    # コメント
    class Test
        pass

インストールは `pip install japick` です。
**太字** の場合。
___別の太字___ も
[Googleさん](https://www.google.co.jp/) 。
~~取り消し~~。[内部リンク][google]。
"""
    )
    assert actual == [
        Line("", is_ignore=True),
        Line("  見出し1", is_head=True),
        Line("   見出し2", is_head=True),
        Line("    見出し3", is_head=True),
        Line("", is_ignore=True),
        Line("  リスト1", is_list=True),
        Line("      ネスト リスト1_1", is_list=True),
        Line("          ネスト リスト1_1_1", is_list=True),
        Line("      ネスト リスト1_2", is_list=True),
        Line("  リスト2", is_list=True),
        Line("", is_ignore=True),
        Line("   番号付きリスト1", is_list=True),
        Line("       番号付きリスト1_1", is_list=True),
        Line("   番号付きリスト2", is_list=True),
        Line("", is_ignore=True),
        Line("  ご連絡いただいた"),
        Line("  お世話になります！"),
        Line("   お世話になります。"),
        Line("", is_ignore=True),
        Line("    # コメント"),
        Line("    class Test", is_ignore=True),
        Line("        pass", is_ignore=True),
        Line("", is_ignore=True),
        Line(f"インストールは {MASK_SYMBOL * 20} です。"),
        Line(f"{NULL_SYMBOL * 2}太字{NULL_SYMBOL * 2} の場合。"),
        Line(f"{NULL_SYMBOL * 3}別の太字{NULL_SYMBOL * 3} も"),
        Line(f"{NULL_SYMBOL}Googleさん{NULL_SYMBOL * 28} 。"),
        Line(f"{NULL_SYMBOL * 2}取り消し{NULL_SYMBOL * 2}。[内部リンク][google]。"),
    ]


def test_clean_narou():
    actual = call_target(
        """\
これはテストです。
《《何を言っているのかわからねーと思うが》》。
｜伸縮自在の愛《バンジーガム》
|薄っぺらな嘘《ドッキリテクスチャー》
|これは|テスト|"""
    )
    assert actual == [
        Line("これはテストです。", is_list=False, is_head=False),
        Line("  何を言っているのかわからねーと思うが  。", is_list=False, is_head=False),
        Line(" 伸縮自在の愛        ", is_list=False, is_head=False),
        Line(" 薄っぺらな嘘            ", is_list=False, is_head=False),
        Line("|これは|テスト|", is_list=False, is_head=False),
    ]
