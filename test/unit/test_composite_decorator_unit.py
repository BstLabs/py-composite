from abc import ABC, abstractmethod
from typing import Any, Tuple
from unittest import TestCase, main

from pycomposite import composite

# from typing import overload


class Configuration:
    """
    Just an example to demonstrate side-effect
    """

    def __init__(self):
        self._configuration = {}

    def configure(self, name: str, value: Any) -> None:
        self._configuration[name] = value


class Builder(ABC):
    @abstractmethod
    def build_part_one(self, arg: int) -> Tuple:  # better covers a general case
        pass

    @abstractmethod
    def build_part_two(self, arg: str) -> Tuple:
        pass

    @abstractmethod
    def configure_part_three(self, arg: Configuration) -> None:
        pass

    @abstractmethod
    def build_part_four(self) -> Tuple:
        pass


class BuilderA(Builder):
    def build_part_one(self, arg: int) -> Tuple:  # better covers a general case
        return (
            arg * 10,
            arg + 5,
        )

    def build_part_two(self, arg: str) -> Tuple:
        return (f"A: {arg}",)

    def configure_part_three(self, arg: Configuration) -> None:
        arg.configure("A", "A builder")

    def build_part_four(self) -> Tuple:
        return (("A", {}),)


class BuilderB(Builder):
    def build_part_one(self, arg: int) -> Tuple:  # better covers a general case
        return (
            arg - 100,
            arg * 5,
        )

    def build_part_two(self, arg: str) -> Tuple:
        return (f"B: {arg}",)

    def configure_part_three(self, arg: Configuration) -> None:
        arg.configure("B", "B builder")

    def build_part_four(self) -> Tuple:
        return (("B", {}),)


class BuilderC(Builder):
    def build_part_one(self, arg: int) -> Tuple:  # better covers a general case
        return (
            arg - 100,
            arg * 5,
        )

    def build_part_two(self, arg: str) -> Tuple:
        return (f"C: {arg}",)

    def configure_part_three(self, arg: Configuration) -> None:
        arg.configure("C", "C builder")

    def build_part_four(self) -> Tuple:
        return (("C", {}),)


class BuilderD(Builder):
    def build_part_one(self, arg: int) -> Tuple:  # better covers a general case
        return (
            arg - 100,
            arg * 5,
        )

    def build_part_two(self, arg: str) -> Tuple:
        return (f"D: {arg}",)

    def configure_part_three(self, arg: Configuration) -> None:
        arg.configure("D", "D builder")

    def build_part_four(self) -> Tuple:
        return (("D", {}),)


@composite
class CompositeBuilder(Builder):
    pass


class CustomCompositeBuilder(CompositeBuilder):
    pass


class TestComposite(TestCase):
    def setUp(self):
        self._builder = CompositeBuilder(
            (BuilderA(), CustomCompositeBuilder(CompositeBuilder(BuilderB())))
        )
        self._config = Configuration()

    def test_composite(self):
        self._builder.configure_part_three(self._config)
        self.assertEqual((70, 12, -93, 35), self._builder.build_part_one(7))
        self.assertEqual(("A: high", "B: high"), self._builder.build_part_two("high"))
        self.assertEqual(
            {"A": "A builder", "B": "B builder"}, self._config._configuration
        )

    def test_iterator(self):
        self.assertEqual(
            [BuilderA, CustomCompositeBuilder], [type(b) for b in self._builder]
        )

    def test_deep_nesting(self):
        builder = CompositeBuilder(
            BuilderA(),
            CompositeBuilder(
                BuilderB(), CompositeBuilder(BuilderC(), CompositeBuilder(BuilderD()))
            ),
        )
        self.assertEqual(
            (("A", {}), ("B", {}), ("C", {}), ("D", {})), builder.build_part_four()
        )


if __name__ == "__main__":
    main()
