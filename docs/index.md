
# Welcome to Chilas documentation


Chilas is a laser manufacturer of widely tunable, narrow linewidth lasers based on state-of-the-art photonic integrated circuit (PIC) **technology**. With high laser performance delivered by compact modules, Chilas’ lasers power innovations worldwide, enabling cutting-edge applications in coherent optical communication, fiber sensing, LiDAR, quantum key distribution, microwave photonics, and beyond.  

Chilas is a privately held company, founded in 2018, and headquartered in Enschede, the Netherlands.

---

<img src="assets\Chilas-Lasers-Comet-Atlas-Polaris-1024x683.webp" alt="Chilas products: ATLAS, POLARIS, COMET" width="400">


## Our Mission and Vision

**Mission:**  
“To deliver precise, compact, and innovative laser solutions that power cutting-edge applications and empower researchers to achieve breakthroughs.”

**Vision:**  
“Solving tomorrow’s challenges and opening new frontiers in science and industry.”

---

## Our Values

### Innovation & Technology
- **Innovation:** Pioneering laser technology based on PIC technology  
- **Future-Focused:** Being open to creating new lasers at different wavelengths based on industry needs  

### Reliability and Dedication
- **Reliability:** Always available to assist and ensure customer success  
- **Dedication:** We go above and beyond to meet customers’ requirements  

### Teamwork and Community
- **Inclusive Work Culture:** International team closely collaborating in an informal environment  


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