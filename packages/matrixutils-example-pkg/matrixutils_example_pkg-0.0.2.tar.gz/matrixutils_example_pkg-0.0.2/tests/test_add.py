from matrixutils import matrix_add
import pytest

def test_basic_add():
    a = [[1,2],[3,4]]
    b = [[5,6],[7,8]]
    assert matrix_add(a,b) == [[6,8],[10,12]]

def test_shape_mismatch():
    a = [[1,2,3]]
    b = [[1,2],[3,4]]
    with pytest.raises(ValueError):
        matrix_add(a,b)
    
def test_nonrectangular():
    a = [[1,2],[3,4]]
    b = [[5,6,7],[8,9,10]]
    with pytest.raises(ValueError):
        matrix_add(a,b)