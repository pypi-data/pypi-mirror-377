import struct
import time
from enum import IntEnum, IntFlag

import serial

from .bplprotocol import BPLProtocol, PacketID, PacketReader


class DeviceID(IntEnum):
    JAWS = 0x01
    ROTATE = 0x02
    BEND_ELBOW = 0x03
    BEND_SHOULDER = 0x04
    ROTATE_BASE = 0x05
    ALL = 0xFF


class DeviceMode(IntEnum):
    STANDBY = 0x00
    DISABLE = 0x01
    POSITION = 0x02
    VELOCITY = 0x03
    CURRENT = 0x04


class HardwareStatusFlags(IntFlag):
    """
    Class containing the relevant hardware status flags

    The manipulator reports the status flags as 4 bytes where the first two are
    relevant, the third is unused, and the fourth is only relevant to the Bravo
    manipulators. The first two bytes are combined into one IntFlag for ease of use.
    """

    FLASH_FAILED_READ = 0x80 << 8
    "Failed to read from flash"
    HARDWARE_OVER_HUMIDITY = 0x40 << 8
    "The humidity levels detected are over acceptable factory humidity levels"
    HARDWARE_OVER_TEMPERATURE = 0x20 << 8
    "Joint temperature is over acceptable temperature levels"
    COMMS_SERIAL_ERROR = 0x10 << 8
    "Serial communication errors detected. This may be due to noise, or half duplex communication (collisions"
    COMMS_CRC_ERROR = 0x08 << 8
    "Communication decoding errors detected. This may be due to noise, or half duplex communication collisions"
    MOTOR_DRIVER_FAULT = 0x04 << 8
    "The motor driver is drawing too much current, or the voltage supply is too low"
    ENCODER_POSITION_ERROR = 0x02 << 8
    "Errors found in the joints position encoder. Absolute position may be incorrect"
    ENCODER_NOT_DETECTED = 0x01 << 8
    "Joints position encoder is not detected"
    DEVICE_AXIS_CONFLICT = 0x80
    "Detected an incorrect setup in a devices kinematic chain. Device ids must be in the correct order."
    MOTOR_NOT_CONNECTED = 0x40
    "Detected that the motor is not connected."
    MOTOR_OVER_CURRENT = 0x20
    "The motor is drawing too much current."
    INNER_ENCODER_POSITION_ERROR = 0x10
    "Errors found in the inner encoder. Commutation of the Joint may be affected."
    DEVICE_ID_CONFLICT = 0x08
    "Detected multiple devices with the same device id."
    HARDWARE_OVER_PRESSURE = 0x04
    "Pressure levels detected are over the factory levels."
    MOTOR_DRIVER_OVER_CURRENT_AND_UNDER_VOLTAGE = 0x02
    "Motor driver is drawing too much current, or the voltage supply is too low"
    MOTOR_DRIVER_OVER_TEMPERATURE = 0x01
    "The motor driver temperature is too high."


class ManipulatorError(Exception):
    """Base class for exceptions related to the manipulator"""


class PacketRequestTimeoutError(ManipulatorError):
    """Exception raised if there's no response from the manipulator"""


class SerialWrapper:
    def __init__(self, com_port: str):
        self._serial_port = serial.Serial(
            com_port,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.001,
        )
        self._packet_reader = PacketReader()

    def request_packet_and_wait_for_reply(
        self, device: DeviceID, packet_id: PacketID, timeout_s: float = 0.5
    ) -> bytes:
        packet = BPLProtocol.encode_packet(device, PacketID.REQUEST, bytes([packet_id]))
        self._serial_port.write(packet)

        start_time = time.time()
        while time.time() - start_time < timeout_s:
            try:
                read_data = self._serial_port.read()
            except serial.SerialException:
                # If there are no bytes to read we wait for a bit before retrying
                time.sleep(0.01)
                continue
            if read_data:
                for packet in self._packet_reader.receive_bytes(read_data):
                    read_device_id, read_packet_id, data_bytes = packet
                    if read_device_id == device and read_packet_id == packet_id:
                        return data_bytes
        else:
            raise PacketRequestTimeoutError(
                "Request for packet "
                f"{packet_id.name if isinstance(packet_id, PacketID) else packet_id} "
                f"from device {device.name if isinstance(device, DeviceID) else device}"
                " timed out"
            )

    def send_packet(self, device: DeviceID, packet: PacketID, data: bytes):
        packet = BPLProtocol.encode_packet(device, packet, data)
        self._serial_port.write(packet)

    def __del__(self):
        self._serial_port.close()


