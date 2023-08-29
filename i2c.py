#!/usr/bin/env python3

import board
import busio
import adafruit_mcp9600
import os

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
mcp = adafruit_mcp9600.MCP9600(i2c)

print(mcp.temperature)