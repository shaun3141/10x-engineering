#Add test case to check if sorting list parameter is being properly handled
def test_sum_numbers_sorting():
    assert sum_numbers([4,2,3], True) == 9
    assert sum_numbers([4,2,3], False) == 9
    assert sum_numbers([9,8,7,6,5], True) == 35
    assert sum_numbers([9,8,7,6,5], False) == 35
