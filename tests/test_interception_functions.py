import pytest

from src.interceptor.interceptor import intercept, get_methods, InterceptionError, CallInfo
from tests.conftest import METHODS, DummyTarget


class TestInterceptionFunctions:
    intercepted = False
    called_methods = set()

    @pytest.mark.parametrize('method', METHODS)
    @pytest.mark.parametrize('blocking', [True, False])
    def test_intercept_single_method(self, method: str, blocking: bool):

        def _intercept(info: CallInfo):
            self.intercepted = True
            assert info.name == method
            assert info.blocking == blocking
            assert info.ret_value == (3 if not blocking else None)
            assert info.args[0] == 1
            assert info.kwargs["b"] == 2
            assert info.target == DummyTarget
            return "foo"

        target = DummyTarget()
        intercept(method, target, _intercept, blocking=blocking)
        m = getattr(target, method)

        # If we use non-blocking mode we expect our function to be executed and thus, deliver the correct result
        if not blocking:
            assert m(1, b=2) == 3
        # Otherwise, if blocking-mode is active, our method should be intercepted but not executed
        else:
            assert m(1, b=2) == "foo"

        assert self.intercepted

    def test_intercept_a_set_of_methods(self):

        def _intercept(info: CallInfo):
            self.called_methods.add(info.name)

        target = DummyTarget()
        intercept(get_methods(target), target, _intercept, True)

        # Call all methods
        for method in get_methods(target):
            getattr(target, method)(1, b=2)

        # Ensure all methods were intercepted
        assert self.called_methods == METHODS

    def test_intercept_raises_on_unsupported_methods_type(self):
        target = DummyTarget()
        with pytest.raises(NotImplementedError, match="intercept is not implemented for <class 'int'>"):
            intercept(123, target, lambda info: None, blocking=False)

    def test_intercept_raises_on_non_existing_method(self):
        target = DummyTarget()
        with pytest.raises(InterceptionError, match="Target object does not have a method 'foo_bar'."):
            intercept("foo_bar", target, lambda info: None, blocking=False)

    def test_intercept_stores_and_reraises_exceptions(self):
        class ErrorTarget:
            def foo(self, a, b):
                1 // 0

        def _intercept(info: CallInfo):
            self.intercepted = True
            assert isinstance(info.exception, ZeroDivisionError)

        target = ErrorTarget()
        intercept("foo", target, _intercept, blocking=False)

        with pytest.raises(ZeroDivisionError):
            target.foo(1, b=2)

        assert self.intercepted

    @pytest.mark.parametrize('target', [DummyTarget, DummyTarget()])
    def test_get_methods_from_class_and_instance(self, target: object):
        assert get_methods(target) == set(METHODS)
