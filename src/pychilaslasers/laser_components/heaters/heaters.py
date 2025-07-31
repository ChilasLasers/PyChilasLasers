"""
Heater component classes.
<p>
This module implements heater components that control thermal elements in the laser.
Includes individual heater types. These are only available in manual mode.
<p>
Authors: SDU
Last Revision: July 30, 2025 - Enhanced documentation and improved code formatting
"""

from pychilaslasers.laser_components.diode import LaserComponent
from pychilaslasers.laser_components.heaters.heater_channels import HeaterChannel
from abc import abstractmethod


class Heater(LaserComponent):
    """Base class for laser heater components.
    <p>
    Provides common functionality for all heater types including
    value setting and channel management.
    
    Attributes:
        channel: The heater channel identifier.
        value: The current heater drive value.
        min_value: Minimum heater value.
        max_value: Maximum heater value.
        unit: Heater value unit.
    """

    def __init__(self, laser) -> None:
        """Initialize the heater component.
        <p>
        Sets up the heater with its operating limits and units by
        querying the laser hardware.
        
        Args:
            laser: The laser instance to control.
        """
        super().__init__(laser)
        self._min: float = float(laser.query(f"DRV:LIM:MIN? {self.channel.value}"))
        self._max: float = float(laser.query(f"DRV:LIM:MAX? {self.channel.value}"))
        self._unit: str = laser.query(f"DRV:UNIT? {self.channel.value}").strip()

    ########## Properties (Getters/Setters) ##########

    @property
    @abstractmethod
    def channel(self) -> HeaterChannel:
        """Get the heater channel identifier.
        <p>
        Must be implemented by subclasses to specify which
        heater channel this component controls.
        
        Returns:
            The channel identifier for this heater.
        """
        pass
    
    @property
    def value(self) -> float:
        """Get the current heater drive value.

        Returns:
            The current heater drive value.
        """
        return float(self._laser.query(f"DRV:D? {self.channel.value:d}"))
    
    @value.setter
    def value(self, value: float) -> None:  
        """Set the heater drive value.

        Args:
            value: The heater drive value to set.
            
        Raises:
            ValueError: If value is not a number or outside valid range.
        """
        # Validate the value
        if not isinstance(value, (int, float)):
            raise ValueError("Heater value must be a number.")
        if value < self._min or value > self._max:
            raise ValueError(f"Heater value must be between {self._min} and {self._max} {self._unit}.")

        self._laser.query(f"DRV:D {self.channel.value:d} {value:.3f}")


class TunableCoupler(Heater):
    """Tunable coupler heater component."""

    @property
    def channel(self) -> HeaterChannel:
        """Get the tunable coupler channel."""
        return HeaterChannel.TUNABLE_COUPLER

class LargeRing(Heater):
    """Large ring heater component."""

    @property
    def channel(self) -> HeaterChannel:
        """Get the large ring channel."""
        return HeaterChannel.RING_LARGE

class SmallRing(Heater):
    """Small ring heater component."""

    @property
    def channel(self) -> HeaterChannel:
        """Get the small ring channel."""
        return HeaterChannel.RING_SMALL
    
class PhaseSection(Heater):
    """Phase section heater component."""

    @property
    def channel(self) -> HeaterChannel:
        """Get the phase section channel."""
        return HeaterChannel.PHASE_SECTION