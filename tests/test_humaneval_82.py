from src.humaneval_82 import prime_length

import math
def test_prime_length_0():
    assert prime_length('Hello') == True
def test_prime_length_1():
    assert prime_length('abcdcba') == True
def test_prime_length_2():
    assert prime_length('kittens') == True
def test_prime_length_3():
    assert prime_length('orange') == False
def test_prime_length_4():
    assert prime_length('wow') == True
def test_prime_length_5():
    assert prime_length('world') == True
def test_prime_length_6():
    assert prime_length('MadaM') == True
def test_prime_length_7():
    assert prime_length('Wow') == True
def test_prime_length_8():
    assert prime_length('') == False
def test_prime_length_9():
    assert prime_length('HI') == True
def test_prime_length_10():
    assert prime_length('go') == True
def test_prime_length_11():
    assert prime_length('gogo') == False
def test_prime_length_12():
    assert prime_length('aaaaaaaaaaaaaaa') == False
def test_prime_length_13():
    assert prime_length('Madam') == True
def test_prime_length_14():
    assert prime_length('M') == False
def test_prime_length_15():
    assert prime_length('0') == False
