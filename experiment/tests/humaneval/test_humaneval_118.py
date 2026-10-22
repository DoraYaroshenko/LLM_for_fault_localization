from src.humaneval_118 import get_closest_vowel

import math
def test_get_closest_vowel_0():
    assert get_closest_vowel('yogurt') == 'u'
def test_get_closest_vowel_1():
    assert get_closest_vowel('full') == 'u'
def test_get_closest_vowel_2():
    assert get_closest_vowel('easy') == ''
def test_get_closest_vowel_3():
    assert get_closest_vowel('eAsy') == ''
def test_get_closest_vowel_4():
    assert get_closest_vowel('ali') == ''
def test_get_closest_vowel_5():
    assert get_closest_vowel('bad') == 'a'
def test_get_closest_vowel_6():
    assert get_closest_vowel('most') == 'o'
def test_get_closest_vowel_7():
    assert get_closest_vowel('ab') == ''
def test_get_closest_vowel_8():
    assert get_closest_vowel('ba') == ''
def test_get_closest_vowel_9():
    assert get_closest_vowel('quick') == ''
def test_get_closest_vowel_10():
    assert get_closest_vowel('anime') == 'i'
def test_get_closest_vowel_11():
    assert get_closest_vowel('Asia') == ''
def test_get_closest_vowel_12():
    assert get_closest_vowel('Above') == 'o'
def test_get_closest_vowel_13():
    assert True
