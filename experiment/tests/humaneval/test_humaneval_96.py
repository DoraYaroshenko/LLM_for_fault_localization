from src.humaneval_96 import count_up_to

import math
def test_count_up_to_0():
    assert count_up_to(5) == [2, 3]
def test_count_up_to_1():
    assert count_up_to(6) == [2, 3, 5]
def test_count_up_to_2():
    assert count_up_to(7) == [2, 3, 5]
def test_count_up_to_3():
    assert count_up_to(10) == [2, 3, 5, 7]
def test_count_up_to_4():
    assert count_up_to(0) == []
def test_count_up_to_5():
    assert count_up_to(22) == [2, 3, 5, 7, 11, 13, 17, 19]
def test_count_up_to_6():
    assert count_up_to(1) == []
def test_count_up_to_7():
    assert count_up_to(18) == [2, 3, 5, 7, 11, 13, 17]
def test_count_up_to_8():
    assert count_up_to(47) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
def test_count_up_to_9():
    assert count_up_to(101) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
