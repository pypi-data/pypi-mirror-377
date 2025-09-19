from matrixutils import matrix_multiply
import pytest

def test_basic():
    a = [[1,2],[3,4]]
    b = [[5,6],[7,8]]
    assert matrix_multiply(a,b) == [[19,22],[43,50]]

def test_incompatible():
    a = [[1,2,3]]
    b = [[1,2],[3,4]]
    with pytest.raises(ValueError):
        matrix_multiply(a,b)

def test_non_rectangular():
    a = [[1,2],[3]]
    b = [[1],[2]]
    with pytest.raises(ValueError):
        matrix_multiply(a,b)
