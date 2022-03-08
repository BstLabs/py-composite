from collections import deque
from functools import reduce
from inspect import getmembers, isfunction, signature
from typing import Any, Iterable, List

from deepmerge import always_merger


def _constructor(self, *parts: List[Iterable[Any]]) -> None:
    self._parts = parts


def _make_iterator(cls):
    def _iterator(self):
        # Simple depth-first composite Iterator
        # Recursive version did not work for some mysterious reason
        # This one proved to be more reliable
        # Credit: https://stackoverflow.com/questions/26145678/implementing-a-depth-first-tree-iterator-in-python
        stack = deque(self._parts)
        while stack:
            # Pop out the first element in the stack
            part = stack.popleft()
            if cls == type(part):  # The same composite exactly
                stack.extendleft(reversed(part._parts))
            elif isinstance(part, cls) or not isinstance(part, Iterable):
                yield part  # derived classes presumably have overloads
            else:  # Iterable
                stack.extendleft(reversed(part))

    return _iterator


def _make_initializer(rt: type) -> Any:
    return getattr(rt, "__origin__", rt)()


def _make_method(name: str, func: callable) -> callable:
    def _make_reduce(m: str, rt: type) -> callable:
        def _reduce_parts(self, *args, **kwargs) -> Any:
            # self is iterable, results come out flattened
            return reduce(
                lambda acc, obj: always_merger.merge(
                    acc, getattr(obj, m)(*args, **kwargs)
                )
                if rt is dict
                else acc + getattr(obj, m)(*args, **kwargs),
                self,
                _make_initializer(rt),
            )

        return _reduce_parts

    def _make_foreach(m) -> callable:
        def _foreach_parts(self, *args, **kwargs) -> callable:
            # self is iterable, concrete functions invoked depth first
            for obj in self:
                getattr(obj, m)(*args, **kwargs)

        return _foreach_parts

    rt: type = signature(func).return_annotation
    return _make_foreach(name) if rt is None else _make_reduce(name, rt)


# TODO: type annotation for parts (have to be descendants from the original class)
def composite(cls: type) -> type:
    """
    Generic class decorator to create a Composite from original class.
    Notes:

    1. the constructor does not make copy, so do not pass generators,
       if you plan to invoke more than one operation.

    2. it will return always flattened results of any operation.

    :param cls: original class
    :return: Composite version of original class
    """
    setattr(cls, "__init__", _constructor)
    base = cls.__bases__[0]
    attrs = {
        n: _make_method(n, f)
        for n, f in getmembers(cls, predicate=isfunction)
        if not n.startswith("_")
    }
    attrs["__init__"] = _constructor
    composite_cls = type(cls.__name__, (base,), attrs)
    composite_cls.__iter__ = _make_iterator(composite_cls)
    return composite_cls
