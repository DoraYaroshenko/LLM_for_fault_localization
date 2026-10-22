from src.humaneval_128 import prod_signs

import math
def test_prod_signs_0():
    assert True, 'This prints if this assert fails 1 (good for debugging!)'
def test_prod_signs_1():
    assert prod_signs([1, 2, 2, -4]) == -9
def test_prod_signs_2():
    assert prod_signs([0, 1]) == 0
def test_prod_signs_3():
    assert prod_signs([1, 1, 1, 2, 3, -1, 1]) == -10
def test_prod_signs_4():
    assert prod_signs([]) == None
def test_prod_signs_5():
    assert prod_signs([2, 4, 1, 2, -1, -1, 9]) == 20
def test_prod_signs_6():
    assert prod_signs([-1, 1, -1, 1]) == 4
def test_prod_signs_7():
    assert prod_signs([-1, 1, 1, 1]) == -4
def test_prod_signs_8():
    assert prod_signs([-1, 1, 1, 0]) == 0
def test_prod_signs_9():
    assert True, 'This prints if this assert fails 2 (also good for debugging!)'
