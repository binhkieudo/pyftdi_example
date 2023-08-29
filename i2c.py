#!/usr/bin/env python3

import board
import busio
import adafruit_mcp9600
import os

import adafruit_platformdetect.constants.boards as ap_board
from adafruit_blinka.agnostic import board_id, detector


board.board_id = ap_board.FTDI_FT232H

print (dir(board))

#i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
#mcp = adafruit_mcp9600.MCP9600(i2c)

#print(mcp.temperature)