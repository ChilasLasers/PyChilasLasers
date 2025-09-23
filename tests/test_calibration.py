"""Tests for the calibration module."""

import pytest
from pathlib import Path
from io import StringIO
from unittest.mock import mock_open, patch

from pychilaslasers.calibration.calibration_parsing import _parse_defaults_block, _parse_rows, load_calibration
from pychilaslasers.calibration import (
    CalibrationEntry,
    Calibration,
    TuneSettings,
)
from pychilaslasers.exceptions.calibration_error import CalibrationError



class TestCalibrationEntry:
    """Test the CalibrationEntry dataclass."""
    
    def test_heater_values_post_init(self):
        """Test that heater_values is computed correctly in __post_init__."""
        entry = CalibrationEntry(
            wavelength=1550.0,
            phase_section=10.0,
            large_ring=20.0,
            small_ring=30.0,
            coupler=40.0,
            mode_index=1,
            mode_hop_flag=False,
            cycler_index=0
        )
        
        assert entry.heater_values == (10.0, 20.0, 30.0, 40.0)



# Sample test data for calibration
SAMPLE_CALIBRATION_ENTRIES = [
    CalibrationEntry(1555.0, 10.0, 20.0, 30.0, 40.0, 1, False, 0),
    CalibrationEntry(1554.0, 11.0, 21.0, 31.0, 41.0, 1, False, 1),
    CalibrationEntry(1553.0, 12.0, 22.0, 32.0, 42.0, 1, False, 2),
    CalibrationEntry(1552.0, 13.0, 22.0, 33.0, 43.0, 2, True, 3),  # mode hop
    CalibrationEntry(1552.0, 12.0, 23.0, 33.0, 43.0, 2, True, 4),  # mode hop
    CalibrationEntry(1552.0, 11.0, 24.0, 33.0, 43.0, 2, False, 5),  # mode hop
    CalibrationEntry(1551.0, 14.0, 24.0, 34.0, 44.0, 2, False, 6),
]

SAMPLE_TUNE_SETTING = TuneSettings(
    current=280.0,
    tec_temp=25.0,
    anti_hyst_voltages=[35.0, 0.0],
    anti_hyst_times=[10.0],
)


class TestCalibration:
    """Test the Calibration class."""
    
    def test_calibration_creation(self):
        """Test basic Calibration object creation."""
        calibration = Calibration(
            model="ATLAS",
            entries=SAMPLE_CALIBRATION_ENTRIES,
            tune_settings=SAMPLE_TUNE_SETTING,
            sweep_settings=None
        )
        
        assert calibration.model == "ATLAS"
        assert len(calibration.entries) == len(SAMPLE_CALIBRATION_ENTRIES)
        assert calibration.tune_settings == SAMPLE_TUNE_SETTING
        assert calibration.sweep_settings is None
        assert calibration.max_wl == 1555.0
        assert calibration.min_wl == 1551.0
    
    def test_calibration_iter(self):
        """Test __iter__ method."""
        calibration = Calibration(
            model="ATLAS",
            entries=SAMPLE_CALIBRATION_ENTRIES,
            tune_settings=SAMPLE_TUNE_SETTING,
            sweep_settings=None
        )
        
        entries_list = list(calibration)
        assert entries_list == SAMPLE_CALIBRATION_ENTRIES
        for entry in calibration:
            assert entry in SAMPLE_CALIBRATION_ENTRIES
    
    def test_calibration_contains_wavelength(self):
        """Test __contains__ method with wavelength."""
        calibration = Calibration(
            model="ATLAS",
            entries=SAMPLE_CALIBRATION_ENTRIES,
            tune_settings=SAMPLE_TUNE_SETTING,
            sweep_settings=None
        )
        
        assert 1552.5 in calibration  # within range
        assert 1556.0 not in calibration  # above max
        assert 1550.0 not in calibration  # below min
    
    def test_calibration_contains_entry(self):
        """Test __contains__ method with CalibrationEntry."""
        calibration = Calibration(
            model="ATLAS",
            entries=SAMPLE_CALIBRATION_ENTRIES,
            tune_settings=SAMPLE_TUNE_SETTING,
            sweep_settings=None
        )
        
        assert SAMPLE_CALIBRATION_ENTRIES[0] in calibration
        
        other_entry = CalibrationEntry(1560.0, 50.0, 60.0, 70.0, 80.0, None, False, 10)
        assert other_entry not in calibration
    
    def test_calibration_getitem_exact_match(self):
        """Test __getitem__ with exact wavelength match."""
        calibration = Calibration(
            model="ATLAS",
            entries=SAMPLE_CALIBRATION_ENTRIES,
            tune_settings=SAMPLE_TUNE_SETTING,
            sweep_settings=None
        )
        
        entry = calibration[1555.0]
        assert entry.wavelength == 1555.0
        assert entry.phase_section == 10.0
    
    def test_calibration_getitem_closest_match(self):
        """Test __getitem__ with closest wavelength match."""
        calibration = Calibration(
            model="ATLAS",
            entries=SAMPLE_CALIBRATION_ENTRIES,
            tune_settings=SAMPLE_TUNE_SETTING,
            sweep_settings=None
        )
        
        # Should find closest non-mode-hop entry
        entry = calibration[1552.7]  # closest to 1552.0, but that's a mode hop
        assert entry.wavelength == 1553.0  # next closest non-mode-hop
    
    def test_calibration_getitem_key_error(self):
        """Test __getitem__ raises KeyError for out of range wavelength."""
        calibration = Calibration(
            model="ATLAS",
            entries=SAMPLE_CALIBRATION_ENTRIES,
            tune_settings=SAMPLE_TUNE_SETTING,
            sweep_settings=None
        )
        
        with pytest.raises(KeyError):
            _ = calibration[1560.0]  # out of range
    
    def test_get_mode_hop_start(self):
        """Test get_mode_hop_start when wavelength has mode hop entry."""
        calibration = Calibration(
            model="ATLAS",
            entries=SAMPLE_CALIBRATION_ENTRIES,
            tune_settings=SAMPLE_TUNE_SETTING,
            sweep_settings=None
        )
        
        entry = calibration.get_mode_hop_start(1552.0)
        assert entry == CalibrationEntry(1552.0, 13.0, 22.0, 33.0, 43.0, 2, True, 3)  # mode hop
        assert not entry ==CalibrationEntry(1552.0, 12.0, 23.0, 33.0, 43.0, 2, True, 4)  # mode hop
        assert not entry ==CalibrationEntry(1552.0, 11.0, 24.0, 33.0, 43.0, 2, False, 5)  # mode hop




    def test_get_mode_hop_start_without_mode_hop(self):
        """Test get_mode_hop_start when wavelength has no mode hop entry."""
        calibration = Calibration(
            model="ATLAS",
            entries=SAMPLE_CALIBRATION_ENTRIES,
            tune_settings=SAMPLE_TUNE_SETTING,
            sweep_settings=None
        )
        
        entry = calibration.get_mode_hop_start(1555.0)
        assert entry == CalibrationEntry(1555.0, 10.0, 20.0, 30.0, 40.0, 1, False, 0)



