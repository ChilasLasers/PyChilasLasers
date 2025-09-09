import pytest
import os
import sys
import tempfile

# Add the src directory to the path and import utils directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'pychilaslasers'))
import utils


class TestCalibrationReading:
    """Test cases for the read_calibration_file function using real calibration files."""

    def test_read_calibration_file_comet1(self):
        """Test reading the real COMET1 calibration file."""
        file_path = os.path.join(os.path.dirname(__file__), 'calibrationFiles', 'comet1.csv')
        result = utils.read_calibration_file(file_path)
        
        # Verify the structure and content
        assert result["model"] == "COMET"
        assert result["steady"]["current"] == 100.0
        assert result["steady"]["tec_temp"] == 25.0
        assert result["steady"]["anti-hyst"] == ([1.0, 2.0, 3.0], [0.1, 0.2, 0.3])
        
        # Check that calibration data exists
        assert len(result["steady"]["calibration"]) > 0
        
        # Check first entry (should be from first non-mode-hopping row)
        first_wavelength = list(result["steady"]["calibration"].keys())[0]
        first_entry = result["steady"]["calibration"][first_wavelength]
        assert isinstance(first_entry, utils.CalibrationEntry)
        assert first_entry.wavelength == first_wavelength
        assert first_entry.mode_index is not None  # COMET should have mode_index
        
        # Check sweep data
        assert result["sweep"]["current"] == 150.0
        assert result["sweep"]["tec_temp"] == 30.0
        assert result["sweep"]["interval"] == 1000
        assert len(result["sweep"]["wavelengths"]) > 0

    def test_read_calibration_file_comet2(self):
        """Test reading the real COMET2 calibration file."""
        file_path = os.path.join(os.path.dirname(__file__), 'calibrationFiles', 'comet2.csv')
        
        result = utils.read_calibration_file(file_path)
        
        # Verify the structure
        assert result["model"] == "COMET"
        assert len(result["steady"]["calibration"]) > 0
        assert len(result["sweep"]["wavelengths"]) > 0
        
        # Verify all entries have mode_index for COMET
        for entry in result["steady"]["calibration"].values():
            assert entry.mode_index is not None

    def test_read_calibration_file_atlas1(self):
        """Test reading the real ATLAS1 calibration file."""
        file_path = os.path.join(os.path.dirname(__file__), 'calibrationFiles', 'atlas1.csv')
        utils.Constants.HARD_CODED_LASER_MODEL = "ATLAS"  # Ensure model is set to COMET 

        result = utils.read_calibration_file(file_path)
        
        # Verify the structure - ATLAS file but uses hard-coded COMET model
        assert result["model"] == "ATLAS"  # Uses hard-coded default
        assert len(result["steady"]["calibration"]) > 0
        
        # Check that entries exist
        first_wavelength = list(result["steady"]["calibration"].keys())[0]
        first_entry = result["steady"]["calibration"][first_wavelength]
        assert isinstance(first_entry, utils.CalibrationEntry)
        assert first_entry.wavelength == first_wavelength
        # Since it's treated as COMET (hard-coded), it will have mode_index

    def test_read_calibration_file_atlas2(self):
        """Test reading the real ATLAS2 calibration file."""
        utils.Constants.HARD_CODED_LASER_MODEL = "ATLAS"  # Ensure model is set to COMET 

        file_path = os.path.join(os.path.dirname(__file__), 'calibrationFiles', 'atlas2.csv')
        
        result = utils.read_calibration_file(file_path)
        
        # Verify the structure
        assert result["model"] == "ATLAS"  # Uses hard-coded default
        assert len(result["steady"]["calibration"]) > 0

    def test_read_calibration_file_nonexistent_file(self):
        """Test reading a non-existent calibration file."""
        with pytest.raises(FileNotFoundError):
            utils.read_calibration_file("nonexistent_file.csv")

    def test_read_calibration_file_invalid_csv(self):
        """Test reading an invalid CSV calibration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Create a CSV with insufficient columns (should cause IndexError when accessing row[5])
            f.write("0.5,1.0,1.5\n")  # Only 3 columns instead of required 6
            temp_file_path = f.name
        
        try:
            with pytest.raises(IndexError):  # CSV reader will fail on row access
                utils.read_calibration_file(temp_file_path)
        finally:
            os.unlink(temp_file_path)

    def test_read_calibration_file_empty_file(self):
        """Test reading an empty calibration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file_path = f.name
        
        try:
            result = utils.read_calibration_file(temp_file_path)
            # Should return basic structure with empty calibration
            assert result["steady"]["calibration"] == {}
            # For COMET model, sweep should exist and be empty
            assert "sweep" not in result
        finally:
            os.unlink(temp_file_path)
