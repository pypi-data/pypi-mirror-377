import collections
import enum
import sys
import typing
from typing import Annotated

import pytest

from typenames import (
    DEFAULT_REMOVE_MODULES,
    REMOVE_ALL_MODULES,
    TypenamesConfig,
    is_annotated_special_form,
    is_standard_collection_type_alias,
    is_typing_module_collection_alias,
    is_union_or_operator,
    is_union_special_form,
    parse_type_tree,
    typenames,
)

T = typing.TypeVar("T")


class MyClass:
    pass


class OuterClass:
    class InnerClass:
        pass


class MyGeneric(typing.Generic[T]):
    def __init__(self, x: T):
        self.x = x


class MyEnum(enum.Enum):
    MEMBER1 = "member1"
    MEMBER2 = "member2"


class MyTypedDict(typing.TypedDict):
    x: int
    y: int
    label: str


cases = [
    (int, "int"),
    (typing.List[int], "list[int]"),
    (typing.Tuple[str, int], "tuple[str, int]"),
    (MyClass, "tests.test_typenames.MyClass"),
    (OuterClass.InnerClass, "tests.test_typenames.OuterClass.InnerClass"),
    (typing.List[MyClass], "list[tests.test_typenames.MyClass]"),
    (typing.Dict[str, int], "dict[str, int]"),
    (typing.Any, "Any"),
    (typing.Dict[str, typing.Any], "dict[str, Any]"),
    (typing.Callable[..., str], "Callable[..., str]"),
    (typing.Callable[[int], str], "Callable[[int], str]"),
    (typing.Callable[[int, float], str], "Callable[[int, float], str]"),
    (MyGeneric[int], "tests.test_typenames.MyGeneric[int]"),
    (MyEnum, "tests.test_typenames.MyEnum"),
    # Forward references
    (typing.List["int"], "list[int]"),
    (typing.List["typing.Any"], "list[Any]"),
    (typing.List["enum.Enum"], "list[enum.Enum]"),
    (typing.List["MyClass"], "list[MyClass]"),
    (typing.List["OuterClass.InnerClass"], "list[OuterClass.InnerClass]"),
    # Python 3.8 adds typing.Literal, typing.Final, typing.TypedDict
    (typing.Literal["s", 0, MyEnum.MEMBER1], "Literal['s', 0, MyEnum.MEMBER1]"),
    (typing.Final[int], "Final[int]"),
    (MyTypedDict, "tests.test_typenames.MyTypedDict"),
    # Python 3.9 adds use of standard collection types as a generic in type annotations (PEP 585),
    # typing.Annotated
    (list[int], "list[int]"),
    (list[tuple[int, str]], "list[tuple[int, str]]"),
    (list[typing.Tuple[int, str]], "list[tuple[int, str]]"),
    (
        list[collections.defaultdict[str, list[int]]],
        "list[defaultdict[str, list[int]]]",
    ),
    (collections.abc.Mapping[str, str], "Mapping[str, str]"),
    # typing.Annotated is available in Python 3.9, or backported with typing_extensions
    (Annotated[str, "some metadata"], "str"),
    (Annotated[str, object()], "str"),
]

if sys.version_info < (3, 14):
    # Should preserve typing.Union and typing.Optional special forms
    cases.extend(
        [
            (
                typing.Optional[typing.List[MyClass]],
                "Optional[list[tests.test_typenames.MyClass]]",
            ),
            (typing.Union[float, int], "Union[float, int]"),
            (typing.Optional[int], "Optional[int]"),
            (typing.Optional[Annotated[str, "some metadata"]], "Optional[str]"),
            (typing.Optional[Annotated[str, object()]], "Optional[str]"),
        ]
    )
else:
    cases.extend(
        [
            (
                typing.Optional[typing.List[MyClass]],
                "list[tests.test_typenames.MyClass] | None",
            ),
            (typing.Union[float, int], "float | int"),
            (typing.Optional[int], "int | None"),
            (typing.Optional[Annotated[str, "some metadata"]], "str | None"),
            (typing.Optional[Annotated[str, object()]], "str | None"),
        ]
    )

if sys.version_info >= (3, 10):
    # Python 3.10 adds union syntax with the | operator (bitwise or),
    # typing.Concatenate, typing.ParamSpec, typing.TypeAlias
    cases.extend(
        [
            (int | str, "int | str"),
            (int | None, "int | None"),
            (None | int, "None | int"),
            (int | None | str, "int | None | str"),
        ]
    )