class TestHelperFunctions:
    """Test helper functions."""

    def test_parse_defaults_block_atlas(self):
        """Test _parse_defaults_block for ATLAS laser."""
        content = """laser_model = ATLAS
tune_diode_current = 280.0
tune_tec_target = 25.0
anti_hyst_phase_v_squared = [35.0, 0.0]
anti_hyst_interval = [10.0]
[look_up_table]
"""
        f = StringIO(content)
        
        model, tune, sweep = _parse_defaults_block(f)
        
        assert model == "ATLAS"
        assert tune.current == 280.0
        assert tune.tec_temp == 25.0
        assert tune.anti_hyst_voltages == [35.0, 0.0]
        assert tune.anti_hyst_times == [10.0]
        assert sweep is None
    
    def test_parse_defaults_block_comet(self):
        """Test _parse_defaults_block for COMET laser."""
        content = """laser_model = COMET
tune_diode_current = 280.0
tune_tec_target = 25.0
anti_hyst_phase_v_squared = [35.0, 0.0]
anti_hyst_interval = [10.0]
sweep_diode_current = 300.0
sweep_tec_target = 30.0
sweep_interval = 100
[look_up_table]
"""
        f = StringIO(content)
        
        model, tune, sweep = _parse_defaults_block(f)
        
        assert model == "COMET"
        assert tune.current == 280.0
        assert sweep is not None
        assert sweep.current == 300.0
        assert sweep.tec_temp == 30.0
        assert sweep.sweep_interval == 100
    
    def test_parse_defaults_block_missing_parameter(self):
        """Test _parse_defaults_block raises CalibrationError for missing parameter."""
        content = """laser_model = ATLAS
tune_diode_current = 280.0
anti_hyst_phase_v_squared = [35.0, 0.0]
anti_hyst_interval = [10.0]
[look_up_table]
"""
        f = StringIO(content)
        
        with pytest.raises(CalibrationError):
            _parse_defaults_block(f)
    
    def test_parse_defaults_block_eof(self):
        """Test _parse_defaults_block raises CalibrationError on unexpected EOF."""
        content = """laser_model = ATLAS
tune_diode_current = 280.0
"""
        f = StringIO(content)
        
        with pytest.raises(CalibrationError):
            _parse_defaults_block(f)
    

