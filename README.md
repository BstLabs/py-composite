# Composite Class Decorator

Generic implementation of the [Composite Design Pattern](https://en.wikipedia.org/wiki/Composite_pattern) as a Python class decorator.

This is an oppionated solution addressing a particular need of creating composite [Builders](https://en.wikipedia.org/wiki/Builder_pattern). All existing solutions we observed so far assumed manual reproduction on every abstract method in Composite, which is problematic from the maintenace point of view.

## Usage Example

```python
from abc import ABC, abstractmethod
from typing import Tuple, Any
from composite_decorator import composite

class Configuration:
    '''
    Just an example to demostrate side-effect
    '''
    def __init__(self):
        self._configuration = {}
        
    def configure(self, name: str, value: Any) -> None:
        self._configuration[name] = value
        
class Builder(ABC):

    @abstractmethod
    def build_part_one(self, arg: int) -> Tuple: #better coveres a general case
        pass
        
    @abstractmethod
    def build_part_two(self, arg: str) -> Tuple:
        pass
        
    @abstractmethod
    def configure_part_three(self, arg: Configuration) -> None:
        pass

class BuilderA(Builder):

    def build_part_one(self, arg: int) -> Tuple: #better coveres a general case
        return arg*10, arg+5,
        
    def build_part_two(self, arg: str) -> Tuple:
        return f'A: {arg}', 
        
    def configure_part_three(self, arg: Configuration) -> None:
        arg.configure('A', 'A builder')

class BuilderB(Builder):

    def build_part_one(self, arg: int) -> Tuple: #better coveres a general case
        return arg-100, arg*5,
        
    def build_part_two(self, arg: str) -> Tuple:
        return f'B: {arg}', 
        
    def configure_part_three(self, arg: Configuration) -> None:
        arg.configure('B', 'B builder')

@composite
class CompositeBuilder(Builder):
    pass
    
builder = CompositeBuilder(BuilderA(), BuilderB())
config = Configuration()

builder.configure_part_three(config)
assert (70, 12, -93, 35) == builder.build_part_one(7)
assert ('A: high', 'B: high') == builder.build_part_two('high')
assert {'A': 'A builder', 'B': 'B builder'} == config._configuration
```
