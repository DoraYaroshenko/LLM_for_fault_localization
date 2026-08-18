from src.humaneval_134 import check_if_last_char_is_a_letter

import math
def test_check_if_last_char_is_a_letter_0():
    assert check_if_last_char_is_a_letter('apple') == False
def test_check_if_last_char_is_a_letter_1():
    assert check_if_last_char_is_a_letter('apple pi e') == True
def test_check_if_last_char_is_a_letter_2():
    assert check_if_last_char_is_a_letter('eeeee') == False
def test_check_if_last_char_is_a_letter_3():
    assert check_if_last_char_is_a_letter('A') == True
def test_check_if_last_char_is_a_letter_4():
    assert check_if_last_char_is_a_letter('Pumpkin pie ') == False
def test_check_if_last_char_is_a_letter_5():
    assert check_if_last_char_is_a_letter('Pumpkin pie 1') == False
def test_check_if_last_char_is_a_letter_6():
    assert check_if_last_char_is_a_letter('') == False
def test_check_if_last_char_is_a_letter_7():
    assert check_if_last_char_is_a_letter('eeeee e ') == False
def test_check_if_last_char_is_a_letter_8():
    assert check_if_last_char_is_a_letter('apple pie') == False
def test_check_if_last_char_is_a_letter_9():
    assert check_if_last_char_is_a_letter('apple pi e ') == False
def test_check_if_last_char_is_a_letter_10():
    assert True
