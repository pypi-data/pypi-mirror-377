#TESTS (pytest)
# tests/test_core.py
import pytest
from my_calculator import add, sub, mul, div

def test_add():
    assert add(1, 2) == 3

def test_sub():
    assert sub(5, 3) == 2

def test_mul():
    assert mul(2, 4) == 8

def test_div():
    assert div(10, 2) == 5

def test_div_zero():
    with pytest.raises(ZeroDivisionError):
        div(1, 0)
