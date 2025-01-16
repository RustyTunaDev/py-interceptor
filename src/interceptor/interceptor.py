import time
from dataclasses import dataclass
from functools import singledispatch
from inspect import getmembers, isfunction, ismethod
from typing import Callable, Set, Any, Optional, Dict, Tuple, Union, Type


class InterceptionError(Exception):
    """
    Exception raised when an interception error occurs.
    """
    pass


def get_methods(target: object) -> Set[str]:
    """
    Fetches all methods from an object and returns them.
    :param target: Target object to inspect.
    :return: The object's methods as a list of tuples.
    """
    methods = getmembers(target, predicate=lambda x: isfunction(x) or ismethod(x) or isinstance(x, property))
    return set(map(lambda m: m[0], methods))


@dataclass
class CallInfo:
    name: str
    blocking: bool
    args: Tuple
    kwargs: Dict
    target: Type
    ret_value: Optional[Any] = None
    exception: Optional[BaseException] = None
    timestamp_ns: Optional[int] = None

    def __post_init__(self):
        if self.timestamp_ns is None:
            self.timestamp_ns = time.time_ns()


@singledispatch
def intercept(methods: Union[str, Set[str]], target: object, interceptor: Callable[[CallInfo], Any],
              blocking: bool) -> None:
    """
    Intercepts a given target's method or set of methods.
    This function wraps the target method and injects a given interceptor callable.
    The injected function is called after (non-blocking mode) the target's original method or instead of it
    (blocking mode).

    :param target: The target object.
    :param methods: The name of the methods to be intercepted.
    :param interceptor: The interceptor callable.
    :param blocking: If true, the target's original method does not get called (it gets blocked), otherwise it gets
    executed after the injected function.
    :raises InterceptionError: If an interception error occurs.
    :return: None
    """
    raise NotImplementedError(f"intercept is not implemented for {type(methods)}")


@intercept.register
def intercept_single(methods: str, target: object, interceptor: Callable[[CallInfo], Any], blocking: bool) -> None:
    try:
        # Get the target's method by name
        fn = getattr(target, methods)
    except AttributeError:
        raise InterceptionError(f"Target object does not have a method '{methods}'.")

    def handler(*args, **kwargs):
        # In block-mode: Directly call the injection function
        if blocking:
            return interceptor(CallInfo(methods, True, args, kwargs, type(target)))

        # In non-blocking mode: Call the target's method and store it's return value or occurring exceptions
        info = CallInfo(methods, False, args, kwargs, type(target))
        try:
            info.ret_value = fn(*args, **kwargs)
        except BaseException as e:
            info.exception = e
        finally:
            interceptor(info)

        # If an exception was raised inside the target's method: re-raise it after injection call
        if info.exception:
            raise info.exception

        # Last step: return the target's method result
        return info.ret_value

    # Replace the target's method by intercept function
    setattr(target, methods, handler)


@intercept.register
def intercept_multiple(methods: set, target: object, interceptor: Callable[[CallInfo], Any],
                       blocking: bool) -> None:
    for name in methods:
        intercept_single(name, target, interceptor, blocking)
