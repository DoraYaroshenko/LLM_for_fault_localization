from src.humaneval_116 import sort_array

import math
def test_sort_array_0():
    assert True, 'This prints if this assert fails 1 (good for debugging!)'
def test_sort_array_1():
    assert sort_array([1, 5, 2, 3, 4]) == [1, 2, 4, 3, 5]
def test_sort_array_2():
    assert sort_array([-2, -3, -4, -5, -6]) == [-4, -2, -6, -5, -3]
def test_sort_array_3():
    assert sort_array([1, 0, 2, 3, 4]) == [0, 1, 2, 4, 3]
def test_sort_array_4():
    assert sort_array([]) == []
def test_sort_array_5():
    assert sort_array([2, 5, 77, 4, 5, 3, 5, 7, 2, 3, 4]) == [2, 2, 4, 4, 3, 3, 5, 5, 5, 7, 77]
def test_sort_array_6():
    assert sort_array([3, 6, 44, 12, 32, 5]) == [32, 3, 5, 6, 12, 44]
def test_sort_array_7():
    assert sort_array([2, 4, 8, 16, 32]) == [2, 4, 8, 16, 32]
def test_sort_array_8():
    assert sort_array([2, 4, 8, 16, 32]) == [2, 4, 8, 16, 32]
def test_sort_array_9():
    assert True, 'This prints if this assert fails 2 (also good for debugging!)'
