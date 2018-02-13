import pytest

from vegamite.utils.timeutil import parse_time_range

def test_parse_time_range():
	# import ipdb; ipdb.set_trace()
	test1 = parse_time_range('90 days')
	test2 = parse_time_range('1 month')

	assert test1.days == 90
	assert test2.days == 30

