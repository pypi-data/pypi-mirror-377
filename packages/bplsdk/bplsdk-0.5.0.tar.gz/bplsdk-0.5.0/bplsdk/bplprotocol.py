import re
import struct
from enum import IntEnum
from typing import Union, Tuple, List, Optional
from cobs import cobs
from crcmod import crcmod
import logging

logger = logging.getLogger(__name__)


class PacketID(IntEnum):
    """
    Class containing BPL packet IDs.
    Look in The Serial Protocol Document for comprehensive details on packet ids.

    Packet IDs:

    """
    MODE = 0x01
    "1 byte - Describes the Mode of a device"
    VELOCITY = 0x02
    "1 float - Describes the velocity of a device. Radians/s for angular joints. mm/s for linear joints."
    POSITION = 0x03
    "1 float - Describes the position of a device. In radians or mm"
    CURRENT = 0x05
    "1 float - Describes the current drawn by a device in mA"
    RELATIVE_POSITION = 0x0E
    "1 float - When sent sets the relative position of actuator. The actuator will move from its current position the amount specified in the data."
    INDEXED_POSITION = 0x0D
    "1 float - On first receiving indexed position an offset is created between the indexed position demand received and the current position. New indexed positions packets then move the actuators relative to the initial indexed position. "
    REQUEST = 0x60
    "bytes - Request a packet ID. On receiving the command, the device will send the packet corresponding to the packet IDs in the data field."
    SERIAL_NUMBER = 0x61
    "1 float - The unique serial number of the device"
    MODEL_NUMBER = 0x62
    "1 float - The model number of the device"
    TEMPERATURE = 0x66
    "1 float - The internal temperature in Celsius"
    SOFTWARE_VERSION = 0x6C
    "3 bytes - The software version on the device"
    KM_END_POS = 0xA1
    "6 floats - Request the current end effector position. (X, Y, Z, Y, P, R) in mm and radians. Only for kinematic enabled arms."
    KM_END_VEL = 0xA2
    "6 floats - Demand the end effector velocity (XYZ, RZ, RY, RX) in mm/s and rads/s. Only for kinematic enabled arm. Rotation commands (RZ, RY, RX) is only available for 7 function arms."
    KM_END_VEL_LOCAL = 0xCB
    "6 floats - Demand the end effector velocity relative to the end effector. (XYZ, RZ, RY, RX) in mm/s and rads/s. Only fora kinematic enabled arm. Rotation commands (RZ, RY, RX) is only available for 7 function arms."
    KM_BOX_OBSTACLE_02 = 0xA5
    "6 floats - (X1, Y1, Z1, X2, Y2, Z2) mm. Box obstacle defined by 2 opposite corners of a rectangular prism. "
    KM_BOX_OBSTACLE_03 = 0xA6
    KM_BOX_OBSTACLE_04 = 0xA7
    KM_BOX_OBSTACLE_05 = 0xA8
    KM_CYLINDER_OBSTACLE_02 = 0xAB
    "7 floats - (X1, Y1, Z1, X2, Y2, Z2, R) mm. Cylinder obstacle defined by 2 opposite centers of a cylinder. R defining the radius of the cylinder"
    KM_CYLINDER_OBSTACLE_03 = 0xAC
    KM_CYLINDER_OBSTACLE_04 = 0xAD
    KM_CYLINDER_OBSTACLE_05 = 0xAE

    VOLTAGE = 0x90
    "1 float - The supply voltage in Volts"
    SAVE = 0x50
    "1 byte - Send this to save user configurable settings on a device"
    HEARTBEAT_FREQUENCY = 0x92
    "1 byte - set the frequency of a packet to be sent from a device."
    HEARTBEAT_SET = 0x91
    "10 bytes - Specify the Packet IDs to be sent via heartbeat."
    POSITION_LIMITS = 0x10
    "2 floats - Maximum and Minimum positions of the device"
    VELOCITY_LIMITS = 0x11
    "2 floats - Maximum and Minimum velocities of the device"
    CURRENT_LIMITS = 0x12
    "2 floats - Maximum and Minimum currents of the device"
    HARDWARE_STATUS_FLAGS = 0x68
    "A 32-bit list corresponding to flags that can be set due to any hardware errors."

    ATI_FT_READING = 0xD8
    "6 floats - Read force in N and Torque in Nm from the Force torque sensor. (FX, FY, FZ, TX, TY, TZ). Send this packet to the FT Sensor to Tare it"
    BOOTLOADER = 0xFF


