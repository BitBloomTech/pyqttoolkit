# PyQtToolkit

A toolkit for PyQt

## Development and packaging

Use Python 3.14 or newer. Install the optional Qt bindings when developing UI
features; installing the base package does not install PyQt5.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install '.[ui,test,publish]'
python -m tox -e py314
python -m build
python -m twine check --strict dist/*
```

The isolated build backend uses setuptools and the bundled Versioneer code to
produce a wheel and source distribution. Build from a Git checkout or an unpacked
source distribution so the release version can be determined. The `publish` extra
provides the build and upload tools; it is not needed by library consumers.

The tox environment runs the full Qt test suite offscreen, including the task-runner
tests, and checks package license headers. See [the validation report](docs/dependency-validation.md)
for tested dependency versions, platform limits and source-review boundaries.