if sys.version_info >= (3, 11):
    # Python 3.11 adds typing.LiteralString, typing.Never, typing.Self
    cases.extend(
        [
            (typing.LiteralString, "LiteralString"),
            (typing.Never, "Never"),
            (typing.Self, "Self"),
        ]
    )


@pytest.mark.parametrize("case", cases, ids=[c[1] for c in cases])
def test_typenames(case):
    assert typenames(case[0]) == case[1]


def test_forward_ref_spurious_module():
    """Regression test that forward references should not spuriously include typing or
    annotationlib as a module name."""
    rendered = typenames(typing.List["int"], remove_modules=[])
    assert "typing.int" not in rendered
    assert "annotationlib.int" not in rendered


def test_remove_modules():
    # Simulate a class from another module
    class OtherModuleClass:
        __qualname__ = "OtherModuleClass"
        __module__ = "other_module"

    # Class defined in a function scope
    class FnScopeClass: ...

    # Default removal
    assert typenames(typing.Any) == "Any"
    assert typenames(MyClass) == "tests.test_typenames.MyClass"
    assert typenames(OtherModuleClass) == "other_module.OtherModuleClass"
    assert (
        typenames(FnScopeClass) == "tests.test_typenames.test_remove_modules.<locals>.FnScopeClass"
    )

    # Override
    config = TypenamesConfig(remove_modules=["tests.test_typenames"])
    assert typenames(typing.Any, config=config) == "typing.Any"
    assert typenames(MyClass, config=config) == "MyClass"
    assert typenames(OtherModuleClass, config=config) == "other_module.OtherModuleClass"
    assert typenames(FnScopeClass, config=config) == "test_remove_modules.<locals>.FnScopeClass"

    # Add to defaults
    config = TypenamesConfig(remove_modules=DEFAULT_REMOVE_MODULES + ["tests.test_typenames"])
    assert typenames(typing.Any, config=config) == "Any"
    assert typenames(MyClass, config=config) == "MyClass"
    assert typenames(OtherModuleClass, config=config) == "other_module.OtherModuleClass"
    assert typenames(FnScopeClass, config=config) == "test_remove_modules.<locals>.FnScopeClass"

    # All modules
    config = TypenamesConfig(remove_modules=REMOVE_ALL_MODULES)
    assert typenames(typing.Any, config=config) == "Any"
    assert typenames(MyClass, config=config) == "MyClass"
    assert typenames(OtherModuleClass, config=config) == "OtherModuleClass"
    assert typenames(OtherModuleClass, config=config) == "OtherModuleClass"
    assert typenames(FnScopeClass, config=config) == "FnScopeClass"

    assert typenames(collections.Counter[str], config=config) == "Counter[str]"
    assert typenames(collections.abc.Sequence[str], config=config) == "Sequence[str]"


def test_union_syntax_or_operator():
    """Test that forcing optional_syntax='or_operator' results in ... | ...."""
    assert typenames(typing.Union[int, str], union_syntax="or_operator") == "int | str"

    if sys.version_info >= (3, 10):
        assert typenames(int | str, union_syntax="or_operator") == "int | str"


def test_union_syntax_union_special_form():
    """Test that forcing optional_syntax='union_special_form' results in Union[...]"""
    assert typenames(typing.Union[int, str], union_syntax="special_form") == "Union[int, str]"

    if sys.version_info >= (3, 10):
        assert typenames(int | str, union_syntax="special_form") == "Union[int, str]"


def test_optional_syntax_or_operator():
    """Test that forcing optional_syntax='or_operator' results in ... | None."""
    assert typenames(typing.Optional[int], optional_syntax="or_operator") == "int | None"

    if sys.version_info >= (3, 10):
        assert typenames(int | None, union_syntax="or_operator") == "int | None"
        assert typenames(None | int, union_syntax="or_operator") == "None | int"


def test_optional_syntax_optional_special_form():
    """Test that forcing optional_syntax='optional_special_form' results in Optional[...]."""
    assert (
        typenames(typing.Optional[int], optional_syntax="optional_special_form") == "Optional[int]"
    )

    if sys.version_info >= (3, 10):
        assert typenames(int | None, optional_syntax="optional_special_form") == "Optional[int]"
        assert typenames(None | int, optional_syntax="optional_special_form") == "Optional[int]"


