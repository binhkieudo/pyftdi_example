#!/usr/bin/env python3

from io import StringIO
from contextlib import redirect_stdout
from collections import namedtuple
import struct
from pyftdi.i2c import I2cController, I2cNackError
from time import sleep
from pyftdi.ftdi import Ftdi

def toNametuple(dict_data) -> namedtuple:
    return namedtuple("X", dict_data.keys())(*tuple(map(
        lambda x: x if not isinstance(x, dict) else toNametuple(x),
        dict_data.values())))

class UCD92xx:
    pmbus_dict = {'page'            : 0x00, 
                  'operation'       : 0x01, 
                  'on_off_config'   : 0x02, 
                  'clear_faults'    : 0x03, 
                  'phase'           : 0x04, 
                  'page_plus_write' : 0x05, 
                  'page_plus_read'  : 0x06, 
                  'zone_config'     : 0x07, 
                  'zone_active'     : 0x08, 
                  'reserved_09'     : 0x09, 
                  'reserved_0a'     : 0x0a, 
                  'reserved_0b'     : 0x0b, 
                  'reserved_0c'     : 0x0c, 
                  'reserved_0d'     : 0x0d, 
                  'reserved_0e'     : 0x0e, 
                  'reserved_0f'     : 0x0f, 
                  'write_protect'   : 0x10, 
                  'store_default_all'   : 0x11, 
                  'restore_default_all' : 0x12, 
                  'store_default_code'  : 0x13, 
                  'restore_default_code': 0x14, 
                  'store_user_all'      : 0x15, 
                  'restore_user_all'    : 0x16, 
                  'store_user_code'     : 0x17, 
                  'restore_user_code'   : 0x18, 
                  'capability': 0x19, 
                  'query': 0x1a, 
                  'smbalert_mask': 0x1b, 
                  'reserved_1c': 0x1c, 
                  'reserved_1d': 0x1d, 
                  'reserved_1e': 0x1e, 
                  'reserved_1f': 0x1f, 
                  'vout_mode': 0x20, 
                  'vout_command': 0x21, 
                  'vout_trim': 0x22, 
                  'vout_cal_offset': 0x23, 
                  'vout_max': 0x24, 
                  'vout_margin_high': 0x25, 
                  'vout_margin_low': 0x26, 
                  'vout_transition_rate': 0x27, 
                  'vout_droop': 0x28, 
                  'vout_scale_loop': 0x29, 
                  'vout_scale_monitor': 0x2a, 
                  'vout_min': 0x2b, 
                  'reserved_2c': 0x2c, 
                  'reserved_2d': 0x2d, 
                  'reserved_2e': 0x2e, 
                  'reserved_2f': 0x2f, 
                  'coefficients': 0x30, 
                  'pout_max': 0x31, 
                  'max_duty': 0x32, 
                  'frequency_switch': 0x33, 
                  'power_mode': 0x34, 
                  'vin_on': 0x35, 
                  'vin_off': 0x36, 
                  'interleave': 0x37, 
                  'iout_cal_gain': 0x38, 
                  'iout_cal_offset': 0x39, 
                  'fan_config_1_2': 0x3a, 
                  'fan_command_1': 0x3b, 
                  'fan_command_2': 0x3c, 
                  'fan_config_3_4': 0x3d, 
                  'fan_command_3': 0x3e, 
                  'fan_command_4': 0x3f, 
                  'vout_ov_fault_limit': 0x40, 
                  'vout_ov_fault_response': 0x41, 
                  'vout_ov_warn_limit': 0x42, 
                  'vout_uv_warn_limit': 0x43, 
                  'vout_uv_fault_limit': 0x44, 
                  'vout_uv_fault_response': 0x45, 
                  'iout_oc_fault_limit': 0x46, 
                  'iout_oc_fault_response': 0x47, 
                  'iout_oc_lv_fault_limit': 0x48, 
                  'iout_oc_lv_fault_response': 0x49, 
                  'iout_oc_warn_limit': 0x4a, 
                  'iout_uc_fault_limit': 0x4b, 
                  'iout_uc_fault_response': 0x4c, 
                  'reserved_4d': 0x4d, 
                  'reserved_4e': 0x4e, 
                  'ot_fault_limit': 0x4f, 
                  'ot_fault_response': 0x50, 
                  'ot_warn_limit': 0x51, 
                  'ut_warn_limit': 0x52, 
                  'ut_fault_limit': 0x53, 
                  'ut_fault_response': 0x54, 
                  'vin_ov_fault_limit': 0x55, 
                  'vin_ov_fault_response': 0x56, 
                  'vin_ov_warn_limit': 0x57, 
                  'vin_uv_warn_limit': 0x58, 
                  'vin_uv_fault_limit': 0x59, 
                  'vin_uv_fault_response': 0x5a, 
                  'iin_oc_fault_limit': 0x5b, 
                  'iin_oc_fault_response': 0x5c, 
                  'iin_oc_warn_limit': 0x5d, 
                  'power_good_on': 0x5e, 
                  'power_good_off': 0x5f, 
                  'ton_delay': 0x60, 
                  'ton_rise': 0x61, 
                  'ton_max_fault_limit': 0x62, 
                  'ton_max_fault_response': 0x63, 
                  'toff_delay': 0x64, 
                  'toff_fall': 0x65, 
                  'toff_max_warn_limit': 0x66, 
                  'reserved_67': 0x67, 
                  'pout_op_fault_limit': 0x68, 
                  'pout_op_fault_response': 0x69, 
                  'pout_op_warn_limit': 0x6a, 
                  'pin_op_warn_limit': 0x6b, 
                  'reserved_6c': 0x6c, 
                  'reserved_6d': 0x6d, 
                  'reserved_6e': 0x6e, 
                  'reserved_6f': 0x6f, 
                  'reserved_70': 0x70, 
                  'reserved_71': 0x71, 
                  'reserved_72': 0x72, 
                  'reserved_73': 0x73, 
                  'reserved_74': 0x74, 
                  'reserved_75': 0x75, 
                  'reserved_76': 0x76, 
                  'reserved_77': 0x77, 
                  'status_byte': 0x78, 
                  'status_word': 0x79, 
                  'status_vout': 0x7a, 
                  'status_iout': 0x7b, 
                  'status_input': 0x7c, 
                  'status_temperature': 0x7d, 
                  'status_cml': 0x7e, 
                  'status_other': 0x7f, 
                  'status_mfr_specific': 0x80, 
                  'status_fans_1_2': 0x81, 
                  'status_fans_3_4': 0x82, 
                  'read_kwh_in': 0x83, 
                  'read_kwh_out': 0x84, 
                  'read_kwh_config': 0x85, 
                  'read_ein': 0x86, 
                  'read_eout': 0x87, 
                  'read_vin': 0x88, 
                  'read_iin': 0x89, 
                  'read_vcap': 0x8a, 
                  'read_vout': 0x8b, 
                  'read_iout': 0x8c, 
                  'read_temperature_1': 0x8d, 
                  'read_temperature_2': 0x8e, 
                  'read_temperature_3': 0x8f, 
                  'read_fan_speed_1': 0x90,
                  'read_fan_speed_2': 0x91, 
                  'read_fan_speed_3': 0x92, 
                  'read_fan_speed_4': 0x93, 
                  'read_duty_cycle': 0x94, 
                  'read_frequency': 0x95, 
                  'read_pout': 0x96, 
                  'read_pin': 0x97, 
                  'pmbus_revision': 0x98, 
                  'mfr_id': 0x99, 
                  'mfr_model': 0x9a, 
                  'mfr_revision': 0x9b, 
                  'mfr_location': 0x9c, 
                  'mfr_date': 0x9d, 
                  'mfr_serial': 0x9e, 
                  'app_profile_support': 0x9f, 
                  'mfr_vin_min': 0xa0, 
                  'mfr_vin_max': 0xa1, 
                  'mfr_iin_max': 0xa2, 
                  'mfr_pin_max': 0xa3, 
                  'mfr_vout_min': 0xa4, 
                  'mfr_vout_max': 0xa5, 
                  'mfr_iout_max': 0xa6, 
                  'mfr_pout_max': 0xa7, 
                  'mfr_tambient_max': 0xa8, 
                  'mfr_tambient_min': 0xa9, 
                  'mfr_efficiency_ll': 0xaa, 
                  'mfr_efficiency_hl': 0xab, 
                  'mfr_pin_accuracy': 0xac, 
                  'ic_device_id': 0xad, 
                  'ic_device_rev': 0xae, 
                  'reserved_af': 0xaf, 
                  'user_data_00': 0xb0, 
                  'user_data_01': 0xb1, 
                  'user_data_02': 0xb2, 
                  'user_data_03': 0xb3, 
                  'user_data_04': 0xb4, 
                  'user_data_05': 0xb5, 
                  'user_data_06': 0xb6, 
                  'user_data_07': 0xb7, 
                  'user_data_08': 0xb8, 
                  'user_data_09': 0xb9, 
                  'user_data_10': 0xba, 
                  'user_data_11': 0xbb, 
                  'user_data_12': 0xbc, 
                  'user_data_13': 0xbd, 
                  'user_data_14': 0xbe, 
                  'user_data_15': 0xbf, 
                  'mfr_max_temp_1': 0xc0, 
                  'mfr_max_temp_2': 0xc1, 
                  'mfr_max_temp_3': 0xc2, 
                  'reserved_c3': 0xc3, 
                  'mfr_specific_c4': 0xc4, 
                  'mfr_specific_c5': 0xc5, 
                  'mfr_specific_c6': 0xc6, 
                  'mfr_specific_c7': 0xc7, 
                  'mfr_specific_c8': 0xc8, 
                  'mfr_specific_c9': 0xc9, 
                  'mfr_specific_ca': 0xca, 
                  'mfr_specific_cb': 0xcb, 
                  'mfr_specific_cc': 0xcc, 
                  'mfr_specific_cd': 0xcd, 
                  'mfr_specific_ce': 0xce, 
                  'mfr_specific_cf': 0xcf, 
                  'mfr_specific_d0': 0xd0, 
                  'mfr_specific_d1': 0xd1, 
                  'mfr_specific_d2': 0xd2, 
                  'mfr_specific_d3': 0xd3, 
                  'mfr_specific_d4': 0xd4, 
                  'mfr_specific_d5': 0xd5, 
                  'mfr_specific_d6': 0xd6, 
                  'mfr_specific_d7': 0xd7, 
                  'mfr_specific_d8': 0xd8, 
                  'mfr_specific_d9': 0xd9, 
                  'mfr_specific_da': 0xda, 
                  'mfr_specific_db': 0xdb, 
                  'mfr_specific_dc': 0xdc, 
                  'mfr_specific_dd': 0xdd, 
                  'mfr_specific_de': 0xde, 
                  'mfr_specific_df': 0xdf, 
                  'mfr_specific_e0': 0xe0, 
                  'mfr_specific_e1': 0xe1, 
                  'mfr_specific_e2': 0xe2, 
                  'mfr_specific_e3': 0xe3, 
                  'mfr_specific_e4': 0xe4, 
                  'mfr_specific_e5': 0xe5, 
                  'mfr_specific_e6': 0xe6, 
                  'mfr_specific_e7': 0xe7, 
                  'mfr_specific_e8': 0xe8, 
                  'mfr_specific_e9': 0xe9, 
                  'mfr_specific_ea': 0xea, 
                  'mfr_specific_eb': 0xeb, 
                  'mfr_specific_ec': 0xec, 
                  'mfr_specific_ed': 0xed, 
                  'mfr_specific_ee': 0xee, 
                  'mfr_specific_ef': 0xef, 
                  'mfr_specific_f0': 0xf0, 
                  'mfr_specific_f1': 0xf1, 
                  'mfr_specific_f2': 0xf2, 
                  'mfr_specific_f3': 0xf3, 
                  'mfr_specific_f4': 0xf4, 
                  'mfr_specific_f5': 0xf5, 
                  'mfr_specific_f6': 0xf6, 
                  'mfr_specific_f7': 0xf7, 
                  'mfr_specific_f8': 0xf8, 
                  'mfr_specific_f9': 0xf9, 
                  'mfr_specific_fa': 0xfa, 
                  'mfr_specific_fb': 0xfb, 
                  'mfr_specific_fc': 0xfc, 
                  'mfr_specific_fd': 0xfd,
                  'mfr_specific_command': 0xfe, 
                  'pmbus_command_ext': 0xff}  # noqa: E501

    commands = toNametuple(pmbus_dict)

    def __init__(self, pmbus_addr:int, frequency=1000, clockstretching=False) -> None:

        ftdi_options = {'frequency': int(frequency), 'clockstretching': clockstretching, 'initial': 0xff78, 'direction': 0xff78}

        io_buffer = StringIO()
        with redirect_stdout(io_buffer):
            try:
                Ftdi.show_devices()  # normally prints to stdout and returns None
            except ValueError:
                print('No backend available, did you install libusb driver?\n'
                  'This library requires that the driver your OS associates\n'
                  'with FTDI device by default should be overriden to use\n'
                  'the "libusb-win32" driver. See README.txt')
                raise ValueError('No backend available')
        response = io_buffer.getvalue()
        response = response.lstrip('Available interfaces:').strip()

        connections = []
        for connection in response.split('\n'):
            if connection == '':
                continue
            url = connection.split()
            connections.append(url[0])

        if not connections:
            raise IOError("No FTDI devices found. Check USB connections..."
                      " Restart python to try again.")

        if (len(connections) > 1):
            for i in range (0, len(connections)):
                print ("[%d] %s" % (i, connections[i]))
            selected = int(input ("Select an interface: "))
            self.url = connections[selected]
        else:
            self.url = connections[0]
        
        # Create ftdi connection
        self.i2c_master = I2cController()
        self.i2c_master.configure(self.url, **ftdi_options)
        self.i2c_slave = self.i2c_master.get_port(pmbus_addr)
        
        self.gpio = self.i2c_master.get_gpio()
        self.gpio_width = self.gpio.width
        self.gpio_pins = self.gpio.all_pins & ((1 << self.gpio_width) - 1)
        self.gpio_master_mask = self.i2c_master._gpio_mask
        self.gpio_ctrl_mask = 0x0008

        self.exponent = self.get_vout_mode()
        
        return None

    def get_crc(self, val, byteorder: str = 'big'):
        """
        Parameters
        ----------
        val (int): value or message to parse for CRC8 using X^8+X^2+X+1
        byteorder (str): 'big' default or 'little' for endianess of the message

        Returns
        -------
        int : CRC byte

        """
        crc = 0  # initialize
        PECtable = [0, 7, 14, 9, 28, 27, 18, 21, 56, 63, 54, 49, 36, 
                    35, 42, 45, 112, 119, 126, 121, 108, 107, 98, 101, 
                    72, 79, 70,  65, 84, 83, 90, 93, 224, 231, 238, 233, 
                    252, 251, 242, 245, 216, 223, 214, 209, 196, 195, 202, 
                    205, 144, 151, 158, 153, 140, 139, 130, 133, 168, 175, 
                    166, 161, 180, 179, 186, 189, 199, 192, 201, 206, 219, 
                    220, 213, 210, 255, 248, 241, 246, 227, 228, 237, 234, 
                    183, 176, 185, 190, 171, 172, 165, 162, 143, 136, 129, 
                    134, 147, 148, 157, 154, 39, 32, 41, 46, 59, 60, 53, 50, 
                    31, 24, 17, 22, 3, 4, 13, 10, 87, 80, 89, 94, 75, 76, 69, 
                    66, 111, 104, 97, 102, 115, 116, 125, 122, 137, 142, 135, 
                    128, 149, 146, 155, 156, 177, 182, 191, 184, 173, 170, 163, 
                    164, 249, 254, 247, 240, 229, 226, 235, 236, 193, 198, 207, 
                    200, 221, 218, 211, 212, 105, 110, 103, 96, 117, 114, 123, 
                    124, 81, 86, 95, 88, 77, 74, 67, 68, 25, 30, 23, 16, 5, 2, 
                    11, 12, 33, 38, 47, 40, 61, 58, 51, 52, 78, 73, 64, 71, 82, 
                    85, 92, 91, 118, 113, 120, 127, 106, 109, 100, 99, 62, 57, 
                    48, 55, 34, 37, 44, 43, 6, 1, 8, 15, 26, 29, 20, 19, 174, 
                    169, 160, 167, 178, 181, 188, 187, 150, 145, 152, 159, 138, 
                    141, 132, 131, 222, 217, 208, 215, 194, 197, 204, 203, 230, 
                    225, 232, 239, 250, 253, 244, 243]  # noqa: E501
        # CRC8 lookup table for PMBus

        message = val.to_bytes((val.bit_length() + 7) // 8,
                               byteorder=byteorder, signed=False)
        for i in range(len(message)):
            pecindex = crc ^ message[i]
            crc = PECtable[pecindex]

        return crc
    
    @staticmethod
    def bytes2uint(byte_array, split_bytes: bool = False, endian='little'):
        """
        bytes2uint(byte_array, split_bytes: bool = False, endian='little')

        Converts a byte array of arbitrary length to an unsigned integer. Byte
        order can be specified with the "endian" arguement. Byte array can
        optionally be returns as a tuple of integers corresponding with each
        byte.

        Args:
            byte_array (bytes, bytearray): byte array to convert
            split_bytes (bool, optional): Whether to split "byte_array:" into a
                                          tuple of bytes (True) or interpret
                                          the value as a single unsigned
                                          integer (False). Defaults to False.
            endian (str, optional): [description]. Defaults to 'little'.

        Returns:
            [type]: [description]
        """

        n = len(byte_array)

        if n < 1:
            return None
        elif n == 1:
            return struct.unpack('B', byte_array)[0]

        endian = endian.lower()
        end_char = '<' if endian == 'little' else '>'

        if split_bytes:
            return tuple(struct.unpack(end_char + 'B'*n, byte_array))

        if n == 2:
            return struct.unpack(f'{end_char}H', byte_array)[0]
        elif n == 4:
            return struct.unpack(f'{end_char}I', byte_array)[0]

        # handles arbitrary lengths
        acc = 0
        for i, b in enumerate(struct.unpack(end_char + 'B'*n, byte_array)):
            acc += b << ((8*i) if endian == 'little' else (8*(n - i - 1)))
        return acc

    @staticmethod
    def uint2bytes(value: int, n_bytes: int, endian: str = 'little'):
        """
        uint2bytes(value: int, n_bytes: int, endian='little')

        Converts a non-negative integer into a bytearray of a specified length.
        Values that required a greater number of bytes to represent than what
        is specified will be truncated while values that can be represented in
        a smaller number bytes than the specified amount will be 0-padded

        Args:
            value (int): unsigned integer to convert
            n_bytes (int): number of bytes in the output byte-array
            endian (str, optional): byte-order. Valid options are 'little'
                                    (LSB first) and 'big' (MSB first). Defaults
                                    to 'little'.

        Raises:
            ValueError: raised if a negative integer or other datatype is
                        passed through value. Or alternatively if an invalid
                        option for 'endian' is used.

        Returns:
            bytearray: the integer "value" stored in a byte-array with the
                       specified length and order.
        """

        if not (isinstance(value, int) and (value >= 0)):
            raise ValueError('Function can only convert positive integers')

        endian = endian.lower()
        end_char = '<' if endian == 'little' else '>'

        if endian == 'little':
            gen = ((value >> (8*i)) & 255 for i in range(n_bytes))
        elif endian == 'big':
            gen = ((value >> (8*i)) & 255 for i in range(n_bytes - 1, -1, -1))
        else:
            raise ValueError('Invalid value for kwarg "endian"')

        byte_array = struct.pack(f"{end_char}{'B'*n_bytes}", *gen)
        return byte_array
    
    @staticmethod
    def twos_complement(value: int, n_bits: int, reverse=False):
        """
        twos_complement(value, n_bits, reverse=False)

        Converts integers between two's complement and signed-integer formats.
        arbitrary bit lengths are supported by specifying the bit length
        (n_bits).

        Args:
            value (int): twos complent or signed integer value to convert
            n_bits (int): number of bits that constitue a packet
            reverse (bool, optional): whether to convert from twos complement
                    to signed (False) or from signed twos complement (True).
                    Defaults to False.

        Returns:
            int: converted value
        """

        if reverse:
            return (value + (1 << n_bits)) % (1 << n_bits)

        if (value & (1 << (n_bits - 1))) != 0:
            return value - (1 << n_bits)
        return value

    @classmethod
    def decode_lin11(cls, value: int):

        """
        decode_lin11(val)

        Decodes a "linear 11" formatted integer into a floating point number.
        The Linear 11 encoding scheme is similar to the floating point standard
        its structure is shown below:

        MSB                             LSB
        [   EXP   ][       MANTISSA       ]
        |<----      WORD LENGTH      ---->|

        Where the 2 byte word consists of a 5 bit exponent and an 11 bit
        mantissa. Both the mantissa and exponent are stored as two's complement
        numbers. The resulting float is calculated as:

        float = mantissa*(2^exponent)

        After converting the mantissa and exponent from twos complement to
        signed integers.

        Arguments:
            value {int} -- linear 11 formatted integer

        Returns:
            out {float} -- decoded value
        """
        return cls.extract_lin11(value=value)[2]

    @classmethod
    def extract_lin11(cls, value: int) -> "tuple(int, int, float)":
        """
        extract_lin11(val)

        Extracts a "linear 11" formatted integer into a its components of
        exponent, mantissa and si units floating point number.
        The Linear 11 encoding scheme is similar to the floating point standard
        its structure is shown below:

        MSB                             LSB
        [   EXP   ][       MANTISSA       ]
        |<----      WORD LENGTH      ---->|

        Where the 2 byte word consists of a 5 bit exponent and an 11 bit
        mantissa. Both the mantissa and exponent are stored as two's complement
        numbers. The resulting float is calculated as:

        float = mantissa*(2^exponent)

        After converting the mantissa and exponent from twos complement to
        signed integers.

        Arguments:
            value {int} -- linear 11 formatted integer

        Returns:
            tuple [int, int, float]: decoded value as exponent, mantissa, si
        """

        exp = (value & 0xf800) >> 11
        exp = cls.twos_complement(exp, 5)

        mantissa = value & 0x07ff
        mantissa = cls.twos_complement(mantissa, 11)

        si_float = float(mantissa*(2**exp))

        return (exp, mantissa, si_float)

    @classmethod
    def encode_lin11(cls, value: float, exp: int):

        """
        encode_lin11(val)

        Encodes a floating point number into a "linear 11" formatted integer.
        The Linear 11 encoding scheme is similar to the floating point standard
        its structure is shown below:

        MSB                             LSB
        [   EXP   ][       MANTISSA       ]
        |<----      WORD LENGTH      ---->|

        Where the 2 byte word consists of a 5 bit exponent and an 11 bit
        mantissa. Both the mantissa and exponent are stored as two's complement
        numbers. The resulting integer is calculated as:

        out = (Twos{exp} << 11) | Twos{(value * 2^-exp)}

        where 'Twos{x}' denotes converting x to a twos complement number

        Arguments:
            value {float} -- value to encode

            exp {int}  -- exponent to be use for encoding, this can differ
                          between firmware as well as between each signal.

        Returns:
            out {int} -- encoded linear 11 formatted integer
        """

        formatted_exp = cls.twos_complement(exp, 5, reverse=True)
        formatted_mant = 0x7FF & round(cls.twos_complement(value*(2**-exp),
                                                           11, reverse=True))

        return ((formatted_exp << 11) | (formatted_mant))

    def decode_ulin16(self, value: int) -> float:
        """
        decode_ulin16(value)

        Decodes an "unsigned linear 16" formatted integer into a floating point
        number. The structure of the unsigned linear 16 encoding scheme is
        shown below:

        MSB                                LSB
        [ INTEGER PART ][   FRACTIONAL PART  ]
        |<-------     WORD LENGTH    ------->|

        Where the 2 byte word consists of a 7 bit integer part and an
        [exponent] bit fractional part. Both parts are stored as
        unsigned integers. The resulting float is calculated as:

        float = value*(2^(-9))

        Arguments:
            value {int} -- integer value to decode

        Returns:
            out {float} -- decoded value
        """

        return value*(2**self.exponent)

    def encode_ulin16(self, value: float) -> int:
        """
        encode_ulin16(value)

        Encodes a floating point number  into an "unsigned linear 16" formatted
        integer number. The structure of the unsigned linear 16 encoding scheme
        is shown below:

        MSB                                LSB
        [ INTEGER PART ][   FRACTIONAL PART  ]
        |<-------     WORD LENGTH    ------->|

        Where the 2 byte word consists of a 7 bit integer part and an
        [exponent] bit fractional part. Both parts are stored as
        unsigned integers. The resulting integer is calculated as:

        ulin16 = int(value/(2^(-9)))

        Arguments:
            value -- float value to encode

        Returns:
            out {int} -- encoded ulin16 integer value
        """

        return round(value/(2**self.exponent))                

    def send_byte(self, command):
        self.set_control_signal()

        self.i2c_slave.write([command], relax=True, start=True)

        self.clear_control_signal()
        return None

    def write_byte(self, command, data: int):
        self.set_control_signal()

        #byte_data = data.to_bytes(1)
        self.i2c_slave.write([command, data], relax=True, start=True)

        self.clear_control_signal()

        return None

    def write_word(self, command, data: int):
        self.set_control_signal()

        byte_data = self.uint2bytes(data, 2)

        self.i2c_slave.write([command], relax=False, start=True)
        self.i2c_slave.write(byte_data, relax=True, start=False)

        self.clear_control_signal()

        return None
    
    def read_word(self, command):
        self.set_control_signal()
        
        bytes_reads = []
        self.i2c_slave.write([command], relax=False, start=True)
        bytes_reads = self.i2c_slave.read(readlen=2, relax=True, start=True)
        
        self.clear_control_signal()

        return bytes_reads

    def set_control_signal(self):
        pins = self.gpio.read()
        pins &= self.gpio_master_mask
        pins |= self.gpio_ctrl_mask
        self.gpio.write(pins)

        return None

    def clear_control_signal(self):
        pins = self.gpio.read()
        pins &= self.gpio_master_mask
        pins &= ~self.gpio_ctrl_mask
        self.gpio.write(pins)

        return None
    
    def get_vout_mode (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.vout_mode)
        
        return self.twos_complement(bytes_reads[0], 5)
    
    def set_page (self, page: int):
        if (page >= 0) and (page < 4):
            self.write_byte(self.commands.page, page)
        return None

    def get_vout_max (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.vout_max)
        value = self.bytes2uint(bytes_reads)
        return self.decode_ulin16(value=value)

    def set_vout_max (self, data: float):
        encoded_value = self.encode_ulin16(data)
        self.write_word(self.commands.vout_max, encoded_value)
        return None

    def get_vout_command (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.vout_command)
        value = self.bytes2uint(bytes_reads)
        return self.decode_ulin16(value=value)

    def set_vout_command (self, data: float):
        encoded_value = self.encode_ulin16(data)
        self.write_word(self.commands.vout_command, encoded_value)
        return None
        
    def get_vout_cal_offset (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.vout_cal_offset)
        value = self.bytes2uint(bytes_reads)
        return self.decode_ulin16(value=value)
    
    def get_vout_margin_high (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.vout_margin_high)
        value = self.bytes2uint(bytes_reads)
        return self.decode_ulin16(value=value)

    def set_vout_margin_high (self, data: float):
        encoded_value = self.encode_ulin16(data)
        self.write_word(self.commands.vout_margin_high, encoded_value)
        return None
    
    def get_vout_margin_low (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.vout_margin_low)
        value = self.bytes2uint(bytes_reads)
        return self.decode_ulin16(value=value)

    def set_vout_margin_low (self, data: float):
        encoded_value = self.encode_ulin16(data)
        self.write_word(self.commands.vout_margin_low, encoded_value)
        return None
    
    def get_vout_ov_fault_limit (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.vout_ov_fault_limit)
        value = self.bytes2uint(bytes_reads)
        return self.decode_ulin16(value=value)

    def set_vout_ov_fault_limit (self, data: float):
        encoded_value = self.encode_ulin16(data)
        self.write_word(self.commands.vout_ov_fault_limit, encoded_value)
        return None
    
    def get_vout_uv_fault_limit (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.vout_uv_fault_limit)
        value = self.bytes2uint(bytes_reads)
        return self.decode_ulin16(value=value)

    def set_vout_uv_fault_limit (self, data: float):
        encoded_value = self.encode_ulin16(data)
        self.write_word(self.commands.vout_uv_fault_limit, encoded_value)
        return None

    def get_power_good_on (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.power_good_on)
        value = self.bytes2uint(bytes_reads)
        return self.decode_ulin16(value=value)
    
    def set_power_good_on (self, data: float):
        encoded_value = self.encode_ulin16(data)
        self.write_word(self.commands.power_good_on, encoded_value)
        return None
    
    def get_power_good_off (self):
        bytes_reads = []
        bytes_reads = self.read_word(self.commands.power_good_off)
        value = self.bytes2uint(bytes_reads)
        return self.decode_ulin16(value=value)

    def set_power_good_off (self, data: float):
        encoded_value = self.encode_ulin16(data)
        self.write_word(self.commands.power_good_off, encoded_value)
        return None

    def store_default_all (self):
        self.send_byte(self.commands.store_default_all)
        return None
                                       
    def close(self):
        self.i2c_slave.flush()
        self.i2c_master.close()


