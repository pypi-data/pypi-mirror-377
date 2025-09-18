# How to run test code
@author: huni1023

## General process
1. Create `.env` file
- see `.env.example` in root directory

2. run `test_rbridge.py`
this module checks installation of R packages (equateIRT and jsonlite).
```bash
pytest src/EqUMP/tests/test_rbridge.py
```

1. various commands to run test
you can choose `-vv`, `-s` options
```bash
pytest . # whole test
pytest -vv -s src/EqUMP/tests/test_*.py # specific module test
pytest -vv -s src/EqUMP/tests/test_*linking*.py::test_stocking_lord_scale_linking # specific function test
```

## Notes
- if you using `uv`, you can run test with `uv run pytest`
- if error raised about `ModuleNotfoundError` for `EqUMP`, run `pip install -e .`