class BPLProtocol:
    """Class used to encode and decode BPL packets."""
    CRC8_FUNC = crcmod.mkCrcFun(0x14D, initCrc=0xFF, xorOut=0xFF)

    @staticmethod
    def packet_splitter(buff: bytes) -> Tuple[List[bytes], Optional[bytes]]:
        """
        Split packets coming in along bpl protocol, Packets are split at b'0x00'.

        :param buff: input buffer of bytes
        :return: List of bytes separated by 0x00, and a remaining bytes of an incomplete packet.
        """
        incomplete_packet = None
        packets = re.split(b'\x00', buff)
        if buff[-1] != b'0x00':
            incomplete_packet = packets.pop()
        return packets, incomplete_packet

    @staticmethod
    def parse_packet(packet_in: Union[bytes, bytearray]) -> Tuple[int, int, bytes]:
        """
        Parse the packet returning a tuple of [int, int, bytes].
        If unable to parse the packet, then return 0,0,b''.
        :param packet_in: bytes of a full packet
        :return: device_id, packet_id, data in bytes.
        """

        packet_in = bytearray(packet_in)

        if packet_in and len(packet_in) > 3:
            try:
                decoded_packet: bytes = cobs.decode(packet_in)
            except cobs.DecodeError as e:
                logger.warning(f"parse_packet(): Cobs Decoding Error, {e}")
                return 0, 0, b''

            if decoded_packet[-2] != len(decoded_packet):
                logger.warning(f"parse_packet(): Incorrect length: length is {len(decoded_packet)} "
                               f"in {[hex(x) for x in list(decoded_packet)]}")
                return 0, 0, b''
            else:
                if BPLProtocol.CRC8_FUNC(decoded_packet[:-1]) == decoded_packet[-1]:
                    rx_data = decoded_packet[:-4]

                    device_id = decoded_packet[-3]
                    packet_id = decoded_packet[-4]
                    rx_data = rx_data
                    return device_id, packet_id, rx_data
                else:
                    logger.warning(f"parse_packet(): CRC error in {[hex(x) for x in list(decoded_packet)]} ")
                    return 0, 0, b''
        return 0, 0, b''

    @staticmethod
    def encode_packet(device_id: int, packet_id: int, data: Union[bytes, bytearray]):
        """
         Encode the packet using the bpl protocol.

        :param device_id: Device ID
        :param packet_id: Packet ID
        :param data: Data in bytes
        :return: bytes of the encoded packet.
        """
        tx_packet = bytes(data)
        tx_packet += bytes([packet_id, device_id, len(tx_packet)+4])
        tx_packet += bytes([BPLProtocol.CRC8_FUNC(tx_packet)])
        packet: bytes = cobs.encode(tx_packet) + b'\x00'
        return packet

    @staticmethod
    def decode_floats(data: Union[bytes, bytearray]) -> List[float]:
        """
        Decode a received byte list, into a float list as specified by the bpl protocol

        Bytes are decoded into 32 bit floats.

        :param data: bytes, but be divisible by 4.
        :return: decoded list of floats
        """
        list_data = list(struct.unpack(str(int(len(data)/4)) + "f", data))
        return list_data

    @staticmethod
    def encode_floats(float_list: List[float]) -> bytes:
        """ Encode a list of floats into bytes

        Floats are encoded into 32 bits (4 bytes)

        :param float_list: list of floats
        :return: encoded bytes
        """
        data = struct.pack('%sf' % len(float_list), *float_list)
        return data


class PacketReader:
    """
    Packet Reader
    Helper class to read and decode incoming bytes and account for the incomplete packets.



    """
    incomplete_packets = b''

    def receive_bytes(self, data: bytes) -> List[Tuple[int, int, bytes]]:
        """
        Decodes packets.
        Accounts for reading incomplete bytes.

        :param data: input bytes
        :return: a list of of decoded packets (Device ID, Packet ID, data (in bytes))
        """
        # Receive data, and return a decoded packet
        packet_list = []
        encoded_packets, self.incomplete_packets = BPLProtocol.packet_splitter(self.incomplete_packets + data)
        if encoded_packets:
            for encoded_packet in encoded_packets:
                if not encoded_packet:
                    continue
                decoded_packet = BPLProtocol.parse_packet(encoded_packet)
                packet_list.append(decoded_packet)
        return packet_list
