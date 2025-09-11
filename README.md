
# <img src="https://raw.githubusercontent.com/ChilasLasers/PyChilasLasers/refs/heads/main/docs/assets/star.ico" alt="Star icon" height="20" /> PyChilasLasers

Python library for controlling <b>Chilas</b> Atlas and Comet tunable lasers.

<div align="center">
	<img src="https://raw.githubusercontent.com/ChilasLasers/PyChilasLasers/refs/heads/main/docs/assets/Chilas-logo-color.png" alt="Chilas Logo" width=50% />
</div>


---

[![PyPI Version](https://img.shields.io/pypi/v/pychilaslasers.svg)](https://pypi.org/project/pychilaslasers) 
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FChilasLasers%2FPyChilasLasers%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
![GitHub Release](https://img.shields.io/github/v/release/ChilasLasers/PyChilasLasers)
![Pepy Total Downloads](https://img.shields.io/pepy/dt/pychilaslasers)
![GitHub contributors](https://img.shields.io/github/contributors/ChilasLasers/PyChilasLasers)
![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)


## Overview

PyChilasLasers is a Python interface for control of Chilas Atlas and Comet tunable laser. It provides:

- Device communication
- Three operating modes (Manual / Tune / Sweep*)
	- Manual: Control of all internal laser parameters
	- Tune: Wavelength tuning based on a calibration look-up table
	- Sweep: Continuous wavelength sweeping (*Comet only)

---
## Links

- [**Library quick start guide**](https://chilaslasers.github.io/PyChilasLasers/quickstart/)
- [**Full library documentation**](https://chilaslasers.github.io/PyChilasLasers)
- [**Overview of all Chilas laser products** ](https://chilasbv.com/products/)
- [**More information about Chilas**](https://chilasbv.com/about-us/)


## Installation

Using pip (stable release):

```bash
pip install pychilaslasers
```

From source (editable):
```bash
git clone https://github.com/ChilasLasers/PyChilasLasers
cd PyChilasLasers
pip install -e .
```


## Quick Example

Basic connection & wavelength set (see full script in [examples/basic_usage.py](https://github.com/ChilasLasers/PyChilasLasers/blob/main/examples/basic_usage.py)):

```python
#Minimal conceptual snippet: see examples for real usage
from pychilaslasers import Laser
laser = Laser("COM_PORT","path/to/calibration/file")
laser.mode = LaserModes.TUNE
laser.tune.wavelength = 1550.0
print(laser.wavelength)
```


## About & Support
<table>
<tr>
<td width="42%" valign="top">
<img src="https://raw.githubusercontent.com/ChilasLasers/PyChilasLasers/refs/heads/main/docs/assets/Chilas-Lasers-Comet-Atlas-Polaris-1024x683.webp" alt="Chilas Laser Modules (COMET / ATLAS / POLARIS)" style="max-width:100%;border-radius:4px;" />
</td>
<td valign="top">
Chilas is a laser manufacturer of widely tunable, narrow linewidth lasers based on state-of-the-art photonic integrated circuit (PIC) technology. With high laser performance delivered by compact modules, Chilas’ lasers power innovations worldwide, enabling cutting-edge applications in coherent optical communication, fiber sensing, LiDAR, quantum key distribution, microwave photonics, and beyond. Chilas is a privately held company (founded 2018) headquartered in Enschede, The Netherlands.
<br>
<br>
	
Sales and support: info@chilasbv.com  

</td>
</tr>
</table>

---

Happy tuning!  

Chilas, *Tuned to your wavelength*
