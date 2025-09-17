import re

NULL_SYMBOL = "~"
INLINE_RETURN_SYMBOL = (
    "ṏ"  # Return symbol inside inline tags (Representing both \n and NULL_SYMBOL)
)
MASK_SYMBOL = "_"

JA_REGEX = re.compile(
    "["
    "\uFF61-\uFF9F"  # HALFWIDTH KATAKANA
    "\u3041-\u309F"  # HIRAGANA
    "\u30A1-\u30FF"  # KATAKANA
    "\u2E80-\u2FDF\u3005-\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF"  # KANJI
    "\u2105-\u273D\u3004-\u33FE\uFD3E-\uFFE4"  # JAPANES SPECIAL SYMBOLS
    "\U00020000-\U0002EBEF"  # KANJI
    "]+"
)

HEAD_REGEX = re.compile("^#+")
LIST_REGEX = re.compile(r"^>?\s*([*-] |\d+\. |[･・])(\[[x ]?] )?")
QUOTE_REGEX = re.compile(r"^>+\s*")
HTML_REGEX = re.compile(r'<("[^"]*"|\'[^\']*\'|[^\'">])*>')

URL_REGEX = re.compile(r"<?(http|https|ftp)://[-a-zA-Z0-9@:%_+.~#?&/=]+>?")
LINK_REGEX = re.compile(r"(!?\[)(.*?)(]\(.*?\))")
CODE_REGEX = re.compile(r"`.+?`")
CODE_TAG_REGEX = re.compile(r"(<code\b[^>]*>)(.*?)(</\s*code\s*>)", re.DOTALL | re.IGNORECASE)
SYMBOL_REGEX = re.compile(r"(\*|___|__|~)")  # ASCII Symbols to clean

FENCE_START = re.compile("^```.*$")
FENCE_END = re.compile("^```$")

NAROU_RUBY = re.compile(r"[\|｜](?P<text>.*?)《(?P<ruby>.*?)》")
NAROU_POINTS = re.compile(r"《《(?P<text>.*?)》》")
