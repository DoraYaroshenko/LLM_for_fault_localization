from src.humaneval_156 import int_to_mini_roman

import math
def test_int_to_mini_roman_0():
    assert int_to_mini_roman(19) == 'xix'
def test_int_to_mini_roman_1():
    assert int_to_mini_roman(152) == 'clii'
def test_int_to_mini_roman_2():
    assert int_to_mini_roman(251) == 'ccli'
def test_int_to_mini_roman_3():
    assert int_to_mini_roman(426) == 'cdxxvi'
def test_int_to_mini_roman_4():
    assert int_to_mini_roman(500) == 'd'
def test_int_to_mini_roman_5():
    assert int_to_mini_roman(1) == 'i'
def test_int_to_mini_roman_6():
    assert int_to_mini_roman(4) == 'iv'
def test_int_to_mini_roman_7():
    assert int_to_mini_roman(43) == 'xliii'
def test_int_to_mini_roman_8():
    assert int_to_mini_roman(90) == 'xc'
def test_int_to_mini_roman_9():
    assert int_to_mini_roman(94) == 'xciv'
def test_int_to_mini_roman_10():
    assert int_to_mini_roman(532) == 'dxxxii'
def test_int_to_mini_roman_11():
    assert int_to_mini_roman(900) == 'cm'
def test_int_to_mini_roman_12():
    assert int_to_mini_roman(994) == 'cmxciv'
def test_int_to_mini_roman_13():
    assert int_to_mini_roman(1000) == 'm'
def test_int_to_mini_roman_14():
    assert True
