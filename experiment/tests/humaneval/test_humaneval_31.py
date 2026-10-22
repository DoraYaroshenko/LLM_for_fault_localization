from src.humaneval_31 import is_prime

import math
def test_is_prime_0():
    assert is_prime(6) == False
def test_is_prime_1():
    assert is_prime(101) == True
def test_is_prime_2():
    assert is_prime(11) == True
def test_is_prime_3():
    assert is_prime(13441) == True
def test_is_prime_4():
    assert is_prime(61) == True
def test_is_prime_5():
    assert is_prime(4) == False
def test_is_prime_6():
    assert is_prime(1) == False
def test_is_prime_7():
    assert is_prime(5) == True
def test_is_prime_8():
    assert is_prime(11) == True
def test_is_prime_9():
    assert is_prime(17) == True
def test_is_prime_10():
    assert is_prime(5 * 17) == False
def test_is_prime_11():
    assert is_prime(11 * 7) == False
def test_is_prime_12():
    assert is_prime(13441 * 19) == False
