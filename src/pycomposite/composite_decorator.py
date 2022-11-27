from collections import deque
from functools import reduce
from inspect import getmembers, isfunction, signature
from operator import add
from typing import Iterable, get_origin

from deepmerge import always_merger


def _constructor(self, *parts) -> None:
    self._parts = parts


def _make_iterator(cls):
    def _iterator(self):
        # Simple depth-first composite Iterator
        # Recursive version did not work for some mysterious reason
        # This one proved to be more reliable
        # Credit: https://stackoverflow.com/questions/26145678/implementing-a-depth-first-tree-iterator-in-python
        stack = deque(self._parts)
        # Pop out the first element in the stack
        while stack:
            part = stack.popleft()
            if cls == type(part):  # The same composite exactly
                stack.extendleft(reversed(part._parts))
            elif isinstance(part, cls) or not isinstance(part, Iterable):
                yield part  # derived classes presumably have overloads
            else:  # Iterable
                stack.extendleft(reversed(part))

    return _iterator


def _make_method(func_name: str, func: callable) -> callable:
    # because of Python closure gotacha need to define nested functions
    def _make_reduce(m: str, rt: type) -> callable:
        init_value = rt()
        combine = add if rt in (int, str, tuple) else always_merger.merge

        def _reduce_parts(
            self, *args, **kwargs
        ):  # this is a member function, hence self
            # self is iterable, results come out flattened
            return reduce(
                lambda acc, obj: combine(acc, getattr(obj, m)(*args, **kwargs)),
                self,
                init_value,
            )

        return _reduce_parts

    def _make_foreach(m) -> callable:
        def _foreach_parts(
            self, *args, **kwargs
        ) -> None:  # this is a member function, hence self
            # self is iterable, concrete functions invoked depth first
            for obj in self:
                getattr(obj, m)(*args, **kwargs)

        return _foreach_parts

    rt_ = signature(func).return_annotation
    rt = (
        get_origin(rt_) or rt_
    )  # strip type annotation parameters like tuple[int, ...] if present
    return _make_foreach(func_name) if rt is None else _make_reduce(func_name, rt)


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
    attrs = {
        func_name: _make_method(func_name, func)
        for func_name, func in getmembers(cls, predicate=isfunction)
        if not func_name.startswith(
            "_"
        )  # skip private methods, __magic_methods__ are TBD
    }
    attrs["__init__"] = _constructor
    composite_cls = type(cls.__name__, cls.__bases__, attrs)
    composite_cls.__iter__ = _make_iterator(composite_cls)
    return composite_cls
