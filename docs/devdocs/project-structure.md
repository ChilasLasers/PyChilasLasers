# Project Structure

This document explains the organization and architecture of the PyChilasLasers codebase.

## 📁 Overall Structure

```
PyChilasLasers/
├── 📁 src/
│   └── 📁 pychilaslasers/          # Main package
│       ├── __init__.py             # Package entry point
│       ├── laser.py                # Core Laser class
│       ├── utils.py                # Utility functions and constants
│       ├── 📁 laser_components/    # Hardware components
│       │   ├── __init__.py
│       │   ├── laser_component.py  # Base component class
│       │   ├── tec.py              # Temperature control
│       │   ├── diode.py            # Laser diode control
│       │   └── 📁 heaters/         # Heater components
│       │       ├── __init__.py
│       │       ├── heaters.py      # Heater implementations
│       │       └── heater_channels.py  # Heater channel control
│       └── 📁 modes/               # Operation modes
│           ├── __init__.py
│           ├── mode.py             # Base mode class and enum
│           ├── manual_mode.py      # Manual control mode
│           ├── calibrated.py       # Base calibrated mode
│           ├── steady_mode.py      # Steady-state mode
│           ├── sweep_mode.py       # Sweep mode
│           └── wl_change_method.py # Wavelength change methods
├── 📁 tests/                       # Test suite
│   ├── __init__.py
│   ├── test_calibration_reading.py # Calibration tests
│   └── 📁 calibrationFiles/        # Test calibration data
│       ├── atlas1.csv
│       ├── atlas2.csv
│       ├── comet1.csv
│       └── comet2.csv
├── 📁 examples/                    # Usage examples
│   ├── basic_usage.py              # Basic usage example
│   └── type_check_example.py       # Type checking example
├── 📁 docs/                        # Documentation
│   ├── README.md                   # User documentation
│   └── 📁 devdocs/                 # Developer docs
│       ├── project-structure.md    # This file
│       ├── coding-conventions.md   # Code style guide
│       └── git-workflow.md         # Git workflow
├── main.py                         # Main entry point
├── pyproject.toml                  # Project configuration
├── uv.lock                         # Dependency lock file
└── README.md                       # Project overview
```

## 🎯 Core Package Structure

### Main Package (`src/pychilaslasers/`)

The main package follows a modular design where each major functionality is separated into its own module or subpackage.

#### `__init__.py` - Package Entry Point

```python
"""Python library for controlling Chilas lasers."""

__version__ = "1.0.0"
__author__ = "ChilasLab"

from .laser import Laser

__all__ = [
    "Laser",
]
```

### Laser Components Package (`laser_components/`)

Hardware component controllers, organized by functionality:

```python
# laser_components/__init__.py
from .laser_component import LaserComponent
from .diode import Diode
from .tec import TEC
from .heaters.heater_channels import HeaterChannel
from .heaters.heaters import Heater, TunableCoupler, LargeRing, SmallRing, PhaseSection

__all__ = [
    "LaserComponent",
    "Diode", 
    "TEC",
    "HeaterChannel",
    "Heater",
    "TunableCoupler",
    "LargeRing", 
    "SmallRing",
    "PhaseSection"
]

# laser_components/laser_component.py
class LaserComponent:
    """Base class for all laser components."""
    pass

# laser_components/diode.py  
class Diode:
    """Laser diode control and monitoring."""
    pass

# laser_components/tec.py
class TEC:
    """Temperature control for laser components."""
    pass

# laser_components/heaters/heaters.py
class Heater:
    """Base heater element control."""
    pass

class TunableCoupler(Heater):
    """Tunable coupler heater control."""
    pass

class LargeRing(Heater):
    """Large ring heater control."""
    pass

class SmallRing(Heater):
    """Small ring heater control."""
    pass

class PhaseSection(Heater):
    """Phase section heater control."""
    pass

# laser_components/heaters/heater_channels.py
class HeaterChannel:
    """Individual heater channel control."""
    pass
```

### Modes Package (`modes/`)

Operation mode implementations with base classes and concrete modes:

