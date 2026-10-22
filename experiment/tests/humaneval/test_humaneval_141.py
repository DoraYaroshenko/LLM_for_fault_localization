from src.humaneval_141 import file_name_check

import math
def test_file_name_check_0():
    assert file_name_check('example.txt') == 'Yes'
def test_file_name_check_1():
    assert file_name_check('1example.dll') == 'No'
def test_file_name_check_2():
    assert file_name_check('s1sdf3.asd') == 'No'
def test_file_name_check_3():
    assert file_name_check('K.dll') == 'Yes'
def test_file_name_check_4():
    assert file_name_check('MY16FILE3.exe') == 'Yes'
def test_file_name_check_5():
    assert file_name_check('His12FILE94.exe') == 'No'
def test_file_name_check_6():
    assert file_name_check('_Y.txt') == 'No'
def test_file_name_check_7():
    assert file_name_check('?aREYA.exe') == 'No'
def test_file_name_check_8():
    assert file_name_check('/this_is_valid.dll') == 'No'
def test_file_name_check_9():
    assert file_name_check('this_is_valid.wow') == 'No'
def test_file_name_check_10():
    assert file_name_check('this_is_valid.txt') == 'Yes'
def test_file_name_check_11():
    assert file_name_check('this_is_valid.txtexe') == 'No'
def test_file_name_check_12():
    assert file_name_check('#this2_i4s_5valid.ten') == 'No'
def test_file_name_check_13():
    assert file_name_check('@this1_is6_valid.exe') == 'No'
def test_file_name_check_14():
    assert file_name_check('this_is_12valid.6exe4.txt') == 'No'
def test_file_name_check_15():
    assert file_name_check('all.exe.txt') == 'No'
def test_file_name_check_16():
    assert file_name_check('I563_No.exe') == 'Yes'
def test_file_name_check_17():
    assert file_name_check('Is3youfault.txt') == 'Yes'
def test_file_name_check_18():
    assert file_name_check('no_one#knows.dll') == 'Yes'
def test_file_name_check_19():
    assert file_name_check('1I563_Yes3.exe') == 'No'
def test_file_name_check_20():
    assert file_name_check('I563_Yes3.txtt') == 'No'
def test_file_name_check_21():
    assert file_name_check('final..txt') == 'No'
def test_file_name_check_22():
    assert file_name_check('final132') == 'No'
def test_file_name_check_23():
    assert file_name_check('_f4indsartal132.') == 'No'
def test_file_name_check_24():
    assert file_name_check('.txt') == 'No'
def test_file_name_check_25():
    assert file_name_check('s.') == 'No'
