from japick.lines import Line, parse_lines


class TestParseLines:
    def test_fenced(self):
        actual = parse_lines(
            """```python
# これはテストです。
import this
```"""
        )
        assert list(actual) == [
            Line("```python", is_ignore=True),
            Line("# これはテストです。", is_ignore=True),
            Line("import this", is_ignore=True),
            Line("```", is_ignore=True),
        ]

    def test_japanese(self):
        actual = parse_lines(
            """This is test
日本語の文章を取得します。
123-4567
\u2E80
</section>"""
        )
        assert list(actual) == [
            Line("This is test", is_ignore=True),
            Line("日本語の文章を取得します。"),
            Line("123-4567", is_ignore=True),
            Line("\u2E80"),
            Line("</section>", is_ignore=True),
        ]

    def test_head(self):
        actual = parse_lines(
            """# テストです
## テストの見出し2
###許容する見出し
# This should be ignored."""
        )
        assert list(actual) == [
            Line("# テストです", is_head=True),
            Line("## テストの見出し2", is_head=True),
            Line("###許容する見出し", is_head=True),
            Line("# This should be ignored.", is_ignore=True),
        ]

    def test_list(self):
        actual = parse_lines(
            """次に示します。
* リスト1
* リスト2
- リスト3
- リスト4
    - リスト5
    - [ ] リスト6
    - [x]リスト7
1. リスト8
    1. リスト9
    2. リスト10"""
        )
        assert list(actual) == [
            Line("次に示します。"),
            Line("* リスト1", is_list=True),
            Line("* リスト2", is_list=True),
            Line("- リスト3", is_list=True),
            Line("- リスト4", is_list=True),
            Line("    - リスト5", is_list=True),
            Line("    - [ ] リスト6", is_list=True),
            Line("    - [x]リスト7", is_list=True),
            Line("1. リスト8", is_list=True),
            Line("    1. リスト9", is_list=True),
            Line("    2. リスト10", is_list=True),
        ]
