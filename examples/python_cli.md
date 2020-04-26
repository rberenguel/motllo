# Tree structure

This represents the folder structure we want to generate. The links section
below is just a helper and not semantically needed to create the template (the
tree representation inside of a code block is needed, and the section needs to
be named _Tree structure_ exactly). It doesn't necessarily needs to be the
first, but I'd look you bad if you move it.

### Replacements

- `project_name`: `PROJECT`

Replacements are applied per section. Replacements are of the form
`key:key_in_code`, in a bullet list. Replacements for the tree structure are
also applied to the section names, so make sure to adapt the file name sections
accordingly.

```
├── paquefile.yaml
├── pyproject.toml
├── tests
│   └── test_version.py
├── README.md
├── .gitignore
├── PROJECT
│   ├── __init__.py
│   └── main.py
└── pylintrc
```

- [`paquefile.yaml`](#paquefileyaml)
- [`pyproject.toml`](#pyprojecttoml)
- `tests`
    - [`test_version.py`](#teststest_version)
- [`README.md`](#readmemd)
- [`.gitignore`](#gitignore)
- `PROJECT`
    - [`__init__.py`](#project__init__py)
    - [`main.py`](#projectmainpy)
- [`pylintrc`](#pylintrc)
- [`poetry.lock`](#poetrylock)


# `paquefile.yaml`

[Paque](https://github.com/rberenguel/paque) is a personal project I use for
building stuff. Why not?

### Replacements

- `project_name`:`$PROJ`

```yaml
isort:
  - run: "isort $PROJ/*.py"
  - message: "Running isort"

mypy:
  - run: "mypy $PROJ"
  - message: "Running mypy"

black:
  - run:
      - "black $PROJ"
      - "black tests"
  - message: "Running black on source and tests"

pytest:
  - run: "pytest -x"
  - message: "Running pytest"

pylint:
  - run: "pylint $PROJ --exit-zero"
  - message: "Running pylint"

precommit:
  - depends:
      - isort
      - mypy
      - black
      - pylint
      - pytest

monkeytype-run:
  - run: "monkeytype run $PROJ/main.py"
  - message: "Runs monkeytype"

monkeytype-stubs:
  - run:
      - "monkeytype stub $PROJ.main"
  - message: "Generates stubs for the base modules"

monkeytype:
  - depends:
      - monkeytype-run
      - monkeytype-stubs
```

# `pyproject.toml`

A basic initial
[`pyproject`](https://www.python.org/dev/peps/pep-0518/#specification) file to
use with [Poetry](https://python-poetry.org)

### Replacements

- `project_name`: `PROJECT`

```toml
[tool.poetry]
name = "PROJECT"
version = "0.1.0"
description = "This intentionally left blank"
authors = ["Ruben Berenguel <ruben+poetry@mostlymaths.net>"]
license = "MIT"
readme = "README.md"

repository = "https://github.com/rberenguel/PROJECT"

[tool.poetry.dependencies]
python = "^3.7"
colorlog = "^4.1.0"
click = "^7.1.1"

[tool.poetry.dev-dependencies]
pytest = "^5.2"
pylint = "^2.4.4"
flake8 = "^3.7.9"
isort = "^4.3.21"
black = "^19.10b0"
mypy = "^0.770"
monkeytype = "^19.11.2"
paque = "^0.1.0"

[tool.poetry.scripts]
PROJECT = 'PROJECT.main:main'

[build-system]
requires = ["poetry>=0.12"]
build-backend = "poetry.masonry.api"
```

# `tests/test_version.py`

### Replacements

The point of having per-section replacements, is that you can use naming that
"looks good" in the specific language/syntax of the code block.

- `project_name`: `_PROJ_`

```python
import pytest

from _PROJ_ import __version__

def test_version():
    assert __version__ == "0.1.0"
```

# `README.md`

### Replacements

- `project_name`: `PROJECT`

```
# PROJECT

This is project PROJECT
```

# `.gitignore`

### Replacements

- `project_name`: `PROJECT`

```
dist
PROJECT.egg-info
```

# `PROJECT/__init__.py`

See how here the title has a replacement used in the [tree structure replacement
section](#replacements). This ensures this "file" eventually matches "the file
described in the structure".

```python
__version__ = "0.1.0"
```


# `PROJECT/main.py`

A bare-bones `main.py` with logging set up how I like it, and a basic click
setup. If I'm not going to work in a CLI tool, I'd delete this

### Replacements

- `project_name`: `$PROJ_`

```python
import logging

import click
from colorlog import ColoredFormatter  # type: ignore

logger = logging.getLogger("$PROJ")

def configure_logger():
    """Fancy logging is nicer"""
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "yellow",
            "INFO": "cyan",
            "WARNING": "purple",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@click.group()
@click.option('--debug', help="Set log level to debug", is_flag=True)
@click.pass_context
def cli(debug):
    """This is project $PROJ
    """
    configure_logger()
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


@cli.command()
def main():
    """Does something"""


if __name__ == "__main__":
    cli()
```

# `pylintrc`

These are my main pet-peeves with `pylint` ([`black`](https://github.com/psf/black) causes `bad-continuation`)

```
[MESSAGES CONTROL]

disable=line-too-long,too-few-public-methods,missing-module-docstring,bad-continuation
good-names=logger
```
