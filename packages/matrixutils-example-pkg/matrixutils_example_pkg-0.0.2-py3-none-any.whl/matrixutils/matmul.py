from typing import List

Matrix = List[List[float]]

def matrix_multiply(a: Matrix, b: Matrix) -> Matrix:
    """Multiply two matrices a and b (as nested lists).

    Raises:
        ValueError: if matrices have incompatible dimensions or are malformed.

    Example:
        >>> matrix_multiply([[1,2],[3,4]], [[5,6],[7,8]])
        [[19, 22], [43, 50]]
    """
    # basic validation
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

    if a_cols != b_rows:
        raise ValueError(f"Incompatible dimensions: a is {a_rows}x{a_cols}, b is {b_rows}x{b_cols}")

    # compute product
    result = [[0 for _ in range(b_cols)] for _ in range(a_rows)]
    for i in range(a_rows):
        for j in range(b_cols):
            s = 0
            for k in range(a_cols):
                s += a[i][k] * b[k][j]
            result[i][j] = s
    return result