if __name__ == "__main__":
    u0 = UCD92xx(0x34)

    voltage = 3.3
    u0.set_page(3) # rail 4

    print ("====== Before setting ======")
    print(f"VOUT_MAX = {u0.get_vout_max()}")
    print(f"VOUT_COMMAND = {u0.get_vout_command()}")
    print(f"VOUT_CAL_OFFSET = {u0.get_vout_cal_offset()}")
    print(f"VOUT_MARGIN_HIGH = {u0.get_vout_margin_high()}")
    print(f"VOUT_MARGIN_LOW = {u0.get_vout_margin_low()}")
    print(f"VOUT_OV_FAULT_LIMIT = {u0.get_vout_ov_fault_limit()}")
    print(f"VOUT_UV_FAULT_LIMIT = {u0.get_vout_uv_fault_limit()}")
    print(f"POWER_GOOD_ON = {u0.get_power_good_on()}")
    print(f"POWER_GOOD_OFF = {u0.get_power_good_off()}")

    print ("====== Setting ======")
    u0.set_vout_max(voltage * 1.3)
    u0.set_vout_margin_high(voltage * 1.15)
    u0.set_vout_margin_low(voltage * 0.85)
    u0.set_vout_ov_fault_limit(voltage * 1.15)
    u0.set_vout_uv_fault_limit(voltage * 0.85)
    u0.set_power_good_on(voltage * 0.95)
    u0.set_power_good_off(voltage * 0.85)

    u0.set_vout_command(voltage)

    print ("====== After setting ======")
    print(f"VOUT_MAX = {u0.get_vout_max()}")
    print(f"VOUT_COMMAND = {u0.get_vout_command()}")
    print(f"VOUT_CAL_OFFSET = {u0.get_vout_cal_offset()}")
    print(f"VOUT_MARGIN_HIGH = {u0.get_vout_margin_high()}")
    print(f"VOUT_MARGIN_LOW = {u0.get_vout_margin_low()}")
    print(f"VOUT_OV_FAULT_LIMIT = {u0.get_vout_ov_fault_limit()}")
    print(f"VOUT_UV_FAULT_LIMIT = {u0.get_vout_uv_fault_limit()}")
    print(f"POWER_GOOD_ON = {u0.get_power_good_on()}")
    print(f"POWER_GOOD_OFF = {u0.get_power_good_off()}")

    accept = int(input("Please measure the voltage then press 1 to save: "))
    if accept == 1:
        u0.store_default_all()

    u0.close()