```python
# modes/__init__.py
"""
PyChilasLasers Modes Module

This module provides various laser operation modes and related classes for controlling
Chilas laser systems. It includes manual mode for direct control, calibrated modes
for wavelength-based operations, and wavelength change methods.

Classes:
    - LaserMode: Enum defining available laser modes
    - Mode: Abstract base class for all modes
    - ManualMode: Direct manual control of laser parameters
    - SteadyMode: Calibrated steady-state wavelength operation
    - SweepMode: Calibrated wavelength sweeping operation
    - WLChangeMethod: Abstract base for wavelength change methods
    - PreLoad: Preload-based wavelength change method
    - CyclerIndex: Cycler index-based wavelength change method
"""

# Core mode classes
from .mode import LaserMode, Mode

# Concrete mode implementations
from .manual_mode import ManualMode
from .steady_mode import SteadyMode
from .sweep_mode import SweepMode

# Wavelength change methods
from .wl_change_method import WLChangeMethod, PreLoad, CyclerIndex

__all__ = [
    # Enums and base classes
    "LaserMode",
    "Mode",
    
    # Mode implementations
    "ManualMode",
    "SteadyMode", 
    "SweepMode",
    
    # Wavelength change methods
    "WLChangeMethod",
    "PreLoad",
    "CyclerIndex",
]

# modes/mode.py
class LaserMode:
    """Enum defining available laser modes."""
    pass

class Mode:
    """Abstract base class for all modes."""
    pass

# modes/manual_mode.py
class ManualMode(Mode):
    """Manual control mode for direct parameter setting."""
    pass

# modes/calibrated.py
class _Calibrated(Mode):
    """Base class for calibrated modes (internal use)."""
    pass

# modes/steady_mode.py
class SteadyMode(_Calibrated):
    """Steady-state operation with automatic stabilization."""
    pass

# modes/sweep_mode.py
class SweepMode(_Calibrated):
    """Wavelength sweep operations."""
    pass

# modes/wl_change_method.py
class WLChangeMethod:
    """Abstract base for wavelength change methods."""
    pass

class PreLoad(WLChangeMethod):
    """Preload-based wavelength change method."""
    pass

class CyclerIndex(WLChangeMethod):
    """Cycler index-based wavelength change method."""
    pass
```

### Utils Module (`utils.py`)

Shared utilities, constants, and helpers in a single module:

```python
# utils.py
"""Utility functions, constants, and data structures for the PyChilasLasers package."""

from dataclasses import dataclass

class Constants:
    """Constants used throughout the library."""
    pass

@dataclass
class CalibrationEntry:
    """Data structure for calibration entries."""
    pass
```

## 🧪 Test Structure

Tests are currently minimal and focused on calibration functionality:

```
tests/
├── __init__.py
├── test_calibration_reading.py     # Calibration file reading tests
└── calibrationFiles/               # Test calibration data
    ├── atlas1.csv                  # ATLAS laser calibration
    ├── atlas2.csv
    ├── comet1.csv                  # COMET laser calibration
    ├── comet2.csv
    └── Calibration files for ATLAS and COMET.zip
```

## 📚 Examples Structure

Examples demonstrate basic usage and type checking:

```
examples/
├── basic_usage.py                  # Basic laser control example
└── type_check_example.py           # Type checking demonstration
```

## 🏗️ Design Principles

### 1. Separation of Concerns
- **Laser Components**: Hardware-specific control (`laser_components/`)
- **Modes**: High-level operation patterns (`modes/`)
- **Utils**: Shared functionality (`utils.py`)
- **Core**: Main laser class (`laser.py`)

### 2. Hierarchical Component Structure
```python
# ✅ Current: Organized component hierarchy
laser_components/
├── laser_component.py      # Base class
├── diode.py               # Diode control
├── tec.py                 # Temperature control
└── heaters/               # Heater subsystem
    ├── heaters.py         # Heater implementations
    └── heater_channels.py # Channel control
```

### 3. Mode-Based Operation
Each operation mode has a clear purpose:
- `manual_mode.py` - Direct parameter control
- `steady_mode.py` - Calibrated steady-state operation
- `sweep_mode.py` - Calibrated sweep operations
- `calibrated.py` - Base class for calibrated modes

### 4. Extensible Design
Easy to extend without modifying existing code:
```python
# ✅ Easy to add new heater types
class NewHeaterType(Heater):
    def custom_control_logic(self): ...

# ✅ Easy to add new wavelength change methods
class NewWLMethod(WLChangeMethod):
    def change_wavelength(self): ...
```

## 📦 Package Requirements

### All packages and modules must have `__init__.py`
This ensures proper Python package structure and enables imports.

```python
# Each __init__.py should:
# 1. Import public classes/functions
# 2. Define __all__ for explicit exports
# 3. Include brief module docstring

# Example: laser_components/__init__.py
from .laser_component import LaserComponent
from .diode import Diode
from .tec import TEC
from .heaters.heater_channels import HeaterChannel
from .heaters.heaters import Heater, TunableCoupler, LargeRing, SmallRing, PhaseSection

__all__ = [
    "LaserComponent",
    "Diode", 
    "TEC",
    "HeaterChannel",
    "Heater",
    "TunableCoupler",
    "LargeRing", 
    "SmallRing",
    "PhaseSection"
]
```

## 🎯 Key Benefits

1. **Modular**: Easy to work on individual components and modes
2. **Hierarchical**: Clear component organization with base classes
3. **Extensible**: New heater types and modes integrate cleanly
4. **Maintainable**: Clear organization aids debugging and development
5. **Focused**: Single-file utils and targeted functionality

## 📝 File Naming Guidelines

- Use `snake_case.py` for all Python files
- Keep names descriptive but concise
- Group related functionality in packages
- Use descriptive names for specialized components (`laser_components/`, `heaters/`)
- Use singular for single-module utilities (`utils.py`)

This structure reflects the current state of the PyChilasLasers library and provides a solid foundation for continued development!