def test_optional_syntax_union_special_form():
    """Test that forcing optional_syntax='union_special_form' results in Union[...]."""
    assert (
        typenames(typing.Optional[int], optional_syntax="union_special_form") == "Union[int, None]"
    )

    if sys.version_info >= (3, 10):
        assert typenames(int | None, optional_syntax="union_special_form") == "Union[int, None]"
        assert typenames(None | int, optional_syntax="union_special_form") == "Union[None, int]"


def test_optional_multiple_params():
    """Test case that a type annotation resolves to the optional case but with multiple non-None
    parameters."""
    if sys.version_info < (3, 14):
        assert typenames(typing.Optional[typing.Union[int, str]]) == "Optional[Union[int, str]]"
    else:
        assert typenames(typing.Optional[typing.Union[int, str]]) == "int | str | None"

    if sys.version_info >= (3, 10):
        if sys.version_info < (3, 14):
            assert (
                typenames(int | str | None, optional_syntax="optional_special_form")
                == "Optional[Union[int, str]]"
            )
            assert (
                typenames(int | None | str, optional_syntax="optional_special_form")
                == "Optional[Union[int, str]]"
            )
        else:
            assert (
                typenames(int | str | None, optional_syntax="optional_special_form")
                == "Optional[int | str]"
            )
            assert (
                typenames(int | None | str, optional_syntax="optional_special_form")
                == "Optional[int | str]"
            )

        # union_syntax='or_operator'
        assert (
            typenames(
                int | None | str,
                optional_syntax="optional_special_form",
                union_syntax="or_operator",
            )
            == "Optional[int | str]"
        )


def test_standard_collection_syntax_as_given():
    """Test that setting standard_collection_syntax='as_given' keeps input syntax."""
    assert typenames(typing.List[int], standard_collection_syntax="as_given") == "List[int]"
    assert typenames(list[int], standard_collection_syntax="as_given") == "list[int]"


def test_standard_collection_syntax_typing_module():
    """Test that forcing standard_collection_syntax='typing_module' results in typing module
    generic aliases."""
    assert typenames(typing.List[int], standard_collection_syntax="typing_module") == "List[int]"
    assert typenames(list[int], standard_collection_syntax="typing_module") == "List[int]"


def test_annotated_include_extras():
    """Test that Annotated is included in the output when include_extras=True."""
    assert (
        typenames(Annotated[str, "some metadata"], include_extras=True)
        == "Annotated[str, 'some metadata']"
    )

    obj = object()
    assert typenames(Annotated[str, obj], include_extras=True) == f"Annotated[str, {obj}]"


def test_node_repr():
    assert repr(parse_type_tree(int)) == "<TypeNode <class 'int'>>"
    assert repr(parse_type_tree(typing.Any)) == "<TypeNode typing.Any>"
    if sys.version_info < (3, 14):
        assert repr(parse_type_tree(typing.Optional[int])) == (
            "<GenericNode typing.Union[<TypeNode <class 'int'>>, <TypeNode <class 'NoneType'>>]>"
        )
    else:
        assert repr(parse_type_tree(typing.Optional[int])) == (
            "<GenericNode <class 'typing.Union'>["
            "<TypeNode <class 'int'>>, <TypeNode <class 'NoneType'>>"
            "]>"
        )
    assert (
        repr(parse_type_tree(typing.Literal["a", "b"]))
        == "<GenericNode typing.Literal[<LiteralNode 'a'>, <LiteralNode 'b'>]>"
    )


is_union_special_form_cases = [
    (typing.Union[int, str], True),
    (typing.Optional[int], True),
    (typing.Union[typing.List[int], typing.Tuple[str, float]], True),
    (typing.Union[typing.Union[int, str], float], True),
    (typing.List[int], False),
    (typing.List[typing.Union[int, str]], False),
    (str, False),
    (type("Union", (), {}), False),
]


@pytest.mark.parametrize(
    "case",
    is_union_special_form_cases,
    ids=[str(c[0]) for c in is_union_special_form_cases],
)
def test_is_union_special_form(case):
    """Test that is_union_special_form correctly identifies if using typing.Union."""
    if sys.version_info < (3, 14):
        assert is_union_special_form(case[0]) == case[1]
    else:
        assert is_union_special_form(case[0]) is False