class Manipulator:
    def __init__(self):
        self._serial_com: SerialWrapper = None

    def connect(self, com_port: str):
        self._serial_com = SerialWrapper(com_port)

    def enable_all(self):
        """Set the operating mode of all devices to STANDBY

        When in Standby, receiving a control command will automatically change the mode
        of operation.
        """
        self._serial_com.send_packet(
            DeviceID.ALL, PacketID.MODE, bytes(DeviceMode.STANDBY)
        )

    def set_velocity(self, device_id: DeviceID, velocity: float):
        """Set the velocity setpoint of the actuator

        When used with a rotational device it is an angular velocity in radians per
        second and when it is a linear device it is in mm per second. Demanding a
        velocity setpoint above the maximum limit will set the velocity to maximum.
        """
        velocity_encoded = BPLProtocol.encode_floats([velocity])
        self._serial_com.send_packet(device_id, PacketID.VELOCITY, velocity_encoded)

    def get_velocity(self, device_id: DeviceID) -> float:
        """Get the instantaneous velocity of the device

        When used with a rotational device it is an angular velocity in radians per
        second and when it is a linear device it is in mm per second.
        """
        velocity_bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.VELOCITY
        )
        return BPLProtocol.decode_floats(velocity_bytes)[0]

    def set_absolute_position(self, device_id: DeviceID, position: float):
        """Sets the absolute position setpoint of the actuator

        When used with a rotational device it is an angle between zero and 2PI and when
        it is a linear device it is a distance in mm. If the position setpoint is
        outside of the limits the command is ignored.
        """
        position_encoded = BPLProtocol.encode_floats([position])
        self._serial_com.send_packet(device_id, PacketID.POSITION, position_encoded)

    def get_absolute_position(self, device_id: DeviceID) -> float:
        """Get the instantaneous position of the device

        When used with a rotational device it is an angle between zero and 2PI and when
        it is a linear device it is a distance in mm.
        """
        position_bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.POSITION
        )
        return BPLProtocol.decode_floats(position_bytes)[0]

    def set_relative_position(self, device_id: DeviceID, amount_to_move: float):
        """Set the relative position of the actuator

        Will move the specified distance/angle from its current position.
        """
        amount_encoded = BPLProtocol.encode_floats([amount_to_move])
        self._serial_com.send_packet(
            device_id, PacketID.RELATIVE_POSITION, amount_encoded
        )

    def get_relative_position(self, device_id: DeviceID) -> float:
        """Get the amount moved since the last time this function was called"""
        amount_bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.RELATIVE_POSITION
        )
        return BPLProtocol.decode_floats(amount_bytes)[0]

    def set_current_setpoint(self, device_id: DeviceID, current_setpoint: float):
        """Set the current setpoint of the motor windings in mA

        Demanding current that is out of range will set the current to maximum.
        """
        current_setpoint_encoded = BPLProtocol.encode_floats([current_setpoint])
        self._serial_com.send_packet(
            device_id, PacketID.CURRENT, current_setpoint_encoded
        )

    def get_current_draw(self, device_id: DeviceID) -> float:
        """Gets the instantaneous current of the device (in mA)"""
        current_bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.CURRENT
        )
        return BPLProtocol.decode_floats(current_bytes)[0]

    def get_internal_temperature(self, device_id: DeviceID) -> float:
        """Gets the internal tempearture of the device in degrees Celsius"""
        temperature_bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.TEMPERATURE
        )
        return BPLProtocol.decode_floats(temperature_bytes)[0]

    def get_supply_voltage(self, device_id: DeviceID) -> float:
        """Get the supply voltage of the device in Volts"""
        voltage: bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.VOLTAGE
        )
        return BPLProtocol.decode_floats(voltage)[0]

    def get_unique_serial_number(self, device_id: DeviceID) -> float:
        """Get the unique 4 digit serial number of the device"""
        serial_number: bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.SERIAL_NUMBER
        )
        return BPLProtocol.decode_floats(serial_number)[0]

    def get_model_number(self, device_id: DeviceID) -> float:
        """Get the 4 digit model number of the device"""
        model_number: bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.MODEL_NUMBER
        )
        return BPLProtocol.decode_floats(model_number)[0]

    def get_software_version(self, device_id: DeviceID) -> str:
        """Get the software version of the current firmware loaded on the device

        Stored in 3 bytes for major, sub-major, and minor on the device, returned as a
        string where each field is separated by a . from this function, eg. '1.2.3'
        """
        sw_version_bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.SOFTWARE_VERSION
        )
        sw_version: list = list(sw_version_bytes)
        return f"{sw_version[0]}.{sw_version[1]}.{sw_version[2]}"

    def check_for_enabled_hardware_status_flags(
        self, device_id: DeviceID
    ) -> list[HardwareStatusFlags]:
        """Check if any of the hardware error flags are set

        Returns a list of HardStatusFlags that are set.
        """
        hardware_status_bytes = self._serial_com.request_packet_and_wait_for_reply(
            device_id, PacketID.HARDWARE_STATUS_FLAGS
        )
        # Discarding the last two bytes since they are unused or only related to the
        # bravo manipulators
        status_flags = struct.unpack(">H", hardware_status_bytes[:2])[0]

        return [flag for flag in HardwareStatusFlags if flag & status_flags]
