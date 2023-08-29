#!/usr/bin/env python3
from pyftdi.spi import SpiController, SpiIOError

CMD_JEDEC_ID = 0x9f
def main():
    spi = SpiController()

    # Configure the first interface (IF/1) of the FTDI device as a SPI master
    spi.configure('ftdi:///1')

    # Get a port to a SPI slave w/ /CS on A*BUS3 and SPI mode 0 @ 12MHz
    slave = spi.get_port(cs=0, freq=12E6, mode=0)

    # Request the JEDEC ID from the SPI slave
    jedec_id = slave.exchange([0x9f], 3)

    print (jedec_id.hex())

if __name__ == "__main__":
    main()
