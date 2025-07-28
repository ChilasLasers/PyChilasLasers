from pychilaslasers.laser_components.diode import LaserComponent
from pychilaslasers.laser_components.heaters.heater_channels import HeaterChannel
from abc import abstractmethod


class Heater(LaserComponent):

    def __init__(self, laser) -> None:
        super().__init__()
        self._laser = laser
        self._min: float = float(laser.query(f"DRV:LIM:MIN? {self.channel.value}"))
        self._max: float = float(laser.query(f"DRV:LIM:MAX? {self.channel.value}"))
        self._unit: str = laser.query(f"DRV:UNIT? {self.channel.value}").strip()

    @property
    @abstractmethod
    def channel(self) -> HeaterChannel:
        """Get the heater channel."""
        pass
    
    @property
    def value(self) -> float:
        """Gets the heater value.

        Returns:
            float: The heater value.
        """
        return float(self._laser.query(f"DRV:D? {self.channel.value:d}"))
    
    @value.setter
    def value(self, value: float) -> None:  
        """Sets the heater value.

        Args:
            value (float): The heater value to be set.
        """
        # Validate the value
        if not isinstance(value, (int, float)):
            raise ValueError("Heater value must be a number.")
        if value < self._min or value > self._max:
            raise ValueError(f"Heater value must be between {self._min} and {self._max} {self._unit}.")

        self._laser.query(f"DRV:D {self.channel.value:d} {value:.3f}")


class TunableCoupler(Heater):

    @property
    def channel(self) -> HeaterChannel:
        return HeaterChannel.TUNABLE_COUPLER

class LargeRing(Heater):

    @property
    def channel(self) -> HeaterChannel:
        return HeaterChannel.RING_LARGE

class SmallRing(Heater):

    @property
    def channel(self) -> HeaterChannel:
        return HeaterChannel.RING_SMALL
    
class PhaseSection(Heater):

    @property
    def channel(self) -> HeaterChannel:
        return HeaterChannel.PHASE_SECTION