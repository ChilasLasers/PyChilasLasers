from abc import ABC, abstractmethod

class LaserComponent(ABC):

    @property
    @abstractmethod
    def value(self) -> float:
        pass

    @property
    def min_value(self) -> float:
        return self._min

    @property
    def max_value(self) -> float:
        return self._max

    @property
    def unit(self) -> str:
        return self._unit