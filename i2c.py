#!/usr/bin/env python3

from pyftdi.i2c import *

# Instantiate an I2C controller
i2c = I2cController()
# Configure the first interface (IF/1) of the FTDI device as an I2C master
i2c.configure('ftdi://ftdi:232h:3:10/1')

# Get a port to an I2C slave device
slave = i2c.get_port(0x34)

# Read device id
device_id = slave.exchange([0xfd], 32)

print (device_id)

# Select page 3 (rail 4)
#slave.write([0x00, 0x03])

	#   //  Now bring down the VOUT_OV_FAULT_LIMIT to 3.63V (3.3 \+ (15% of 3.3))
	#   //  0x3a14 * 2^(-12) = 3.63V
	#   //  i2c write 0x65 0x44 0x28 0x74
	#   Status = IICWriteByte(ZC706_PMBUS_ADDR, WriteBuffer[0], WriteBuffer\+1, 2);
#slave.write ([0x40, 0x28, 0x74])

# Set vout max
#slave.write ([0x24, 0x28, 0x74])

# Set vout to 3.3V
# From SLUU337
# VOUT_COMMAND = 0x21
# vout = 3.3 V -> 3.3*2^12 = 13516 = 0x34CC
#slave.write ([0x21, 0x99, 0x69])

# Set power good to 3.1
#    0x3199 * 2^(-12)  = 3.1
#slave.write ([0x5e, 0x63, 0x33])

# Store everything
#slave.write ([0x11])

