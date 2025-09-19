# matrixutils_example_pkg

Minimal example Python package that implements matrix multiplication.

## Features
- `matrix_multiply(a, b)` multiplies two matrices represented as nested lists.
- Includes basic input validation and helpful errors.
- Tests included (pytest).

## Quickstart (local)
```bash
git clone <your-gitlab-repo-url>
cd matrixutils_example_pkg
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip build
python -m build
pip install dist/*.whl
python -c "from matrixutils import matrix_multiply; print(matrix_multiply([[1,2],[3,4]], [[5,6],[7,8]]))"
