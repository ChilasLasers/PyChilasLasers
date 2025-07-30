# Coding Conventions

This document outlines the coding standards and conventions for the PyChilasLasers project.

## 🎯 Overview

We follow **PEP 8** as our base style guide. All code should be consistent, readable, and maintainable.

## 🐍 Python Naming Conventions

| **Element**             | **Convention**                         | **Example**                      |
|------------------------|----------------------------------------|----------------------------------|
| **Variables**          | `snake_case`                           | `laser_power`, `wavelength_nm`   |
| **Constants**          | `ALL_CAPS_WITH_UNDERSCORES`            | `MAX_POWER`, `DEFAULT_WAVELENGTH`|
| **Functions/Methods**  | `snake_case()`                         | `set_power()`, `get_status()`    |
| **Classes**            | `PascalCase`                           | `LaserComponent`, `ManualMode`   |
| **Modules (.py files)**| `snake_case.py`                        | `laser_control.py`               |
| **Packages (folders)** | `lowercase` (no underscores preferred) | `components`, `modes`            |
| **Class Attributes**   | `snake_case`                           | `self.current_power`             |
| **Private/Internal**   | `_single_leading_underscore`           | `_calibration_table`             |
| **Strongly Private**   | `__double_leading_underscore`          | `__internal_config`              |
| **Special Methods**    | `__dunder__`                           | `__init__`, `__enter__`          |



## 📦 Import Organization

```python
# ✅ Standard library imports
import logging
import time
from typing import Optional, Union, List

# ✅ Third-party imports
import numpy as np
import serial

# ✅ Local imports
from pychilaslasers.exceptions import LaserError
from pychilaslasers.components.tec import TECController
```

## 📄 Package `__init__.py` Files

The `__init__.py` file serves as the entry point for Python packages and controls what gets imported when someone uses your package.

### 🎯 Purpose of `__init__.py`

- **Marks directories as packages**: Makes Python treat a directory as a package
- **Controls public API**: Defines what users can import from your package
- **Provides convenient imports**: Allows users to import from the package root
- **Package initialization**: Runs setup code when the package is first imported

### ✅ How to Write `__init__.py` Files

**Basic Package `__init__.py`** (expose main classes):
```python
"""PyChilasLasers - Python interface for Chilas laser control."""

# Import main classes for easy access
from .laser import Laser
from .exceptions import LaserError, CalibrationError

# Define what gets imported with "from pychilaslasers import *"
__all__ = [
    "Laser",
    "LaserError", 
    "CalibrationError",
]

# Package metadata
__version__ = "1.0.0"
__author__ = "ChilasLab"
```

**Subpackage `__init__.py`** (like `laser_components/__init__.py`):
```python
"""Laser hardware components."""

from .diode import Diode
from .tec import TEC
from .laser_component import LaserComponent

__all__ = [
    "Diode",
    "TEC", 
    "LaserComponent",
]
```

**Simple `__init__.py`** (minimal approach):
```python
"""Heater control components."""

# Just import what users need
from .heaters import HeaterController
from .heater_channels import HeaterChannels
```

### 🚫 Common Mistakes to Avoid

- ❌ **Empty `__init__.py`**: Makes imports harder for users
- ❌ **Importing everything**: Creates namespace pollution
- ❌ **Circular imports**: Be careful with cross-package imports
- ❌ **Heavy initialization**: Don't run expensive code at import time

### 📋 `__init__.py` Checklist

- ✅ Include a module docstring
- ✅ Import main public classes/functions
- ✅ Define `__all__` for controlled `import *`
- ✅ Add package metadata (`__version__`, etc.)
- ✅ Keep imports lightweight
- ✅ Use relative imports (`.module_name`)


## 🏗️ Class Organization and File Structure

### 📁 File Organization Rules

**One Class Per File** (unless exceptions apply):
- ✅ Each public class should have its own file
- ✅ Private classes (starting with `_`) can share files with their related public class
- ✅ Heavily related classes serving the same purpose can share a file
- ✅ Small utility classes that are tightly coupled can be grouped

### 📋 Class Structure Template

Organize class code in the following order:

```python
class ClassName:
    """Class docstring"""
    
    # Class-level constants
    
    def __init__(self):
        """Initialization with docstring"""

    ########## Main Methods ##########
    def public_method_1(self):
    def public_method_2(self):
    def public_method_3(self):

    ########## Private Methods ##########
    def _private_method_1(self):
    def _private_method_2(self):
    def _private_helper(self):

    ########## Properties (Getters/Setters) ##########
    @property
    def property_name(self):
    
    @property_name.setter
    def property_name(self, value):

    ########## Method Overloads/Aliases ##########
    def alias_method(self):
        """Calls other methods for convenience or backwards compatibility"""
    
    def combined_operation(self):
        """Combines multiple related functions in one call"""

    ########## Private Classes ##########
    # At the end of the file, outside the main class
    
class _PrivateHelper:
    """Private class for internal use only (starts with _)"""
    
class _InternalUtility:
    """Another private class not used outside this file"""
```

### 🔒 Private Classes

- Private classes start with `_` and should not be used outside their file
- Place private classes at the end of the file
- Document them but mark as internal use only
- Common use cases: helper classes, internal state machines, temporary data structures

## 📝 Attributes and Access Patterns

