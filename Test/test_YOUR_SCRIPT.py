import pytest
import sys

sys.path.append('/Users/kedjoshi/Desktop/venv')

from venv.__main__ import *

complement(255,0,255)

def test_file1_method1():
	x=6
	y=6
	assert x+1 == y,"test failed"
	assert x == y,"test failed"
def test_file1_method2():
	x=6
	y=6
	assert x+1 == y,"test failed"