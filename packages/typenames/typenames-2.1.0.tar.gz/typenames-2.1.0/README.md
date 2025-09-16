# typenames : String representations of type annotations

[![Docs Status](https://img.shields.io/badge/docs-stable-informational)](https://typenames.drivendata.org/)
[![PyPI](https://img.shields.io/pypi/v/typenames.svg)](https://pypi.org/project/typenames/)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/typenames.svg)](https://github.com/conda-forge/typenames-feedstock)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/typenames)](https://pypi.org/project/typenames/)
[![tests](https://github.com/drivendataorg/typenames/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/drivendataorg/typenames/actions/workflows/tests.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/drivendataorg/typenames/branch/main/graph/badge.svg)](https://codecov.io/gh/drivendataorg/typenames)

**typenames** is a configurable Python library for creating string representations of type annotations. By default, it produces compact representations by removing standard library module names. Configurable options include standardizing on `|` operator syntax for unions or standard collections classes for generics.

```python
import typing
from typenames import typenames

typenames(int)
#> 'int'
typenames(dict[str, typing.Any])
#> 'dict[str, Any]'
typenames(str | int)
#> 'str | int'
typenames(typing.Optional[str])
#> 'Optional[str]'
```

## Why use this library?

String representations of Python type objects, type aliases, and special typing forms are inconsistent and often verbose. Here are some comparisons using default settings against built-in string representations:

| Input | With `str(...)` | With `typenames(...)` |
| :-: | :-: | :-: |
| `int` | `<class 'int'>` | `int` |
| `list` | `<class 'list'>` | `list` |
| `typing.Optional[int]` | `typing.Optional[int]` | `Optional[int]` |
| `collections.abc.Iterator[typing.Any]` | `collections.abc.Iterator[typing.Any]` | `Iterator[Any]` |
| `typing.Literal[MyEnum.NAME]` | `typing.Literal[<MyEnum.NAME: 'value'>]` | `Literal[MyEnum.NAME]` |

typenames also has handy configurable functionality, such as:

- Forcing standardization on `|` operator union syntax (e.g., `Union[int, str]` to `int | str`) or vice versa
- Forcing standardization on `|` operator optional syntax (e.g., `Optional[int]` to `int | None`) or vice versa
- Forcing standardization on standard collection types for generics (e.g., `List[int]` to `list[int]`) or vice versa
- Controlling exactly which module names to remove using regex patterns.

No need for string manipulation to get what you want!

## Installation

typenames is available on [PyPI](https://pypi.org/project/typenames/):

```bash
pip install typenames
```

It is also available on [conda-forge](https://github.com/conda-forge/typenames-feedstock):

```bash
conda install typenames --channel conda-forge
```

## Basic Usage

The main way to use the library is the `typenames` function. Calling it on a type annotation renders a string representation:

```python
import collections.abc
import typing
from typenames import typenames

typenames(int)
#> 'int'
typenames(typing.Optional[str])
#> 'Optional[str]'
typenames(collections.abc.Callable[[int], tuple[str, ...]])
#> 'Callable[[int], tuple[str, ...]]
```

Under the hood, typenames parses a type annotation as a tree structure. If you need to see the parsed tree, use the `parse_type_tree` function to return the root node. You can get the rendered string representation by calling `str(...)` on root node.

```python
import typing
from typenames import parse_type_tree

tree = parse_type_tree(typing.Union[typing.Any, list[typing.Any]])
tree
#> <GenericNode typing.Union[<TypeNode typing.Any>, <GenericNode <class 'list'>[<TypeNode typing.Any>]>]>
str(tree)
#> 'Union[Any, list[Any]]'
```

## Configurable options

All configuration options can be passed as keyword arguments to either the `typenames` or `parse_type_tree` functions.

### Union Syntax (`union_syntax`)

This option controls how unions are rendered. It supports both the `typing.Union` special form and the `|` operator (bitwise or) syntax from [PEP 604](https://peps.python.org/pep-0604/). Valid options are defined by the enum `UnionSyntax` and include:

- **`"as_given"` (default)**: render the union as it is given without changing syntax.
- **`"or_operator"`**: render all type unions using the `|` operator.
- **`"special_form"`**: render all type unions using the `typing.Union` special form.

> [!NOTE]
> Runtime use of the `|` operator between types is new in Python 3.10. To use in earlier versions of Python, you will need to use postponed evaluation of annotations à la [PEP 563](https://peps.python.org/pep-0563/) with `from __future__ import__annotations__`. Support for the `|` operator is only a limitation on providing type annotation inputs to typenames, and not a limitation on output rendering.

> [!NOTE]
> In Python 3.14, the `typing.Union` special form and the `types.Union` type (produced by the `|` operator) have been [unified into a single implementation](https://docs.python.org/3.14/whatsnew/3.14.html#whatsnew314-typing-union). This means that both will always be rendered with the `|` operator when using `as_given`, as their created instances are no longer distinguishable.

> [!IMPORTANT]
> **Limitations:** Python automatically flattens unions when evaluating them at runtime. Since typenames uses runtime type objects, it will only see the flattened result and not know if your original input was nested. Furthermore, any mixing of `|` operator syntax and any typing module types will result in a `typing.Union` union, so `as_given` will always render such inputs with `typing.Union`.


### Optional Syntax (`optional_syntax`)

This option controls how optional types are rendered. It supports both the `typing.Optional` special form and the `|` operator (bitwise or) syntax from [PEP 604](https://peps.python.org/pep-0604/). Valid options are defined by the enum `OptionalSyntax` and include:

- **`"as_given"` (default)**: render the optional type as it is given without changing syntax
- **`"or_operator"`**: render all optional types using the `|` operator
- **`"union_special_form"`**: render all optional types using the `typing.Optional` special form
- **`"optional_special_form"`**: render all optional types using the `typing.Optional` special form

> [!NOTE]
> Runtime use of the `|` operator between types is new in Python 3.10. To use in earlier versions of Python, you will need to use postponed evaluation of annotations à la [PEP 563](https://peps.python.org/pep-0563/) with `from __future__ import__annotations__`. Support for the `|` operator is only a limitation on providing type annotation inputs to typenames, and not a limitation on output rendering.

> [!NOTE]
> In Python 3.14, the `typing.Optional` special form no longer produces a `typing.Optional` type object; instead, it produces a `Union` object. Additionally, the `typing.Union` special form and the `types.Union` type (produced by the `|` operator) have been [unified into a single implementation](https://docs.python.org/3.14/whatsnew/3.14.html#whatsnew314-typing-union). This means that all syntaxes for optional types will be rendered with the `|` operator when using `as_given`, as their created instances are no longer distinguishable.

> [!IMPORTANT]
> **Limitations:**
>
> - Python automatically converts `typing.Union[..., None]` to `typing.Optional[...]` when evaluating at runtime. Since typenames uses runtime type objects, it will only see the result using `typing.Optional` and not know the form of your original input.
> - Python automatically flattens unions when evaluating them at runtime. Since typenames uses runtime type objects, it will only see the flattened result and not know if your original input was nested. Furthermore, any mixing of `|` operator syntax and any typing module types will result in a `typing.Union` union, so `as_given` will always render such inputs with typing module special forms.
> - The `typing.Optional` special form only accepts exactly one parameter. By default, typenames will render cases with multiple parameters with `Optional[Union[...]]`. You can use the `union_syntax` option to control the inner union's syntax.


### Standard Collection Syntax (`standard_collection_syntax`)

_Default value changed in v2.0.0_

This option controls how parameterized standard collection generic types are rendered. It supports both the typing module's generic aliases (e.g., `typing.List[...]`) and the standard class (e.g., `list[...]`) syntax from [PEP 585](https://peps.python.org/pep-0585/). Valid options are defined by the enum `StandardCollectionSyntax` and include:

- **`"standard_class"` (default)**: render all parameterized standard collection generic types using their class
- **`"as_given"`**: render the parameterized generic type as it is given without changing syntax
- **`"typing_module"`**: render all parameterized standard collection generic types using the typing module's generic alias

> [!NOTE]
> The typing module's generic aliases are [deprecated](https://docs.python.org/3/library/typing.html#deprecated-aliases) in favor of parameterizing standard collection classes. Parameterizing standard collection classes was added in Python 3.9 and is available in all currently supported versions of Python.

### Removing Module Names (`remove_modules`)

This option controls how module names are removed from the rendered output. It takes a list of inputs, which can either be a string of the module name or a `re.Pattern` regex pattern directly (the result of `re.compile`). String inputs are templated into the following regex pattern:

```python
module: str  # Given module name
re.compile(r"^{}\.".format(module.replace(".", r"\.")))
```

Note that module names are removed in the given order, so having entries that are submodules of other entries can potentially lead to the wrong behavior. You can either order them from higher-depth to lower-depth, or directly provide a compiled pattern with optional groups. For example, the pattern `re.compile(r"^collections\.(abc\.)?")` will match both `"collections."` and `"collections.abc."`.

The default list of module names include the standard library modules relevant to [PEP 585](https://peps.python.org/pep-0585/) plus `types` and `typing`. It can be accessed at `DEFAULT_REMOVE_MODULES`.

```python
DEFAULT_REMOVE_MODULES: List[Union[str, re.Pattern]] = [
    "__main__",
    "builtins",
    re.compile(r"^collections\.(abc\.)?"),
    "contextlib",
    "re",
    "types",
    "typing",
]
```

If you are trying to _add_ additional modules to this option (rather than overriding the defaults), the easiest way to do so is to concatenate with the default list:

```python
from typing import Optional
from typenames import typenames, DEFAULT_REMOVE_MODULES, BaseNode

# Default removals
typenames(Optional[BaseNode])
#> 'Optional[typenames.BaseNode]'

# Replace default with 'typenames'
typenames(Optional[BaseNode], remove_modules=["typenames"])
#> 'typing.Optional[BaseNode]'

# Extend default with 'typenames'
typenames(
    Optional[BaseNode],
    remove_modules=DEFAULT_REMOVE_MODULES + ["typenames"],
)
#> 'Optional[BaseNode]'
```

To remove all module names, you can use `REMOVE_ALL_MODULES`, which contains the pattern `re.compile(r"^(<?\w+>?\.)+")`.

### Annotated (`include_extras`)

This option controls whether to render `Annotated` and the extra metadata. `typing.Annotated` is a [typing special form](https://docs.python.org/3/library/typing.html#typing.Annotated) introduced in Python 3.9 and originally specified by [PEP 593](https://peps.python.org/pep-0593/). Many libraries like [Pydantic](https://docs.pydantic.dev/latest/concepts/fields/#using-annotated), [FastAPI](https://fastapi.tiangolo.com/python-types/#type-hints-with-metadata-annotations), and [Typer](https://typer.tiangolo.com/tutorial/arguments/optional/#an-alternative-cli-argument-declaration) use it to attach metadata to type annotations that are used at runtime.

By default, typenames will _not_ render `Annotated` and extra metadata. Set `include_extras=True` to render them.

```python
from typing import Annotated
from typenames import typenames

typenames(Annotated[int, "some metadata"])
#> 'int'
typenames(Annotated[int, "some metadata"], include_extras=True)
#> "Annotated[int, 'some metadata']"
```

---

<sup>Reproducible examples created by <a href="https://github.com/jayqi/reprexlite">reprexlite</a>.</sup>
