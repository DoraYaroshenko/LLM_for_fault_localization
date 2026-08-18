from src.humaneval_119 import match_parens

import math
def test_match_parens_0():
    assert match_parens(['()(', ')']) == 'Yes'
def test_match_parens_1():
    assert match_parens([')', ')']) == 'No'
def test_match_parens_2():
    assert match_parens(['(()(())', '())())']) == 'No'
def test_match_parens_3():
    assert match_parens([')())', '(()()(']) == 'Yes'
def test_match_parens_4():
    assert match_parens(['(())))', '(()())((']) == 'Yes'
def test_match_parens_5():
    assert match_parens(['()', '())']) == 'No'
def test_match_parens_6():
    assert match_parens(['(()(', '()))()']) == 'Yes'
def test_match_parens_7():
    assert match_parens(['((((', '((())']) == 'No'
def test_match_parens_8():
    assert match_parens([')(()', '(()(']) == 'No'
def test_match_parens_9():
    assert match_parens([')(', ')(']) == 'No'
def test_match_parens_10():
    assert match_parens(['(', ')']) == 'Yes'
def test_match_parens_11():
    assert match_parens([')', '(']) == 'Yes'
