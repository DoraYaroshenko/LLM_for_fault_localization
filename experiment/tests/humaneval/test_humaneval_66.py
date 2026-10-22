from src.humaneval_66 import digitSum

import math
def test_digitSum_0():
    assert True, 'This prints if this assert fails 1 (good for debugging!)'
def test_digitSum_1():
    assert digitSum('') == 0, 'Error'
def test_digitSum_2():
    assert digitSum('abAB') == 131, 'Error'
def test_digitSum_3():
    assert digitSum('abcCd') == 67, 'Error'
def test_digitSum_4():
    assert digitSum('helloE') == 69, 'Error'
def test_digitSum_5():
    assert digitSum('woArBld') == 131, 'Error'
def test_digitSum_6():
    assert digitSum('aAaaaXa') == 153, 'Error'
def test_digitSum_7():
    assert True, 'This prints if this assert fails 2 (also good for debugging!)'
def test_digitSum_8():
    assert digitSum(' How are yOu?') == 151, 'Error'
def test_digitSum_9():
    assert digitSum('You arE Very Smart') == 327, 'Error'
