from src.humaneval_76 import is_simple_power

import math
def test_is_simple_power_0():
    assert is_simple_power(16, 2) == True, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_simple_power_1():
    assert is_simple_power(143214, 16) == False, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_simple_power_2():
    assert is_simple_power(4, 2) == True, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_simple_power_3():
    assert is_simple_power(9, 3) == True, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_simple_power_4():
    assert is_simple_power(16, 4) == True, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_simple_power_5():
    assert is_simple_power(24, 2) == False, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_simple_power_6():
    assert is_simple_power(128, 4) == False, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_simple_power_7():
    assert is_simple_power(12, 6) == False, 'This prints if this assert fails 1 (good for debugging!)'
def test_is_simple_power_8():
    assert is_simple_power(1, 1) == True, 'This prints if this assert fails 2 (also good for debugging!)'
def test_is_simple_power_9():
    assert is_simple_power(1, 12) == True, 'This prints if this assert fails 2 (also good for debugging!)'
