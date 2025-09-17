"""Test markup."""

from webtools.code_markup import code_highlight
from webtools.markup import markup


def test_code_highlight_cpp():
    assert "#&lt;" in code_highlight("#<include>", "cpp")
    assert "#&lt;" in markup("```cpp\n#<include>\n```\n")
