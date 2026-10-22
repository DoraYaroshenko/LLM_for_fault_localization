from src.humaneval_61 import correct_bracketing

import math
def test_correct_bracketing_0():
    assert correct_bracketing('()')
def test_correct_bracketing_1():
    assert correct_bracketing('(()())')
def test_correct_bracketing_2():
    assert correct_bracketing('()()(()())()')
def test_correct_bracketing_3():
    assert correct_bracketing('()()((()()())())(()()(()))')
def test_correct_bracketing_4():
    assert not correct_bracketing('((()())))')
def test_correct_bracketing_5():
    assert not correct_bracketing(')(()')
def test_correct_bracketing_6():
    assert not correct_bracketing('(')
def test_correct_bracketing_7():
    assert not correct_bracketing('((((')
def test_correct_bracketing_8():
    assert not correct_bracketing(')')
def test_correct_bracketing_9():
    assert not correct_bracketing('(()')
def test_correct_bracketing_10():
    assert not correct_bracketing('()()(()())())(()')
def test_correct_bracketing_11():
    assert not correct_bracketing('()()(()())()))()')
