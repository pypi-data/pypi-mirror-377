# typed_classproperties

![Pydowndoc](https://img.shields.io/badge/%F0%9F%A5%95-typed__classproperties-blue)
![PyPI Version](https://img.shields.io/pypi/v/typed_classproperties)
![Python Version](https://img.shields.io/pypi/pyversions/typed_classproperties?logo=Python&logoColor=white&label=Python)
![Tests Status](https://github.com/CarrotManMatt/typed_classproperties/actions/workflows/check-build-publish.yaml/badge.svg)
![mypy Status](https://img.shields.io/badge/mypy-checked-%232EBB4E&label=mypy)
![pre-commit Status](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)

Typed decorators for `classproperty` and `cached_classproperty`.

***Python 3 compatible only****. **No dependencies***footnote:[The library `[typing_extensions](https://github.com/python/typing_extensions)` is required when running with [Python](https://python.org) &lt; 3.12].

## Installation

This package is hosted on [PyPI](https://pypi.org) and can be installed using
[uv](https://astral.sh/uv) or [pip](https://pip.pypa.io).

**Add to your [uv project/script’s dependencies](https://docs.astral.sh/uv/concepts/projects#managing-dependencies)**

uv add typed_classproperties

**Install using [pip](https://pip.pypa.io) after [creating a virtual environment](https://docs.python.org/3/tutorial/venv)**

path/to/venv/python -m pip install typed_classproperties

## Example Usage

```python
from typing import override

from typed_classproperties import classproperty, cached_classproperty


class Foo:
    @override
    def __init__(self, bar: str) -> None:
        self.bar: str = bar

    @classproperty
    def BAR(cls) -> int:
        return 1


assert Foo.BAR == 1
assert Foo(bar="one").BAR == 1


class CachedFoo:
    @override
    def __init__(self, bar: str) -> None:
        self.bar: str = bar

    @cached_classproperty
    def BAR(cls) -> int:
        print("This will be executed only once")
        return 1


assert CachedFoo.BAR == 1
assert CachedFoo(bar="bar").FOO == 1
```

## Tests

See [tests.py](tests.py) for further usage examples and expected behaviour.

**To run tests**

uv run --group test -- pytest

## Credits

Credits to Denis Ryzhkov, on Stack Overflow, for the original implementation of the `@classproperty` decorator:
https://stackoverflow.com/a/13624858/1280629
