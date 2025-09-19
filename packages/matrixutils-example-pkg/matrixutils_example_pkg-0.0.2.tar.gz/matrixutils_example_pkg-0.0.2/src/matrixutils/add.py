from typing import List

Matrix = List[List[float]]

def matrix_add(a: Matrix, b: Matrix) -> Matrix:
    """Element-wise addition of two matrices represented as nested lists.

    Raises:
        ValueError: if matrices are empty, non-rectangular, or shapes differ.

    Example:
        >>> matrix_add([[1,2],[3,4]], [[5,6],[7,8]])
        [[6, 8], [10, 12]]
    """
    if not a or not b:
        raise ValueError("Input matrices must be non-empty")
    if not all(isinstance(row, list) and row for row in a):
        raise ValueError("Matrix 'a' must be a list of non-empty rows")
    if not all(isinstance(row, list) and row for row in b):
        raise ValueError("Matrix 'b' must be a list of non-empty rows")

    a_rows = len(a)
    a_cols = len(a[0])
    b_rows = len(b)
    b_cols = len(b[0])

    if any(len(row) != a_cols for row in a):
        raise ValueError("All rows in matrix 'a' must have the same length")
    if any(len(row) != b_cols for row in b):
        raise ValueError("All rows in matrix 'b' must have the same length")

    if (a_rows, a_cols) != (b_rows, b_cols):
        raise ValueError(f"Matrices must have the same shape: got {a_rows}x{a_cols} and {b_rows}x{b_cols}")

    return [[a[i][j] + b[i][j] for j in range(a_cols)] for i in range(a_rows)]
