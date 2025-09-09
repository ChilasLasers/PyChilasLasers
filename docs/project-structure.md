```
📁 PyChilasLasers/
├──  📁 src/
│   └──  📁 pychilaslasers/
│       ├──  📁 exceptions/
│       │   ├──  __init__.py  # PyChilasLasers exceptions module.
│       │   ├──  laser_error.py  # Class representing errors received from the laser
│       │   └──  mode_error.py  # Exception class for laser mode-related errors.
│       ├──  📁 laser_components/
│       │   ├──  📁 heaters/
│       │   │   ├──  __init__.py  # Heater components package for laser thermal control.
│       │   │   ├──  heater_channels.py
│       │   │   └──  heaters.py  # Heater component classes.
│       │   ├──  __init__.py  # Laser hardware components package.
│       │   ├──  diode.py  # Laser diode component
│       │   ├──  laser_component.py  # Abstract base class for laser hardware components.
│       │   └──  tec.py  # Temperature control (TEC) component
│       ├──  📁 modes/
│       │   ├──  __init__.py  # PyChilasLasers Modes Module
│       │   ├──  calibrated.py  # Abstract base class for laser modes that require calibration data.
│       │   ├──  manual_mode.py  # Manual mode implementation for direct laser heater control.
│       │   ├──  mode.py  # Abstract base classes and enumerations for laser operating modes.
│       │   ├──  steady_mode.py  # Steady mode operation for laser wavelength control.
│       │   └──  sweep_mode.py  # Sweep mode implementation for laser wavelength sweeping operations.
│       ├──  __init__.py  # PyChilasLasers Module
│       ├──  comm.py  # This module contains the `Communication` class for handling communication with the laser
│       ├──  laser.py  # This module defines the Laser class for Chilas lasers.
│       └──  utils.py
├──  .gitignore
├──  licence.md
├──  main.py
├──  mkdocs.yml
├──  pyproject.toml
└──  README.md
``````
📁 PyChilasLasers/
├──  📁 src/
│   └──  📁 pychilaslasers/
│       ├──  📁 exceptions/
│       │   ├──  __init__.py  # PyChilasLasers exceptions module.
│       │   ├──  laser_error.py  # Class representing errors received from the laser
│       │   └──  mode_error.py  # Exception class for laser mode-related errors.
│       ├──  📁 laser_components/
│       │   ├──  📁 heaters/
│       │   │   ├──  __init__.py  # Heater components package for laser thermal control.
│       │   │   ├──  heater_channels.py
│       │   │   └──  heaters.py  # Heater component classes.
│       │   ├──  __init__.py  # Laser hardware components package.
│       │   ├──  diode.py  # Laser diode component
│       │   ├──  laser_component.py  # Abstract base class for laser hardware components.
│       │   └──  tec.py  # Temperature control (TEC) component
│       ├──  📁 modes/
│       │   ├──  __init__.py  # PyChilasLasers Modes Module
│       │   ├──  calibrated.py  # Abstract base class for laser modes that require calibration data.
│       │   ├──  manual_mode.py  # Manual mode implementation for direct laser heater control.
│       │   ├──  mode.py  # Abstract base classes and enumerations for laser operating modes.
│       │   ├──  steady_mode.py  # Steady mode operation for laser wavelength control.
│       │   └──  sweep_mode.py  # Sweep mode implementation for laser wavelength sweeping operations.
│       ├──  __init__.py  # PyChilasLasers Module
│       ├──  comm.py  # This module contains the `Communication` class for handling communication with the laser
│       ├──  laser.py  # This module defines the Laser class for Chilas lasers.
│       └──  utils.py
├──  .gitignore
├──  licence.md
├──  main.py
├──  mkdocs.yml
├──  pyproject.toml
└──  README.md
``````
📁 PyChilasLasers/
├──  📁 src/
│   └──  📁 pychilaslasers/
│       ├──  📁 exceptions/
│       │   ├──  __init__.py  # PyChilasLasers exceptions module.
│       │   ├──  laser_error.py  # Class representing errors received from the laser
│       │   └──  mode_error.py  # Exception class for laser mode-related errors.
│       ├──  📁 laser_components/
│       │   ├──  📁 heaters/
│       │   │   ├──  __init__.py  # Heater components package for laser thermal control.
│       │   │   ├──  heater_channels.py
│       │   │   └──  heaters.py  # Heater component classes.
│       │   ├──  __init__.py  # Laser hardware components package.
│       │   ├──  diode.py  # Laser diode component
│       │   ├──  laser_component.py  # Abstract base class for laser hardware components.
│       │   └──  tec.py  # Temperature control (TEC) component
│       ├──  📁 modes/
│       │   ├──  __init__.py  # PyChilasLasers Modes Module
│       │   ├──  calibrated.py  # Abstract base class for laser modes that require calibration data.
│       │   ├──  manual_mode.py  # Manual mode implementation for direct laser heater control.
│       │   ├──  mode.py  # Abstract base classes and enumerations for laser operating modes.
│       │   ├──  steady_mode.py  # Steady mode operation for laser wavelength control.
│       │   └──  sweep_mode.py  # Sweep mode implementation for laser wavelength sweeping operations.
│       ├──  __init__.py  # PyChilasLasers Module
│       ├──  comm.py  # This module contains the `Communication` class for handling communication with the laser
│       ├──  laser.py  # This module defines the Laser class for Chilas lasers.
│       └──  utils.py
├──  .gitignore
├──  licence.md
├──  main.py
├──  mkdocs.yml
├──  pyproject.toml
└──  README.md
```