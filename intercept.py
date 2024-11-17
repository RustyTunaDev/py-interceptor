from inspect import getmembers, isfunction, ismethod
from typing import List, Tuple, Any, Callable


def get_methods(target: object) -> List[Tuple[str, Any]]:
    """
    Fetches all methods from an object and returns them.
    :param target: Target object to inspect.
    :return: The object's methods as a list of tuples.
    """
    return getmembers(target, predicate=lambda x: isfunction(x) or ismethod(x) or isinstance(x, property))


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
    :return: None
    """
    fn = getattr(target, name)

    def intercept(*args, **kwargs):
        inject(name, *args, **kwargs)
        if blocking:
            return None
        return fn(*args, **kwargs)

    setattr(target, name, intercept)
