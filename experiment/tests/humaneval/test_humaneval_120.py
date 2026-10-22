from src.humaneval_120 import maximum

import math
def test_maximum_0():
    assert maximum([-3, -4, 5], 3) == [-4, -3, 5]
def test_maximum_1():
    assert maximum([4, -4, 4], 2) == [4, 4]
def test_maximum_2():
    assert maximum([-3, 2, 1, 2, -1, -2, 1], 1) == [2]
def test_maximum_3():
    assert maximum([123, -123, 20, 0, 1, 2, -3], 3) == [2, 20, 123]
def test_maximum_4():
    assert maximum([-123, 20, 0, 1, 2, -3], 4) == [0, 1, 2, 20]
def test_maximum_5():
    assert maximum([5, 15, 0, 3, -13, -8, 0], 7) == [-13, -8, 0, 0, 3, 5, 15]
def test_maximum_6():
    assert maximum([-1, 0, 2, 5, 3, -10], 2) == [3, 5]
def test_maximum_7():
    assert maximum([1, 0, 5, -7], 1) == [5]
def test_maximum_8():
    assert maximum([4, -4], 2) == [-4, 4]
def test_maximum_9():
    assert maximum([-10, 10], 2) == [-10, 10]
def test_maximum_10():
    assert maximum([1, 2, 3, -23, 243, -400, 0], 0) == []
