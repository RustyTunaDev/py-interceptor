import pytest

from intercept import get_methods
from tests.conftest import DummyTarget, METHODS


@pytest.mark.parametrize('target', [DummyTarget, DummyTarget()])
def test_get_methods_from_class_and_instance(target: object):
    methods = get_methods(target)
    methods = set(map(lambda m: m[0], methods))
    assert methods == set(METHODS)
