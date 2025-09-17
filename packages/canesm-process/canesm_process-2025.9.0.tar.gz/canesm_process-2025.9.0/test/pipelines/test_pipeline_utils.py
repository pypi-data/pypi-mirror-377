from canproc.pipelines.utils import (
    merge_lists,
    check_merge,
    merge_destination,
    MergeException,
    replace_constants,
    AstParser,
)
import xarray as xr
import ast
import pytest


def test_merge_lists_same():

    # full overlap, output = a = b
    a = ["a", "b", "c"]
    b = ["a", "b", "c"]
    assert merge_lists(a, b) == ["a", "b", "c"]


def test_merge_lists_no_overlap():
    # no strict order between a and b list, but order must be preserved of individual elements
    a = ["a", "b", "c"]
    b = ["d", "e", "f"]
    out = merge_lists(a, b)
    assert out.index("a") < out.index("b")
    assert out.index("b") < out.index("c")
    assert out.index("d") < out.index("e")
    assert out.index("e") < out.index("f")


def test_merge_lists_partial_overlap():
    # c must come after b
    a = ["a", "b", "d", "e"]
    b = ["b", "c"]
    out = merge_lists(a, b)
    assert out.index("a") < out.index("b")
    assert out.index("b") < out.index("c")
    assert out.index("b") < out.index("d")
    assert out.index("d") < out.index("e")


def test_dict_merge():

    assert check_merge({"rename": "good"}, {"rename": "good"})
    assert check_merge({"rename": "good"}, {"scale": 7})

    with pytest.raises(MergeException):
        check_merge({"rename": "good"}, {"rename": "bad"})


def test_destination_merge():

    d1 = {"destination": None}
    d2 = {"rename": "GT"}
    merge_destination(d1, d2)
    assert d2 == {"rename": "GT"}
    assert d1 == {}

    d1 = {"destination": None}
    d2 = {"rename": "GT", "destination": None}
    merge_destination(d2, d1)
    assert d2 == {"rename": "GT", "destination": None}
    assert d1 == {"destination": None}

    d1 = {"shift": 10}
    d2 = {"rename": "GT"}
    merge_destination(d2, d1)
    assert d2 == {"rename": "GT"}
    assert d1 == {"shift": 10}


def test_replacement():
    config = {"num_cores": "${system.cores}", "launch": "${launch}", "unchanged": "test"}
    variables = {"system": {"cores": 9}, "launch": True}
    config = replace_constants(config, variables)
    assert config == {"num_cores": 9, "launch": True, "unchanged": "test"}


def test_replacement_nested():
    config = {
        "system": {"cpu": {"cores": "${system.cores}"}},
        "launch": "${launch}",
        "unchanged": "test",
    }
    variables = {"system": {"cores": 9}, "launch": True}
    config = replace_constants(config, variables)
    assert config == {"system": {"cpu": {"cores": 9}}, "launch": True, "unchanged": "test"}


def test_replacement_list():
    config = {
        "system": {"cpu": ["${system.cores}", "${system.cores}"]},
        "launch": "${launch}",
        "unchanged": "test",
    }
    variables = {"system": {"cores": 9}, "launch": True}
    config = replace_constants(config, variables)
    assert config == {"system": {"cpu": [9, 9]}, "launch": True, "unchanged": "test"}


@pytest.mark.parametrize(
    "formula, function, args",
    [
        ("TEST < 2", "xr.lt", ["TEST", 2]),
        ("TEST > -2", "xr.gt", ["TEST", -2]),
        ("TEST is not False", "xr.not_", ["TEST", False]),
        ("TEST is True", "xr.is_", ["TEST", True]),
        ("TEST is ~2", "xr.is_", ["TEST", -3]),
    ],
    ids=["less than positive", "greater than negative", "not False", "is True", "invert 2"],
)
def test_ast_parser(formula, function, args):

    tree = ast.parse(formula)
    dag = AstParser().build_dag(tree)
    assert dag["dag"][0]["function"] == function
    assert dag["dag"][0]["args"] == args
