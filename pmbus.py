#!/usr/bin/env python3

from pyftdi.i2c import I2cController

# ftdi_options = {'frequency': int(400000), 'clockstretching': True,
#                 'initial': 0x78, 'direction': 0x78}

ftdi_options = {'frequency': int(1000)}

i2c_master = I2cController()
i2c_master.configure('ftdi://ftdi:232h/1', **ftdi_options)


slave = i2c_master.get_port(0x34)

# Read id
# i2c_master.write(0x34, [0xfd], relax=False)
# dev_id = i2c_master.read(0x34, 33, relax=True)
# print (dev_id)

# Read vout mode
i2c_master.write(0x34, [0x20], relax=False)
vout_mode = i2c_master.read(0x34, 2, relax=True)
print (vout_mode)