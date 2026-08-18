from src.humaneval_132 import is_nested

import math
def test_is_nested_0():
    assert is_nested('[[]]') == True, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_nested_1():
    assert is_nested('[]]]]]]][[[[[]') == False
def test_is_nested_2():
    assert is_nested('[][]') == False
def test_is_nested_3():
    assert is_nested('[]') == False
def test_is_nested_4():
    assert is_nested('[[[[]]]]') == True
def test_is_nested_5():
    assert is_nested('[]]]]]]]]]]') == False
def test_is_nested_6():
    assert is_nested('[][][[]]') == True
def test_is_nested_7():
    assert is_nested('[[]') == False
def test_is_nested_8():
    assert is_nested('[]]') == False
def test_is_nested_9():
    assert is_nested('[[]][[') == True
def test_is_nested_10():
    assert is_nested('[[][]]') == True
def test_is_nested_11():
    assert is_nested('') == False, 'This prints if this assert fails 2 (also good for debugging!)'
def test_is_nested_12():
    assert is_nested('[[[[[[[[') == False
def test_is_nested_13():
    assert is_nested(']]]]]]]]') == False