```python
class LaserController:
    def __init__(self):
        # ✅ Public attributes
        self.current_wavelength = 1550.0
        self.power_level = 0.0
        
        # ✅ Protected attributes (internal use)
        self._calibration_table = {}
        self._connection_state = "disconnected"
        
        # ✅ Private attributes (name mangling)
        self.__hardware_config = {}

    @property
    def wavelength(self) -> float:
        """Current laser wavelength in nm."""
        return self.current_wavelength
    
    @wavelength.setter
    def wavelength(self, value: float) -> None:
        """Set laser wavelength with validation."""
        if not (1500 <= value <= 1600):
            raise ValueError(f"Wavelength {value} nm out of range")
        self.current_wavelength = value
```


## 📋 Docstring Format

Use **Google-style** docstrings:

Indent everything under each section by 4 spaces.

The first line should be a short summary, followed by a blank line and a longer description (optional).

All section headers should be capitalized and followed by a colon (Args:, not args or args:).

### Supported sections

| Section             | Description                               |
| ------------------- | ----------------------------------------- |
| `Args:`             | Function or method parameters             |
| `Attributes:`       | Class instance attributes                 |
| `Class Attributes:` | Class-level attributes                    |
| `Returns:`          | Return value(s) from a function           |
| `Yields:`           | If the function is a generator            |
| `Raises:`           | Exceptions the function may raise         |
| `Examples:`         | Example usage (can use `>>>` for doctest) |
| `Note:`             | Extra developer or usage notes            |
| `Warning:`          | Cautions about usage                      |
| `See Also:`         | Related functions, classes, or modules    |


### Text formatting

| Feature               | Syntax                                                       | Example                              |
| --------------------- | ------------------------------------------------------------ | ------------------------------------ |
| **Bold text**         | `**bold**`                                                   | `This is **important**.`             |
| *Italic text*         | `*italic*`                                                   | `This is *emphasized*.`              |
| `Code`                | \`inline code\`                                              | `Returns a `dict\`\`                 |
| Code block            | Indent with 4 spaces or triple backticks (in Markdown tools) | ``` code ```                            |
| Hyperlink (inline)    | `[text](URL)` *(Markdown style)*                             | `[Google](https://google.com)`       |
| Hyperlink (RST style) | `` `text <url>`_ ``                                          | `` `Google <https://google.com>`_ `` |

### Links

:class:, :func:, and :mod: will create links if Sphinx can find them.

You can also link to methods like :meth:YourClass.method_name`

### Example

```python
def set_sweep_parameters(self, start_wl: float, end_wl: float) -> None:
    """Configure wavelength sweep parameters.

    Args:
        start_wl: Starting wavelength in nanometers.
        end_wl: Ending wavelength in nanometers.

    Raises:
        ValueError: If wavelength range is invalid.

    Examples:
        >>> laser.set_sweep_parameters(1530, 1570)

    See Also:
        :class:`DataParser`
        :func:`validate_input`
        :mod:`your_package.utils`
    """
```

## 🏷️ Type Hints

Always include type hints:

```python
from typing import Optional, Union, List, Dict

class LaserComponent:
    def __init__(self, name: str, channel: int) -> None:
        self.name = name
        self.channel = channel

    def set_value(self, value: Union[int, float]) -> bool:
        return True

    def get_status(self) -> Dict[str, Union[str, float, bool]]:
        return {"name": self.name, "active": True}
```


### Forward References and Circular Imports

Use `TYPE_CHECKING` to avoid circular imports while maintaining type safety:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

# Regular imports
from pychilaslasers.laser_components.laser_component import LaserComponent

# Type-only imports (not available at runtime)
if TYPE_CHECKING:
    from pychilaslasers import Laser  # Avoids circular import


class TEC(LaserComponent):
    def __init__(self, laser: Laser) -> None:
        super().__init__()
        self._laser: Laser = laser  # Type hint for clarity
```

### Using Dataclasses for Structured Data

For data containers, use `@dataclass` with type hints. These are a nice way to organize data:

```python
from dataclasses import dataclass
from typing import Tuple

@dataclass
class CalibrationEntry:
    wavelength: float
    phase_section: float
    large_ring: float
    small_ring: float
    coupler: float
    heater_values: Tuple[float, float, float, float]
    mode_index: int | None  # Python 3.10+ union syntax
    cycler_index: int
```

### Type Hint Guidelines

- ✅ **Always** use type hints for public methods and functions
- ✅ Use `Union[int, float]` or `int | float` for numeric parameters
- ✅ Use `Optional[T]` or `T | None` for nullable values
- ✅ Import types only when needed with `TYPE_CHECKING`
- ✅ Use `from __future__ import annotations` for forward references
- ✅ Add type hints to instance variables for clarity: `self._laser: Laser = laser`
- ❌ Don't import types that cause circular dependencies at runtime

## 🧪 Constants and Configuration

```python
# ✅ Module-level constants
DEFAULT_WAVELENGTH = 1550.0  # nm
MAX_POWER_MW = 100.0  # mW
CALIBRATION_TIMEOUT = 30.0  # seconds

# ✅ Enum-style constants
class LaserState:
    IDLE = "idle"
    READY = "ready"
    ACTIVE = "active"
    ERROR = "error"

class HeaterChannel:
    GAIN_CHIP = 1
    PHASE_SECTION = 2
    MIRROR_HEATER = 3
```

## ✅ Quick Style Checklist

- ✅ Use `snake_case` for variables and functions
- ✅ Use `PascalCase` for classes and exceptions
- ✅ Constants use `ALL_CAPS`
- ✅ Private attributes start with `_`
- ✅ Include type hints on all functions
- ✅ Use Google-style docstrings
- ✅ Group imports properly
- ✅ Follow PEP 8 line length (88 chars with black)
- ✅ Use meaningful, descriptive names
- ❌ Avoid `camelCase` (unless required by external APIs)
- ❌ Don't use single-letter variables (except loop counters)
