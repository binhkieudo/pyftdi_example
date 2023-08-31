#!/usr/bin/env python3

from pyftdi.i2c import *

# Instantiate an I2C controller
i2c = I2cController()

# Configure the first interface (IF/1) of the FTDI device as an I2C master
i2c.configure('ftdi:///1')

# Get a port to an I2C slave device
slave = i2c.get_port(0x34)

# Select page 3 (rail 4)
slave.write([0x00, 0x03])

# Set vout to 3.3V
# From SLUU337
# VOUT_COMMAND = 0x21
# vout = 3.3 V -> 3.3*2^12 = 13516 = 0x34CC
slave.write ([0x21, 0xcc, 0x34])

# arr = [0x34, 0xcc, 0x21]
# send 1 bytes, then receive 1 bytes
# slave.write([0x21, 0xCC, 0x34])