@pytest.mark.parametrize(
    "case",
    is_union_special_form_cases,
    ids=[str(c[0]) for c in is_union_special_form_cases],
)
def test_is_union_or_operator_for_typing_alias_cases(case):
    """Test that is_union_or_operator correctly returns False for all typing.Union test cases."""
    if sys.version_info < (3, 14):
        assert is_union_or_operator(case[0]) is False
    else:
        assert is_union_or_operator(case[0]) == case[1]


if sys.version_info >= (3, 10):
    # Python 3.10 adds | operator (bitwise or) for Union
    is_union_or_operator_cases = [
        (int | str, True),
        (int | None, True),
        (None | int, True),
        (int | str | float, True),
        (list[int] | tuple[str, float], True),
        (list[int | str], False),
    ]

    @pytest.mark.parametrize(
        "case",
        is_union_or_operator_cases,
        ids=[str(c[0]) for c in is_union_or_operator_cases],
    )
    def test_is_union_or_operator(case):
        """Test that is_union_or_operator correctly identifies cases using | operator."""
        assert is_union_or_operator(case[0]) == case[1]

    @pytest.mark.parametrize(
        "case",
        is_union_or_operator_cases,
        ids=[str(c[0]) for c in is_union_or_operator_cases],
    )
    def test_is_union_special_form_for_or_operator_cases(case):
        """Test that is_union_special_form correctly returns False for all | operator cases."""
        assert is_union_special_form(case[0]) is False


is_typing_module_collection_alias_cases = [
    (typing.List[int], True),
    (typing.Dict[str, int], True),
    (typing.Tuple[int, int], True),
    (typing.List[typing.Optional[int]], True),
    (typing.Dict[typing.Tuple[int, int], str], True),
    (int, False),
    (str, False),
    (typing.Optional[typing.List[int]], False),
    (typing.Union[typing.List[int], typing.List[str]], False),
    (collections.namedtuple("Point", ["x", "y"]), False),
]


@pytest.mark.parametrize(
    "case",
    is_typing_module_collection_alias_cases,
    ids=[str(c[0]) for c in is_typing_module_collection_alias_cases],
)
def test_is_typing_module_collection_alias(case):
    assert is_typing_module_collection_alias(case[0]) == case[1]


@pytest.mark.parametrize(
    "case",
    is_typing_module_collection_alias_cases,
    ids=[str(c[0]) for c in is_typing_module_collection_alias_cases],
)
def test_is_standard_collection_type_alias_for_typing_alias_cases(case):
    """Test that is_standard_collection_type_alias correctly returns False for all typing module
    alias cases."""
    assert is_standard_collection_type_alias(case[0]) is False


# Python 3.9 adds generic aliases for standard collections
is_standard_collection_type_alias_cases = [
    (list[int], True),
    (dict[str, int], True),
    (tuple[int, int], True),
    (list[typing.Optional[int]], True),
    (dict[tuple[int, int], str], True),
    (dict[typing.Tuple[int, int], str], True),
    (typing.Optional[list[int]], False),
    (typing.Union[list[int], list[str]], False),
]


@pytest.mark.parametrize(
    "case",
    is_standard_collection_type_alias_cases,
    ids=[str(c[0]) for c in is_standard_collection_type_alias_cases],
)
def test_is_standard_collection_type_alias(case):
    assert is_standard_collection_type_alias(case[0]) == case[1]


@pytest.mark.parametrize(
    "case",
    is_standard_collection_type_alias_cases,
    ids=[str(c[0]) for c in is_standard_collection_type_alias_cases],
)
def test_is_typing_module_collection_alias_for_collection_types(case):
    """Test that is_typing_module_collection_alias correctly returns False for all standard
    collection type aliases."""
    assert is_typing_module_collection_alias(case[0]) is False


def test_nested_collection_types_nested_both():
    """Test that is_typing_module_collection_alias and is_standard_collection_type_alias
    correctly identify nested cases using both typing approaches."""
    tp1 = typing.Dict[tuple[int, int], str]
    assert is_typing_module_collection_alias(tp1) is True
    assert is_standard_collection_type_alias(tp1) is False

    tp2 = dict[typing.Tuple[int, int], str]
    assert is_typing_module_collection_alias(tp2) is False
    assert is_standard_collection_type_alias(tp2) is True


def test_annotated():
    assert is_annotated_special_form(Annotated[str, "some metadata"]) is True
    assert is_annotated_special_form(Annotated[str, object()]) is True
