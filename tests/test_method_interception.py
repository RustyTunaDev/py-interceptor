import pytest

from intercept import intercept_method
from tests.conftest import METHODS, DummyTarget


@pytest.mark.parametrize('method', METHODS)
@pytest.mark.parametrize('blocking', [True, False])
def test_intercept_method(method: str, blocking: bool):
    intercepted = False

    def _interception(name: str, *args, **kwargs):
        nonlocal intercepted
        intercepted = True
        assert name == method
        assert args[0] == 1
        assert kwargs["b"] == 2

    target = DummyTarget()
    intercept_method(target, method, _interception, blocking=blocking)
    m = getattr(target, method)

    # If we use non-blocking mode we expect our function to be executed and thus, deliver the correct result
    if not blocking:
        assert m(1, b=2) == 3
    # Otherwise, if blocking-mode is active, our method should be intercepted but not executed
    else:
        assert m(1, b=2) is None

    assert intercepted
