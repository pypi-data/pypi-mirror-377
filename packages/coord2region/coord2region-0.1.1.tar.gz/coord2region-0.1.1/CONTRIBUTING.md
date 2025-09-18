# Contributing

## Development environment

Install the package with its development extras:

```bash
pip install '.[dev]'
```

On shells like zsh, quoting the extras spec avoids glob expansion errors.

## Pre-commit, linting, and formatting

This project uses [pre-commit](https://pre-commit.com) with
[Ruff](https://github.com/astral-sh/ruff) to enforce PEP8 and NumPy-style
docstrings. All commits must pass the pre-commit checks.

Set up the git hook once:

```bash
pre-commit install
```

Run the checks on all files before committing:

```bash
pre-commit run --all-files
```

## Testing and coverage

Run the unit test suite with coverage. The project aims for at least 80%
coverage, which is enforced by Codecov:

```bash
pytest --cov
```

## Documentation

Write docstrings in [numpydoc](https://numpydoc.readthedocs.io) style. To build
the documentation, install the docs extras and run Sphinx:

```bash
pip install '.[docs]'
make -C docs html
```

## Versioning

This project follows [Semantic Versioning](https://semver.org). The
[setuptools_scm](https://github.com/pypa/setuptools_scm) plugin derives the
package version from Git tags, so no version is stored in the repository. To
update the version, create an annotated tag such as `vX.Y.Z`.

## How to release

1. Ensure checks pass:

   ```bash
   pre-commit run --all-files
   pytest --cov
   ```

2. Tag the release:

   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

## Code of Conduct and security

Please review our [Code of Conduct](CODE_OF_CONDUCT.md) and
[security policy](SECURITY.md) before contributing.
