from src.humaneval_150 import x_or_y

import math
def test_x_or_y_0():
    assert x_or_y(7, 34, 12) == 34
def test_x_or_y_1():
    assert x_or_y(15, 8, 5) == 5
def test_x_or_y_2():
    assert x_or_y(3, 33, 5212) == 33
def test_x_or_y_3():
    assert x_or_y(1259, 3, 52) == 3
def test_x_or_y_4():
    assert x_or_y(7919, -1, 12) == -1
def test_x_or_y_5():
    assert x_or_y(3609, 1245, 583) == 583
def test_x_or_y_6():
    assert x_or_y(91, 56, 129) == 129
def test_x_or_y_7():
    assert x_or_y(6, 34, 1234) == 1234
def test_x_or_y_8():
    assert x_or_y(1, 2, 0) == 0
def test_x_or_y_9():
    assert x_or_y(2, 2, 0) == 2
