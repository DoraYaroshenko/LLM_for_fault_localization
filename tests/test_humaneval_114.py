from src.humaneval_114 import minSubArraySum

import math
def test_minSubArraySum_0():
    assert minSubArraySum([2, 3, 4, 1, 2, 4]) == 1, 'This prints if this assert fails 1 (good for debugging!)'
def test_minSubArraySum_1():
    assert minSubArraySum([-1, -2, -3]) == -6
def test_minSubArraySum_2():
    assert minSubArraySum([-1, -2, -3, 2, -10]) == -14
def test_minSubArraySum_3():
    assert minSubArraySum([-9999999999999999]) == -9999999999999999
def test_minSubArraySum_4():
    assert minSubArraySum([0, 10, 20, 1000000]) == 0
def test_minSubArraySum_5():
    assert minSubArraySum([-1, -2, -3, 10, -5]) == -6
def test_minSubArraySum_6():
    assert minSubArraySum([100, -1, -2, -3, 10, -5]) == -6
def test_minSubArraySum_7():
    assert minSubArraySum([10, 11, 13, 8, 3, 4]) == 3
def test_minSubArraySum_8():
    assert minSubArraySum([100, -33, 32, -1, 0, -2]) == -33
def test_minSubArraySum_9():
    assert minSubArraySum([-10]) == -10, 'This prints if this assert fails 2 (also good for debugging!)'
def test_minSubArraySum_10():
    assert minSubArraySum([7]) == 7
def test_minSubArraySum_11():
    assert minSubArraySum([1, -1]) == -1
