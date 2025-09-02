
# Welcome to Chilas documentation


## 📁 Project Structure

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



# TODO

- [ ] Choose theme
- [ ] Write index page
- [ ] Write getting started guide
- [ ] Add logos
- [ ] Deploy
- [ ] 
[Google Docs Devdocs update](https://mkdocstrings.github.io/griffe/reference/docstrings/#google-sections) 
- [] 
[drawio](https://github.com/LukeCarrier/mkdocs-drawio-exporter)