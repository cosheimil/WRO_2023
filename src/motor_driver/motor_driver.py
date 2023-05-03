import smbus
import struct
import time

class MotorDriver:
    def __init__(self):
        self.bus = smbus.SMBus(0)
        self.address = 8

    def read_unpack(self, size, format):
        """Read all data from AStar

        Args:
            size (int): read bytes sended
            format (str): in what format

        Returns:
            struct: ?
        """
        self.bus.write_byte(20, self.address)
        time.sleep(0.0001)
        byte_list = [self.bus.read_byte(20) for _ in range(size)]
        return struct.unpack(format, bytes(byte_list))

    def write_pack(self, format, *data):
        """Write package to AStar

        Args:
            format (list[bytes]): Information: we wanna read
        """
        data_array = list(struct.pack(format, *data))
        self.bus.write_i2c_block_data(20, self.address, data_array)
        time.sleep(0.0001)

    def leds(self, red, yellow, green):
        """Control Leds from AStar

        Args:
            red (bool): red channel
            yellow (bool): yellow channel
            green (bool): green channel
        """
        self.write_pack(0, 'BBB', red, yellow, green)

    def play_notes(self, notes):
        """Play on buzzer

        Args:
            notes (ascii): melody
        """
        self.write_pack(24, 'B14s', 1, notes.encode("ascii"))

    def motors(self, left, right):
        """Control 2 motors by velocity

        Args:
            left (int): [-255, 255]
            right (int): [-255, 255]
        """
        self.write_pack(6, 'hh', left, right)

    def read_buttons(self):
        """Read 3 buttons states

        Returns:
            (bool, bool, bool): 3 Buttons on plate
        """
        return self.read_unpack(3, 3, "???")

    def read_battery_millivolts(self):
        """Read battery millivolts

        Returns:
            float: millivolts of battery
        """
        return self.read_unpack(10, 2, "H")

    def read_analog(self):
        """Read analog

        Returns:
            ?: ?
        """
        return self.read_unpack(12, 12, "HHHHHH")

    def read_encoders(self):
        """Read encoders connected to plat

        Returns:
            (float): encoders
        """
        return self.read_unpack(39, 4, 'hh')

    def test_read8(self):
        self.read_unpack(0, 8, 'cccccccc') 

    def test_write8(self):
        self.bus.write_i2c_block_data(20, 0, [0,0,0,0,0,0,0,0])
        time.sleep(0.0001)
