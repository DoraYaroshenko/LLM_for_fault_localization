from src.humaneval_126 import is_sorted

import math
def test_is_sorted_0():
    assert is_sorted([5]) == True
def test_is_sorted_1():
    assert is_sorted([1, 2, 3, 4, 5]) == True
def test_is_sorted_2():
    assert is_sorted([1, 3, 2, 4, 5]) == False
def test_is_sorted_3():
    assert is_sorted([1, 2, 3, 4, 5, 6]) == True
def test_is_sorted_4():
    assert is_sorted([1, 2, 3, 4, 5, 6, 7]) == True
def test_is_sorted_5():
    assert is_sorted([1, 3, 2, 4, 5, 6, 7]) == False, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_sorted_6():
    assert is_sorted([]) == True, 'This prints if this assert fails 2 (good for debugging!)'
def test_is_sorted_7():
    assert is_sorted([1]) == True, 'This prints if this assert fails 3 (good for debugging!)'
def test_is_sorted_8():
    assert is_sorted([3, 2, 1]) == False, 'This prints if this assert fails 4 (good for debugging!)'
def test_is_sorted_9():
    assert is_sorted([1, 2, 2, 2, 3, 4]) == False, 'This prints if this assert fails 5 (good for debugging!)'
def test_is_sorted_10():
    assert is_sorted([1, 2, 3, 3, 3, 4]) == False, 'This prints if this assert fails 6 (good for debugging!)'
def test_is_sorted_11():
    assert is_sorted([1, 2, 2, 3, 3, 4]) == True, 'This prints if this assert fails 7 (good for debugging!)'
def test_is_sorted_12():
    assert is_sorted([1, 2, 3, 4]) == True, 'This prints if this assert fails 8 (good for debugging!)'
