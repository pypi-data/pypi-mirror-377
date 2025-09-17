# japick

文章中から日本語のパラグラフのみ抽出するライブラリーです。
現在はMarkdownにのみ緩やかに対応しています。

`japick.parse` 関数に日本語を含む文章を渡してください。
詳しい使い方は `japick.paragraph.Paragraph` クラスを参照ください。

## フォーマット修正

```bash
$ pip install invoke black isort
$ invoke format
```

## テスト

```bash
$ pip install tox
$ tox
```
