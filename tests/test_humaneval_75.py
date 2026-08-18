from src.humaneval_75 import is_multiply_prime

import math
def test_is_multiply_prime_0():
    assert is_multiply_prime(5) == False
def test_is_multiply_prime_1():
    assert is_multiply_prime(30) == True
def test_is_multiply_prime_2():
    assert is_multiply_prime(8) == True
def test_is_multiply_prime_3():
    assert is_multiply_prime(10) == False
def test_is_multiply_prime_4():
    assert is_multiply_prime(125) == True
def test_is_multiply_prime_5():
    assert is_multiply_prime(3 * 5 * 7) == True
def test_is_multiply_prime_6():
    assert is_multiply_prime(3 * 6 * 7) == False
def test_is_multiply_prime_7():
    assert is_multiply_prime(9 * 9 * 9) == False
def test_is_multiply_prime_8():
    assert is_multiply_prime(11 * 9 * 9) == False
def test_is_multiply_prime_9():
    assert is_multiply_prime(11 * 13 * 7) == True
