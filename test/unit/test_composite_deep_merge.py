from abc import ABC, abstractmethod
from unittest import TestCase

from pycomposite import composite


class Builder(ABC):
    @abstractmethod
    def awesome(self) -> dict:
        pass


class BuilderA(Builder):
    def awesome(self) -> dict:
        return dict(a=[1, 2], b=3)


class BuilderB(Builder):
    def awesome(self) -> dict:
        return dict(a=[4, 5], d=6)


@composite
class CompositeBuilder(Builder):
    pass


class TestCompositeDeepMerge(TestCase):
    def setUp(self):
        self._builder = CompositeBuilder(BuilderA(), BuilderB())

    def test_deepmerge(self):
        self.assertEqual({"a": [1, 2, 4, 5], "b": 3, "d": 6}, self._builder.awesome())
