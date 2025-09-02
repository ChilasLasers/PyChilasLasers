# PyChilasLasers quickstart

To facilitate custom laser contol, the ATLAS tunable laser comes with a Python library package called PyChilasLasers. This package is a **Python library for controlling Chilas laser systems**, specifically designed for **ATLAS tunable laser modules**. The package provides a comprehensive, object-oriented interface for laser control.

  

## Package overview

The package contains the following:

- a demo file (demo.py) to show an example of how the library may be used
- the actual pyChilasLasers package, which contains the library
- a docs folder, which contains the code documentation in HTML format for reference.
- a Python project file (pyproject.toml)

  

## Class hierarchy

![[inheritance-8cebaa4c7740b9ffeb31ebd2b097d2f57e3c078a.png]]

  

The package follows a hierarchical design with increasingly specialized functionality:

  

**lasers.py** - Laser class to support serial communication with the laser driver

- Serial communication management

- Error handling and status monitoring

- Low-level laser operations (system state, TEC temperature, diode current, heater voltages)

  

**lasers_tlm.py** - TLMLaser class for specific functionality for the electronic driver (Tunable Laser Module)

- Management of the stored look-up table for laser calibration

- Temperature monitoring and control

  

**atlas_laser.py** - ATLAS laser class for wavelength control of the ATLAS tunable laser

- Two operating modes (STEADY and MANUAL)

- The STEADY operating mode enables wavelength tuning based on the pre-calibrated wavelength look-up table

- The MANUAL operating mode enables unrestricted laser control without using the look-up table

- Anti-hysteresis functionality to support accurate wavelength setting

- Generation of a trigger signal upon wavelength setting

  
  

## Key Features of the ATLAS laser class

  

**Dual Operating Modes:**

- **Steady Mode (`OperatingMode.STEADY`)**: Uses the calibration table entries for wavelength tuning

- **Manual Mode (`OperatingMode.MANUAL`)**: Provides direct control over individual heater voltages

  

**Wavelength Control:**

- **Absolute wavelength tuning** (`set_wavelength_abs()`) - tune to a specific wavelength in nanometers

- **Relative wavelength tuning** (`set_wavelength_rel()`) - tune by a wavelength offset from current

- **Index-based tuning** (`set_wavelength_abs_idx()`) - tune using calibration table indices

  

**Other:**

- **Wavelength lookup** - bidirectional conversion between wavelengths and calibration table indices

- **Trigger pulse generation** - generation of a trigger signal for synchronization with other equipment

  

## Quick start using the demo file

  

To operate an ATLAS laser using the PyChilasLasers library, an `AtlasLaser` object must be created, a calibration file loaded, and the appropriate operating mode configured. The demo_atlas.py file demonstrates a typical workflow for Atlas laser operation.

The demo illustrates the standard workflow: establish connection → load calibration → activate system → perform wavelength operations → shutdown safely. User prompts are included between operations to allow step-by-step observation of the laser's behavior.

  

**1. Initial Setup and Connection**

The demo starts by creating an `AtlasLaser` object and configuring it to communicate with the hardware on COM port 5. The right COM port number can be found after connecting the laser device to the computer and checking the number of the added COM port in the Windows Device Manager. After establishing the initial connection, the communication speed is optimized by increasing the baudrate to 460800.

  

```python

# Create laser object and establish connection

laser = AtlasLaser()

laser.port = "COM5"

laser.open_connection()

laser.baudrate = 460800  # Optimize for faster communication

```

  

**2. Load Calibration and Activate System**

The demo loads a calibration file using the `open_file_cycler_table` function. The system is then powered on and configured for steady-state operation mode.

  

```python

# Load the pre-calibrated lookup table by specifying its path.

fp_lut = Path(r"D:\\settings.csv")

laser.open_file_cycler_table(fp_lut)

  

# Power on the laser and set it to steady mode

laser.system_state = True

laser.operation_mode = OperatingMode.STEADY

```

  

**3. Wavelength Control Examples**

The demo demonstrates three different approaches to wavelength control: setting an absolute wavelength of 1545.000 nm, jumping directly to calibration table entry 2123, and making relative adjustments of +0.004 nm and -1.000 nm from the current position.

  

```python

# Direct wavelength setting

wavelength = laser.set_wavelength_abs(wl=1545.000)

  

# Index-based tuning using calibration table entries

wavelength = laser.set_wavelength_abs_idx(2123)

  

# Relative wavelength adjustments

laser.set_wavelength_rel(wl_delta=0.004)   # +0.004 nm step

laser.set_wavelength_rel(wl_delta=-1.000)  # -1.000 nm step

```

  

**4. Wavelength Monitoring**

The demo shows how to query the laser's actual wavelength and how to look up wavelength values from the calibration table without changing the laser's settings.

  

```python

# Check actual wavelength

current_wl = laser.get_wavelength()

  

# Look up wavelength for specific calibration index

index_wl = laser.get_wavelength_idx(2123)

```

  

**5. Safe Shutdown**

The demo concludes by properly shutting down the laser system and closing the communication connection.

  

```python

# Turn off laser and close connection

laser.system_state = False

laser.close_connection()

```

  

## Additional capabilities

  

The demo above demonstrates Atlas laser wavelength tuning using the pre-calibrated look-up table. In addition, the PyChilasLasers library provides extensive functionality including manual heater control, trigger pulse generation, anti-hysteresis algorithms, temperature monitoring, and advanced feedback control systems. For the complete documentation, we refer to the docs folder, which contains the code documentation in HTML format.

