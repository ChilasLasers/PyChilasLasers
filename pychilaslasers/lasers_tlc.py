#!/usr/bin/env python
"""
TLCLaser class to communicate with TLC.
"""

from enum import IntEnum
import logging

from pychilaslasers import Laser


class HeaterChannelTLC(IntEnum):
    PHASE_SECTION = 5
    RING_LARGE = 3
    RING_SMALL = 4
    TUNABLE_COUPLER = 0

logger = logging.getLogger(__name__)

class TLCLaser(Laser):
    """TLC Laser class for Chilas lasers."""

    model = "Chilas TLM Laser"
    channel_config = HeaterChannelTLC

    def __init__(self, address=None, timeout=10.0):
        super().__init__(address, timeout)

    # Extra TEC commands
    # To be tested by WTG
    def set_tec_p(self, p_value):  # in mA/K
        str_query = "TEC:CTRL:PSHR " + str(p_value)
        self.write(str_query)

    def set_tec_i(self, i_value):  # in mA/(K*s)
        str_query = "TEC:CTRL:ISHR " + str(i_value)
        self.write(str_query)

    def set_tec_d(self, d_value):  # in (mA*s)/K
        str_query = "TEC:CTRL:DSHR " + str(d_value)
        self.write(str_query)

    def get_tec_p(self):
        return float(self.query("TEC:CTRL:PSHR?"))

    def get_tec_i(self):
        return float(self.query("TEC:CTRL:ISHR?"))

    def get_tec_d(self):
        return float(self.query("TEC:CTRL:DSHR?"))

    # Initialize cycler table for TLC
    def initialize_cycler_table(self):
        self.set_cycler_count(self.cycler_table_length)
        logger.info("Initializing cycler table")
        for i in range(self.cycler_table_length):
            self.initialize_cycler_row(i)
            logger.info(str(i + 1) + "/" + str(self.cycler_table_length))
        logger.info("Initializing cycler table Done!")

    # Initialize cycler row for TLC
    def initialize_cycler_row(self, row: int):
        self.set_driver_value(
            HeaterChannelTLC.PHASE_SECTION,
            float(self.cycler_table[row, type(self).cycler_config.PHASE_SECTION]),
        )
        self.set_driver_value(
            HeaterChannelTLC.RING_LARGE,
            float(self.cycler_table[row, type(self).cycler_config.RING_LARGE]),
        )  # Large ring
        self.set_driver_value(
            HeaterChannelTLC.RING_SMALL,
            float(self.cycler_table[row, type(self).cycler_config.RING_SMALL]),
        )  # Small ring
        self.set_driver_value(
            HeaterChannelTLC.TUNABLE_COUPLER,
            float(self.cycler_table[row, type(self).cycler_config.TUNABLE_COUPLER]),
        )  # Tunable coupler
        self.save_cycler_entry(row)