class TestLoadCalibration:
    """Test the load_calibration function."""
    
    def test_load_calibration_with_defaults(self):
        """Test loading calibration file with default settings block."""
        content = """[default_settings]
laser_model = ATLAS
tune_diode_current = 280.0
tune_tec_target = 25.0
anti_hyst_phase_v_squared = [35.0, 0.0]
anti_hyst_interval = [10.0]
[look_up_table]
10.0;20.0;30.0;40.0;1555.0;0
11.0;21.0;31.0;41.0;1554.0;0"""
        
        with patch("builtins.open", mock_open(read_data=content)):
            calibration = load_calibration("test.csv")
        
        assert calibration.model == "ATLAS"
        assert len(calibration.entries) == 2
        assert calibration.tune_settings.current == 280.0
        assert calibration.sweep_settings is None
    
    
    def test_load_calibration_file_not_found(self):
        """Test load_calibration raises appropriate error for non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_calibration("nonexistent.csv")

    @pytest.mark.parametrize(
        "content",
        [
            # Missing [default_settings] section
            """
    laser_model = ATLAS
    tune_diode_current = 280.0
    tune_tec_target = 25.0
    anti_hyst_phase_v_squared = [35.0, 0.0]
    anti_hyst_interval = [10.0]
    [look_up_table]
    10.0;20.0;30.0;40.0;1555.0;0
    11.0;21.0;31.0;41.0;1554.0;0
    """,
            # Missing [look_up_table] section
            """
    [default_settings]
    laser_model = ATLAS
    tune_diode_current = 280.0
    tune_tec_target = 25.0
    anti_hyst_phase_v_squared = [35.0, 0.0]
    anti_hyst_interval = [10.0]
    10.0;20.0;30.0;40.0;1555.0;0
    11.0;21.0;31.0;41.0;1554.0;0
    """,
            # Malformed defaults block (missing tune_tec_target)
            """
    [default_settings]
    laser_model = ATLAS
    tune_diode_current = 280.0
    anti_hyst_phase_v_squared = [35.0, 0.0]
    anti_hyst_interval = [10.0]
    [look_up_table]
    10.0;20.0;30.0;40.0;1555.0;0
    """,        
            # Too many columns in data rows
            """
    [default_settings]
    laser_model = ATLAS
    tune_diode_current = 280.0
    tune_tec_target = 25.0
    anti_hyst_phase_v_squared = [35.0, 0.0]
    anti_hyst_interval = [10.0]
    [look_up_table]
    10.0;20.0;30.0;12.3;122.98;1555.0;0
    10.0;20.0;30.0;12.3;122.98;1555.0;0
    10.0;20.0;30.0;12.3;122.98;1555.0;0
    10.0;20.0;30.0;12.3;122.98;1555.0;0
    10.0;20.0;30.0;12.3;122.98;1555.0;0
    """,
        ],
        ids=[
            "missing_default_settings_header",
            "missing_lookup_table_header", 
            "missing_required_parameter",
            "extra_columns_in_data"
        ]
    )
    def test_incorrect_file_formats(self, content):
        with patch("builtins.open", mock_open(read_data=content)):
            with pytest.raises(CalibrationError):
                load_calibration("test.csv")



class TestCalibrationEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_calibration_with_empty_entries(self):
        """Test Calibration with empty entries list."""
        with pytest.raises(CalibrationError):
            Calibration(
                model="ATLAS",
                entries=[],
                tune_settings=SAMPLE_TUNE_SETTING,
                sweep_settings=None
            )
    
    def test_parse_rows_empty_content(self):
        """Test _parse_rows with empty content."""
        content = ""
        f = StringIO(content)
        
        entries = _parse_rows(f, "ATLAS")
        assert len(entries) == 0
    
    
    def test_comet_mode_hop_tracking(self):
        """Test COMET mode hop tracking logic."""
        content = """
10.0;20.0;30.0;40.0;1555.0;0 
11.0;21.0;31.0;41.0;1554.0;1
12.0;22.0;32.0;42.0;1553.0;1
13.0;23.0;33.0;43.0;1552.0;0
14.0;24.0;34.0;44.0;1551.0;0
14.0;24.0;34.0;44.0;1551.0;0
14.0;24.0;34.0;44.0;1551.0;1
14.0;24.0;34.0;44.0;1551.0;1
14.0;24.0;34.0;44.0;1551.0;0"""
        f = StringIO(content)
        
        entries = _parse_rows(f, "COMET")
        
        # Verify mode index progression through mode hop
        assert entries[0].mode_index == 1  # normal
        assert entries[1].mode_index == 2  # hop start, same mode
        assert entries[2].mode_index == 2  # still in hop
        assert entries[3].mode_index == 2  # hop ended, mode incremented
        assert entries[4].mode_index == 2  # continues in new mode
        assert entries[5].mode_index == 2  # continues in new mode
        assert entries[6].mode_index == 3  # continues in new mode
        assert entries[7].mode_index == 3  # continues in new mode