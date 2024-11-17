from inspect import getmembers, isfunction, ismethod
from typing import Callable, Set


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


def intercept_method(target: object, name: str, inject: Callable[..., None], blocking: bool) -> None:
    """
    Intercepts a given target's method.
    This function wraps the target method and injects a given function.
    The injected function is called before (non-blocking mode) the target's original method or instead of it
    (blocking mode).

    :param target: The target object.
    :param name: The name of the method to be intercepted.
    :param inject: The injection function.
    :param blocking: If true, the target's original method does not get called (it gets blocked), otherwise it gets
    executed after the injected function.
    :raises InterceptionError: If an interception error occurs.
    :return: None
    """
    try:
        fn = getattr(target, name)
    except AttributeError:
        raise InterceptionError(f"Target object does not have a method '{name}'.")

    def intercept(*args, **kwargs):
        inject(name, *args, **kwargs)
        if blocking:
            return None
        return fn(*args, **kwargs)

    setattr(target, name, intercept)


def intercept_methods(target: object, names: Set[str], inject: Callable[..., None], blocking: bool) -> None:
    """
    Intercepts a given target's methods.
    This function wraps the target methods and injects a given function.
    The injected function is called before (non-blocking mode) the target's original methods or instead of them
    (blocking mode).

    :param target: The target object.
    :param names: The names of the methods to be intercepted.
    :param inject: The injection function.
    :param blocking: If true, the target's original method does not get called (it gets blocked), otherwise it gets
    executed after the injected function.
    :raises InterceptionError: If an interception error occurs.
    :return: None
    """
    for name in names:
        intercept_method(target, name, inject, blocking)
