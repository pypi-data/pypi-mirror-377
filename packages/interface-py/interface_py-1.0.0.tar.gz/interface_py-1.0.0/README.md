# interface-py

**interface-py** is a lightweight Python package for defining **interfaces** and **concrete implementations** with enforced contracts. It ensures that concrete classes implement all required methods and properties, including optional enforcement of getter/setter properties.

---

## Features

- Define **interfaces** using a decorator or base class.
- Enforce that concrete classes implement all interface methods.
- Enforce **getter** and **setter** implementation for properties.
- Supports **multi-level interface hierarchies**.
- Prevents runtime errors from missing implementations.
- Works alongside Python's built-in ABCs.

---

## Installation

```bash
pip install interface-py
```

---

## Usage

### Defining an Interface

```python
from interface_py import interface

@interface
class HumanInterface:
    def speak(self):
        ...
    
    @property
    def name(self):
        ...
    
    @name.setter
    def name(self, value):
        ...
```

### Multi-level Interface Example

```python
@interface
class MilitaryHumanInterface(HumanInterface):
    def march(self):
        ...

@concrete
class Soldier(MilitaryHumanInterface):
    def speak(self):
        print("Reporting for duty!")

    def march(self):
        print("Marching!")

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
```

- `MilitaryHumanInterface` **extends** `HumanInterface`.  
- `Soldier` **implements all required methods and properties** from both `HumanInterface` and `MilitaryHumanInterface`.

---

### Validation

- Trying to instantiate a concrete class that **does not implement all interface methods/properties** raises a `TypeError`.
- Ensures consistent **interface contracts** across your project.

---

## Why Use interface-py?

- Provides **contract enforcement** in dynamically typed Python.
- Helps structure large codebases with clear **interface and implementation separation**.
- Avoids runtime errors from missing methods or properties.
- Enhances code **readability**, **maintainability**, and **Pythonic design**.

---

## License

MIT License
