from dataclasses import dataclass
from enum import IntEnum, IntFlag

from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage, ReplyHarpMessage
from harp.serial import Device

@dataclass
class FlowmeterPayload:
    Channel0: int
    Channel1: int
    Channel2: int
    Channel3: int
    Channel4: int

@dataclass
class ChannelsTargetFlowPayload:
    Channel0: float
    Channel1: float
    Channel2: float
    Channel3: float
    Channel4: float


class DigitalOutputs(IntFlag):
    """
    Specifies the states of the digital outputs.

    Attributes
    ----------
    DO0 : int
        _No description currently available_
    DO1 : int
        _No description currently available_
    """

    NONE = 0x0
    DO0 = 0x1
    DO1 = 0x2


class Valves(IntFlag):
    """
    Specifies the states of the valves.

    Attributes
    ----------
    VALVE0 : int
        _No description currently available_
    VALVE1 : int
        _No description currently available_
    VALVE2 : int
        _No description currently available_
    VALVE3 : int
        _No description currently available_
    END_VALVE0 : int
        _No description currently available_
    END_VALVE1 : int
        _No description currently available_
    VALVE_DUMMY : int
        _No description currently available_
    """

    NONE = 0x0
    VALVE0 = 0x1
    VALVE1 = 0x2
    VALVE2 = 0x4
    VALVE3 = 0x8
    END_VALVE0 = 0x10
    END_VALVE1 = 0x20
    VALVE_DUMMY = 0x40


class OdorValves(IntFlag):
    """
    Specifies the states of the odor valves.

    Attributes
    ----------
    VALVE0 : int
        _No description currently available_
    VALVE1 : int
        _No description currently available_
    VALVE2 : int
        _No description currently available_
    VALVE3 : int
        _No description currently available_
    """

    NONE = 0x0
    VALVE0 = 0x1
    VALVE1 = 0x2
    VALVE2 = 0x4
    VALVE3 = 0x8


class EndValves(IntFlag):
    """
    Specifies the states of the end valves.

    Attributes
    ----------
    END_VALVE0 : int
        _No description currently available_
    END_VALVE1 : int
        _No description currently available_
    VALVE_DUMMY : int
        _No description currently available_
    """

    NONE = 0x0
    END_VALVE0 = 0x10
    END_VALVE1 = 0x20
    VALVE_DUMMY = 0x40


class OlfactometerEvents(IntFlag):
    """
    The events that can be enabled/disabled.

    Attributes
    ----------
    FLOWMETER : int
        _No description currently available_
    DI0_TRIGGER : int
        _No description currently available_
    CHANNEL_ACTUAL_FLOW : int
        _No description currently available_
    """

    NONE = 0x0
    FLOWMETER = 0x1
    DI0_TRIGGER = 0x2
    CHANNEL_ACTUAL_FLOW = 0x4


class DigitalState(IntEnum):
    """
    The state of a digital pin.

    Attributes
    ----------
    LOW : int
        _No description currently available_
    HIGH : int
        _No description currently available_
    """

    LOW = 0
    HIGH = 1


class DO0SyncConfig(IntEnum):
    """
    Available configurations when using DO0 pin to report firmware events.

    Attributes
    ----------
    NONE : int
        _No description currently available_
    MIMIC_ENABLE_FLOW : int
        _No description currently available_
    """

    NONE = 0
    MIMIC_ENABLE_FLOW = 1


class DO1SyncConfig(IntEnum):
    """
    Available configurations when using DO1 pin to report firmware events.

    Attributes
    ----------
    NONE : int
        _No description currently available_
    MIMIC_ENABLE_FLOW : int
        _No description currently available_
    """

    NONE = 0
    MIMIC_ENABLE_FLOW = 1


class DI0TriggerConfig(IntEnum):
    """
    Specifies the configuration of the digital input 0 (DIN0).

    Attributes
    ----------
    SYNC : int
        _No description currently available_
    ENABLE_FLOW_WHILE_HIGH : int
        _No description currently available_
    VALVE_TOGGLE : int
        _No description currently available_
    """

    SYNC = 0
    ENABLE_FLOW_WHILE_HIGH = 1
    VALVE_TOGGLE = 2


class MimicOutputs(IntEnum):
    """
    Specifies the target IO on which to mimic the specified register.

    Attributes
    ----------
    NONE : int
        _No description currently available_
    DO0 : int
        _No description currently available_
    DO1 : int
        _No description currently available_
    """

    NONE = 0
    DO0 = 1
    DO1 = 2


class Channel3RangeConfig(IntEnum):
    """
    Available flow ranges for channel 3 (ml/min).

    Attributes
    ----------
    FLOW_RATE100 : int
        _No description currently available_
    FLOW_RATE1000 : int
        _No description currently available_
    """

    FLOW_RATE100 = 0
    FLOW_RATE1000 = 1


class OlfactometerRegisters(IntEnum):
    """Enum for all available registers in the Olfactometer device.

    Attributes
    ----------
    ENABLE_FLOW : int
        Starts or stops the flow in all channels.
    FLOWMETER : int
        Value of single ADC read from all flowmeter channels.
    DI0_STATE : int
        State of the digital input pin 0.
    CHANNEL0_USER_CALIBRATION : int
        Calibration values for a single channel [x0,...xn], where x= ADC raw value for 0:10:100 ml/min.
    CHANNEL1_USER_CALIBRATION : int
        Calibration values for a single channel [x0,...xn], where x= ADC raw value for 0:10:100 ml/min.
    CHANNEL2_USER_CALIBRATION : int
        Calibration values for a single channel [x0,...xn], where x= ADC raw value for 0:10:100 ml/min.
    CHANNEL3_USER_CALIBRATION : int
        Calibration values for a single channel [x0,...xn], where x= ADC raw value for 0:10:100 ml/min.
    CHANNEL4_USER_CALIBRATION : int
        Calibration values specific for channel 4 [x0,...xn], where x= ADC raw value for 0:100:1000 ml/min.
    CHANNEL3_USER_CALIBRATION_AUX : int
        Calibration values specific for channel 3 if Channel3RangeConfig = FlowRate1000. [x0,...xn], where x= ADC raw value for 0:100:1000 ml/min.
    USER_CALIBRATION_ENABLE : int
        Override the factory calibration values, replacing with CHX_USER_CALIBRATION.
    CHANNEL0_TARGET_FLOW : int
        Sets the flow-rate rate for channel 0 [ml/min].
    CHANNEL1_TARGET_FLOW : int
        Sets the flow-rate rate for channel 1 [ml/min].
    CHANNEL2_TARGET_FLOW : int
        Sets the flow-rate rate for channel 2 [ml/min].
    CHANNEL3_TARGET_FLOW : int
        Sets the flow-rate rate for channel 3 [ml/min].
    CHANNEL4_TARGET_FLOW : int
        Sets the flow-rate rate for channel 4 [ml/min].
    CHANNELS_TARGET_FLOW : int
        Sets the flow-rate rate for all channels [ml/min].
    CHANNEL0_ACTUAL_FLOW : int
        Actual flow-rate read for channel 0 - flowmeter 0 [ml/min].
    CHANNEL1_ACTUAL_FLOW : int
        Actual flow-rate read for channel 1 - flowmeter 1 [ml/min].
    CHANNEL2_ACTUAL_FLOW : int
        Actual flow-rate read for channel 2 - flowmeter 2 [ml/min].
    CHANNEL3_ACTUAL_FLOW : int
        Actual flow-rate read for channel 3 - flowmeter 3 [ml/min].
    CHANNEL4_ACTUAL_FLOW : int
        Actual flow-rate read for channel 4 - flowmeter 4 [ml/min].
    CHANNEL0_DUTY_CYCLE : int
        Duty cycle for proportional valve 0 [%].
    CHANNEL1_DUTY_CYCLE : int
        Duty cycle for proportional valve 1 [%].
    CHANNEL2_DUTY_CYCLE : int
        Duty cycle for proportional valve 2 [%].
    CHANNEL3_DUTY_CYCLE : int
        Duty cycle for proportional valve 3 [%].
    CHANNEL4_DUTY_CYCLE : int
        Duty cycle for proportional valve 4 [%].
    DIGITAL_OUTPUT_SET : int
        Set the specified digital output lines.
    DIGITAL_OUTPUT_CLEAR : int
        Clears the specified digital output lines.
    DIGITAL_OUTPUT_TOGGLE : int
        Toggles the specified digital output lines.
    DIGITAL_OUTPUT_STATE : int
        Write the state of all digital output lines.
    ENABLE_VALVE_PULSE : int
        Enable pulse mode for valves.
    VALVE_SET : int
        Set the specified valve output lines.
    VALVE_CLEAR : int
        Clears the specified valve output lines.
    VALVE_TOGGLE : int
        Toggles the specified valve output lines.
    ODOR_VALVE_STATE : int
        Write the state of all odor valve output lines.
    END_VALVE_STATE : int
        Write the state of all end valve output lines.
    VALVE0_PULSE_DURATION : int
        Sets the pulse duration for Valve0.
    VALVE1_PULSE_DURATION : int
        Sets the pulse duration for Valve1.
    VALVE2_PULSE_DURATION : int
        Sets the pulse duration for Valve2.
    VALVE3_PULSE_DURATION : int
        Sets the pulse duration for Valve3.
    END_VALVE0_PULSE_DURATION : int
        Sets the pulse duration for EndValve0.
    END_VALVE1_PULSE_DURATION : int
        Sets the pulse duration for EndValve1.
    DO0_SYNC : int
        Configuration of the digital output 0 (DOUT0).
    DO1_SYNC : int
        Configuration of the digital output 1 (DOUT1).
    DI0_TRIGGER : int
        Configuration of the digital input pin 0 (DIN0).
    MIMIC_VALVE0 : int
        Mimic Valve0.
    MIMIC_VALVE1 : int
        Mimic Valve1.
    MIMIC_VALVE2 : int
        Mimic Valve2.
    MIMIC_VALVE3 : int
        Mimic Valve3.
    MIMIC_END_VALVE0 : int
        Mimic EndValve0.
    MIMIC_END_VALVE1 : int
        Mimic EndValve1.
    ENABLE_VALVE_EXTERNAL_CONTROL : int
        Enable the valves control via low-level IO screw terminals.
    CHANNEL3_RANGE : int
        Selects the flow range for the channel 3.
    TEMPERATURE_VALUE : int
        Temperature sensor reading value.
    ENABLE_TEMPERATURE_CALIBRATION : int
        Enable flow adjustment based on the temperature calibration.
    TEMPERATURE_CALIBRATION_VALUE : int
        Temperature value measured during the device calibration.
    ENABLE_EVENTS : int
        Specifies the active events in the device.
    """

    ENABLE_FLOW = 32
    FLOWMETER = 33
    DI0_STATE = 34
    CHANNEL0_USER_CALIBRATION = 35
    CHANNEL1_USER_CALIBRATION = 36
    CHANNEL2_USER_CALIBRATION = 37
    CHANNEL3_USER_CALIBRATION = 38
    CHANNEL4_USER_CALIBRATION = 39
    CHANNEL3_USER_CALIBRATION_AUX = 40
    USER_CALIBRATION_ENABLE = 41
    CHANNEL0_TARGET_FLOW = 42
    CHANNEL1_TARGET_FLOW = 43
    CHANNEL2_TARGET_FLOW = 44
    CHANNEL3_TARGET_FLOW = 45
    CHANNEL4_TARGET_FLOW = 46
    CHANNELS_TARGET_FLOW = 47
    CHANNEL0_ACTUAL_FLOW = 48
    CHANNEL1_ACTUAL_FLOW = 49
    CHANNEL2_ACTUAL_FLOW = 50
    CHANNEL3_ACTUAL_FLOW = 51
    CHANNEL4_ACTUAL_FLOW = 52
    CHANNEL0_DUTY_CYCLE = 58
    CHANNEL1_DUTY_CYCLE = 59
    CHANNEL2_DUTY_CYCLE = 60
    CHANNEL3_DUTY_CYCLE = 61
    CHANNEL4_DUTY_CYCLE = 62
    DIGITAL_OUTPUT_SET = 63
    DIGITAL_OUTPUT_CLEAR = 64
    DIGITAL_OUTPUT_TOGGLE = 65
    DIGITAL_OUTPUT_STATE = 66
    ENABLE_VALVE_PULSE = 67
    VALVE_SET = 68
    VALVE_CLEAR = 69
    VALVE_TOGGLE = 70
    ODOR_VALVE_STATE = 71
    END_VALVE_STATE = 72
    VALVE0_PULSE_DURATION = 73
    VALVE1_PULSE_DURATION = 74
    VALVE2_PULSE_DURATION = 75
    VALVE3_PULSE_DURATION = 76
    END_VALVE0_PULSE_DURATION = 77
    END_VALVE1_PULSE_DURATION = 78
    DO0_SYNC = 80
    DO1_SYNC = 81
    DI0_TRIGGER = 82
    MIMIC_VALVE0 = 83
    MIMIC_VALVE1 = 84
    MIMIC_VALVE2 = 85
    MIMIC_VALVE3 = 86
    MIMIC_END_VALVE0 = 87
    MIMIC_END_VALVE1 = 88
    ENABLE_VALVE_EXTERNAL_CONTROL = 90
    CHANNEL3_RANGE = 91
    TEMPERATURE_VALUE = 92
    ENABLE_TEMPERATURE_CALIBRATION = 93
    TEMPERATURE_CALIBRATION_VALUE = 94
    ENABLE_EVENTS = 95


class Olfactometer(Device):
    """
    Olfactometer class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1140:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1140}, got {self.WHO_AM_I}")

    def read_enable_flow(self) -> bool:
        """
        Reads the contents of the EnableFlow register.

        Returns
        -------
        bool
            Value read from the EnableFlow register.
        """
        address = OlfactometerRegisters.ENABLE_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("EnableFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_enable_flow(self, value: bool) -> ReplyHarpMessage | None:
        """
        Writes a value to the EnableFlow register.

        Parameters
        ----------
        value : bool
            Value to write to the EnableFlow register.
        """
        address = OlfactometerRegisters.ENABLE_FLOW
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EnableFlow")

        return reply

    def read_flowmeter(self) -> FlowmeterPayload:
        """
        Reads the contents of the Flowmeter register.

        Returns
        -------
        FlowmeterPayload
            Value read from the Flowmeter register.
        """
        address = OlfactometerRegisters.FLOWMETER
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Flowmeter")

        # Map payload (list/array) to dataclass fields by offset
        payload = reply.payload
        return FlowmeterPayload(
            Channel0=payload[0],
            Channel1=payload[1],
            Channel2=payload[2],
            Channel3=payload[3],
            Channel4=payload[4]
        )

    def read_di0_state(self) -> DigitalState:
        """
        Reads the contents of the DI0State register.

        Returns
        -------
        DigitalState
            Value read from the DI0State register.
        """
        address = OlfactometerRegisters.DI0_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DI0State")

        return DigitalState(reply.payload)

    def read_channel0_user_calibration(self) -> list[int]:
        """
        Reads the contents of the Channel0UserCalibration register.

        Returns
        -------
        list[int]
            Value read from the Channel0UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL0_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel0UserCalibration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel0_user_calibration(self, value: list[int]) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel0UserCalibration register.

        Parameters
        ----------
        value : list[int]
            Value to write to the Channel0UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL0_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel0UserCalibration")

        return reply

    def read_channel1_user_calibration(self) -> list[int]:
        """
        Reads the contents of the Channel1UserCalibration register.

        Returns
        -------
        list[int]
            Value read from the Channel1UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL1_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel1UserCalibration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel1_user_calibration(self, value: list[int]) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel1UserCalibration register.

        Parameters
        ----------
        value : list[int]
            Value to write to the Channel1UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL1_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel1UserCalibration")

        return reply

    def read_channel2_user_calibration(self) -> list[int]:
        """
        Reads the contents of the Channel2UserCalibration register.

        Returns
        -------
        list[int]
            Value read from the Channel2UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL2_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel2UserCalibration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel2_user_calibration(self, value: list[int]) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel2UserCalibration register.

        Parameters
        ----------
        value : list[int]
            Value to write to the Channel2UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL2_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel2UserCalibration")

        return reply

    def read_channel3_user_calibration(self) -> list[int]:
        """
        Reads the contents of the Channel3UserCalibration register.

        Returns
        -------
        list[int]
            Value read from the Channel3UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL3_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel3UserCalibration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel3_user_calibration(self, value: list[int]) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel3UserCalibration register.

        Parameters
        ----------
        value : list[int]
            Value to write to the Channel3UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL3_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel3UserCalibration")

        return reply

    def read_channel4_user_calibration(self) -> list[int]:
        """
        Reads the contents of the Channel4UserCalibration register.

        Returns
        -------
        list[int]
            Value read from the Channel4UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL4_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel4UserCalibration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel4_user_calibration(self, value: list[int]) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel4UserCalibration register.

        Parameters
        ----------
        value : list[int]
            Value to write to the Channel4UserCalibration register.
        """
        address = OlfactometerRegisters.CHANNEL4_USER_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel4UserCalibration")

        return reply

    def read_channel3_user_calibration_aux(self) -> list[int]:
        """
        Reads the contents of the Channel3UserCalibrationAux register.

        Returns
        -------
        list[int]
            Value read from the Channel3UserCalibrationAux register.
        """
        address = OlfactometerRegisters.CHANNEL3_USER_CALIBRATION_AUX
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel3UserCalibrationAux")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel3_user_calibration_aux(self, value: list[int]) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel3UserCalibrationAux register.

        Parameters
        ----------
        value : list[int]
            Value to write to the Channel3UserCalibrationAux register.
        """
        address = OlfactometerRegisters.CHANNEL3_USER_CALIBRATION_AUX
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel3UserCalibrationAux")

        return reply

    def read_user_calibration_enable(self) -> bool:
        """
        Reads the contents of the UserCalibrationEnable register.

        Returns
        -------
        bool
            Value read from the UserCalibrationEnable register.
        """
        address = OlfactometerRegisters.USER_CALIBRATION_ENABLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("UserCalibrationEnable")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_user_calibration_enable(self, value: bool) -> ReplyHarpMessage | None:
        """
        Writes a value to the UserCalibrationEnable register.

        Parameters
        ----------
        value : bool
            Value to write to the UserCalibrationEnable register.
        """
        address = OlfactometerRegisters.USER_CALIBRATION_ENABLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("UserCalibrationEnable")

        return reply

    def read_channel0_target_flow(self) -> float:
        """
        Reads the contents of the Channel0TargetFlow register.

        Returns
        -------
        float
            Value read from the Channel0TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL0_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel0TargetFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel0_target_flow(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel0TargetFlow register.

        Parameters
        ----------
        value : float
            Value to write to the Channel0TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL0_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel0TargetFlow")

        return reply

    def read_channel1_target_flow(self) -> float:
        """
        Reads the contents of the Channel1TargetFlow register.

        Returns
        -------
        float
            Value read from the Channel1TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL1_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel1TargetFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel1_target_flow(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel1TargetFlow register.

        Parameters
        ----------
        value : float
            Value to write to the Channel1TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL1_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel1TargetFlow")

        return reply

    def read_channel2_target_flow(self) -> float:
        """
        Reads the contents of the Channel2TargetFlow register.

        Returns
        -------
        float
            Value read from the Channel2TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL2_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel2TargetFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel2_target_flow(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel2TargetFlow register.

        Parameters
        ----------
        value : float
            Value to write to the Channel2TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL2_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel2TargetFlow")

        return reply

    def read_channel3_target_flow(self) -> float:
        """
        Reads the contents of the Channel3TargetFlow register.

        Returns
        -------
        float
            Value read from the Channel3TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL3_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel3TargetFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel3_target_flow(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel3TargetFlow register.

        Parameters
        ----------
        value : float
            Value to write to the Channel3TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL3_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel3TargetFlow")

        return reply

    def read_channel4_target_flow(self) -> float:
        """
        Reads the contents of the Channel4TargetFlow register.

        Returns
        -------
        float
            Value read from the Channel4TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL4_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel4TargetFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel4_target_flow(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel4TargetFlow register.

        Parameters
        ----------
        value : float
            Value to write to the Channel4TargetFlow register.
        """
        address = OlfactometerRegisters.CHANNEL4_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel4TargetFlow")

        return reply

    def read_channels_target_flow(self) -> ChannelsTargetFlowPayload:
        """
        Reads the contents of the ChannelsTargetFlow register.

        Returns
        -------
        ChannelsTargetFlowPayload
            Value read from the ChannelsTargetFlow register.
        """
        address = OlfactometerRegisters.CHANNELS_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("ChannelsTargetFlow")

        # Map payload (list/array) to dataclass fields by offset
        payload = reply.payload
        return ChannelsTargetFlowPayload(
            Channel0=payload[0],
            Channel1=payload[1],
            Channel2=payload[2],
            Channel3=payload[3],
            Channel4=payload[4]
        )

    def write_channels_target_flow(self, value: ChannelsTargetFlowPayload) -> ReplyHarpMessage | None:
        """
        Writes a value to the ChannelsTargetFlow register.

        Parameters
        ----------
        value : ChannelsTargetFlowPayload
            Value to write to the ChannelsTargetFlow register.
        """
        address = OlfactometerRegisters.CHANNELS_TARGET_FLOW
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("ChannelsTargetFlow")

        return reply

    def read_channel0_actual_flow(self) -> float:
        """
        Reads the contents of the Channel0ActualFlow register.

        Returns
        -------
        float
            Value read from the Channel0ActualFlow register.
        """
        address = OlfactometerRegisters.CHANNEL0_ACTUAL_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel0ActualFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def read_channel1_actual_flow(self) -> float:
        """
        Reads the contents of the Channel1ActualFlow register.

        Returns
        -------
        float
            Value read from the Channel1ActualFlow register.
        """
        address = OlfactometerRegisters.CHANNEL1_ACTUAL_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel1ActualFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def read_channel2_actual_flow(self) -> float:
        """
        Reads the contents of the Channel2ActualFlow register.

        Returns
        -------
        float
            Value read from the Channel2ActualFlow register.
        """
        address = OlfactometerRegisters.CHANNEL2_ACTUAL_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel2ActualFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def read_channel3_actual_flow(self) -> float:
        """
        Reads the contents of the Channel3ActualFlow register.

        Returns
        -------
        float
            Value read from the Channel3ActualFlow register.
        """
        address = OlfactometerRegisters.CHANNEL3_ACTUAL_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel3ActualFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def read_channel4_actual_flow(self) -> float:
        """
        Reads the contents of the Channel4ActualFlow register.

        Returns
        -------
        float
            Value read from the Channel4ActualFlow register.
        """
        address = OlfactometerRegisters.CHANNEL4_ACTUAL_FLOW
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel4ActualFlow")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def read_channel0_duty_cycle(self) -> float:
        """
        Reads the contents of the Channel0DutyCycle register.

        Returns
        -------
        float
            Value read from the Channel0DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL0_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel0DutyCycle")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel0_duty_cycle(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel0DutyCycle register.

        Parameters
        ----------
        value : float
            Value to write to the Channel0DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL0_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel0DutyCycle")

        return reply

    def read_channel1_duty_cycle(self) -> float:
        """
        Reads the contents of the Channel1DutyCycle register.

        Returns
        -------
        float
            Value read from the Channel1DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL1_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel1DutyCycle")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel1_duty_cycle(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel1DutyCycle register.

        Parameters
        ----------
        value : float
            Value to write to the Channel1DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL1_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel1DutyCycle")

        return reply

    def read_channel2_duty_cycle(self) -> float:
        """
        Reads the contents of the Channel2DutyCycle register.

        Returns
        -------
        float
            Value read from the Channel2DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL2_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel2DutyCycle")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel2_duty_cycle(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel2DutyCycle register.

        Parameters
        ----------
        value : float
            Value to write to the Channel2DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL2_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel2DutyCycle")

        return reply

    def read_channel3_duty_cycle(self) -> float:
        """
        Reads the contents of the Channel3DutyCycle register.

        Returns
        -------
        float
            Value read from the Channel3DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL3_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel3DutyCycle")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel3_duty_cycle(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel3DutyCycle register.

        Parameters
        ----------
        value : float
            Value to write to the Channel3DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL3_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel3DutyCycle")

        return reply

    def read_channel4_duty_cycle(self) -> float:
        """
        Reads the contents of the Channel4DutyCycle register.

        Returns
        -------
        float
            Value read from the Channel4DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL4_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel4DutyCycle")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_channel4_duty_cycle(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel4DutyCycle register.

        Parameters
        ----------
        value : float
            Value to write to the Channel4DutyCycle register.
        """
        address = OlfactometerRegisters.CHANNEL4_DUTY_CYCLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel4DutyCycle")

        return reply

    def read_digital_output_set(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputSet register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputSet register.
        """
        address = OlfactometerRegisters.DIGITAL_OUTPUT_SET
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DigitalOutputSet")

        return DigitalOutputs(reply.payload)

    def write_digital_output_set(self, value: DigitalOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the DigitalOutputSet register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the DigitalOutputSet register.
        """
        address = OlfactometerRegisters.DIGITAL_OUTPUT_SET
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DigitalOutputSet")

        return reply

    def read_digital_output_clear(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputClear register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputClear register.
        """
        address = OlfactometerRegisters.DIGITAL_OUTPUT_CLEAR
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DigitalOutputClear")

        return DigitalOutputs(reply.payload)

    def write_digital_output_clear(self, value: DigitalOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the DigitalOutputClear register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the DigitalOutputClear register.
        """
        address = OlfactometerRegisters.DIGITAL_OUTPUT_CLEAR
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DigitalOutputClear")

        return reply

    def read_digital_output_toggle(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputToggle register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputToggle register.
        """
        address = OlfactometerRegisters.DIGITAL_OUTPUT_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DigitalOutputToggle")

        return DigitalOutputs(reply.payload)

    def write_digital_output_toggle(self, value: DigitalOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the DigitalOutputToggle register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the DigitalOutputToggle register.
        """
        address = OlfactometerRegisters.DIGITAL_OUTPUT_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DigitalOutputToggle")

        return reply

    def read_digital_output_state(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputState register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputState register.
        """
        address = OlfactometerRegisters.DIGITAL_OUTPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DigitalOutputState")

        return DigitalOutputs(reply.payload)

    def write_digital_output_state(self, value: DigitalOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the DigitalOutputState register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the DigitalOutputState register.
        """
        address = OlfactometerRegisters.DIGITAL_OUTPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DigitalOutputState")

        return reply

    def read_enable_valve_pulse(self) -> Valves:
        """
        Reads the contents of the EnableValvePulse register.

        Returns
        -------
        Valves
            Value read from the EnableValvePulse register.
        """
        address = OlfactometerRegisters.ENABLE_VALVE_PULSE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("EnableValvePulse")

        return Valves(reply.payload)

    def write_enable_valve_pulse(self, value: Valves) -> ReplyHarpMessage | None:
        """
        Writes a value to the EnableValvePulse register.

        Parameters
        ----------
        value : Valves
            Value to write to the EnableValvePulse register.
        """
        address = OlfactometerRegisters.ENABLE_VALVE_PULSE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EnableValvePulse")

        return reply

    def read_valve_set(self) -> Valves:
        """
        Reads the contents of the ValveSet register.

        Returns
        -------
        Valves
            Value read from the ValveSet register.
        """
        address = OlfactometerRegisters.VALVE_SET
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("ValveSet")

        return Valves(reply.payload)

    def write_valve_set(self, value: Valves) -> ReplyHarpMessage | None:
        """
        Writes a value to the ValveSet register.

        Parameters
        ----------
        value : Valves
            Value to write to the ValveSet register.
        """
        address = OlfactometerRegisters.VALVE_SET
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("ValveSet")

        return reply

    def read_valve_clear(self) -> Valves:
        """
        Reads the contents of the ValveClear register.

        Returns
        -------
        Valves
            Value read from the ValveClear register.
        """
        address = OlfactometerRegisters.VALVE_CLEAR
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("ValveClear")

        return Valves(reply.payload)

    def write_valve_clear(self, value: Valves) -> ReplyHarpMessage | None:
        """
        Writes a value to the ValveClear register.

        Parameters
        ----------
        value : Valves
            Value to write to the ValveClear register.
        """
        address = OlfactometerRegisters.VALVE_CLEAR
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("ValveClear")

        return reply

    def read_valve_toggle(self) -> Valves:
        """
        Reads the contents of the ValveToggle register.

        Returns
        -------
        Valves
            Value read from the ValveToggle register.
        """
        address = OlfactometerRegisters.VALVE_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("ValveToggle")

        return Valves(reply.payload)

    def write_valve_toggle(self, value: Valves) -> ReplyHarpMessage | None:
        """
        Writes a value to the ValveToggle register.

        Parameters
        ----------
        value : Valves
            Value to write to the ValveToggle register.
        """
        address = OlfactometerRegisters.VALVE_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("ValveToggle")

        return reply

    def read_odor_valve_state(self) -> OdorValves:
        """
        Reads the contents of the OdorValveState register.

        Returns
        -------
        OdorValves
            Value read from the OdorValveState register.
        """
        address = OlfactometerRegisters.ODOR_VALVE_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("OdorValveState")

        return OdorValves(reply.payload)

    def write_odor_valve_state(self, value: OdorValves) -> ReplyHarpMessage | None:
        """
        Writes a value to the OdorValveState register.

        Parameters
        ----------
        value : OdorValves
            Value to write to the OdorValveState register.
        """
        address = OlfactometerRegisters.ODOR_VALVE_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OdorValveState")

        return reply

    def read_end_valve_state(self) -> EndValves:
        """
        Reads the contents of the EndValveState register.

        Returns
        -------
        EndValves
            Value read from the EndValveState register.
        """
        address = OlfactometerRegisters.END_VALVE_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("EndValveState")

        return EndValves(reply.payload)

    def write_end_valve_state(self, value: EndValves) -> ReplyHarpMessage | None:
        """
        Writes a value to the EndValveState register.

        Parameters
        ----------
        value : EndValves
            Value to write to the EndValveState register.
        """
        address = OlfactometerRegisters.END_VALVE_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EndValveState")

        return reply

    def read_valve0_pulse_duration(self) -> int:
        """
        Reads the contents of the Valve0PulseDuration register.

        Returns
        -------
        int
            Value read from the Valve0PulseDuration register.
        """
        address = OlfactometerRegisters.VALVE0_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Valve0PulseDuration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_valve0_pulse_duration(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the Valve0PulseDuration register.

        Parameters
        ----------
        value : int
            Value to write to the Valve0PulseDuration register.
        """
        address = OlfactometerRegisters.VALVE0_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Valve0PulseDuration")

        return reply

    def read_valve1_pulse_duration(self) -> int:
        """
        Reads the contents of the Valve1PulseDuration register.

        Returns
        -------
        int
            Value read from the Valve1PulseDuration register.
        """
        address = OlfactometerRegisters.VALVE1_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Valve1PulseDuration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_valve1_pulse_duration(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the Valve1PulseDuration register.

        Parameters
        ----------
        value : int
            Value to write to the Valve1PulseDuration register.
        """
        address = OlfactometerRegisters.VALVE1_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Valve1PulseDuration")

        return reply

    def read_valve2_pulse_duration(self) -> int:
        """
        Reads the contents of the Valve2PulseDuration register.

        Returns
        -------
        int
            Value read from the Valve2PulseDuration register.
        """
        address = OlfactometerRegisters.VALVE2_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Valve2PulseDuration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_valve2_pulse_duration(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the Valve2PulseDuration register.

        Parameters
        ----------
        value : int
            Value to write to the Valve2PulseDuration register.
        """
        address = OlfactometerRegisters.VALVE2_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Valve2PulseDuration")

        return reply

    def read_valve3_pulse_duration(self) -> int:
        """
        Reads the contents of the Valve3PulseDuration register.

        Returns
        -------
        int
            Value read from the Valve3PulseDuration register.
        """
        address = OlfactometerRegisters.VALVE3_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("Valve3PulseDuration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_valve3_pulse_duration(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the Valve3PulseDuration register.

        Parameters
        ----------
        value : int
            Value to write to the Valve3PulseDuration register.
        """
        address = OlfactometerRegisters.VALVE3_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Valve3PulseDuration")

        return reply

    def read_end_valve0_pulse_duration(self) -> int:
        """
        Reads the contents of the EndValve0PulseDuration register.

        Returns
        -------
        int
            Value read from the EndValve0PulseDuration register.
        """
        address = OlfactometerRegisters.END_VALVE0_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("EndValve0PulseDuration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_end_valve0_pulse_duration(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the EndValve0PulseDuration register.

        Parameters
        ----------
        value : int
            Value to write to the EndValve0PulseDuration register.
        """
        address = OlfactometerRegisters.END_VALVE0_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EndValve0PulseDuration")

        return reply

    def read_end_valve1_pulse_duration(self) -> int:
        """
        Reads the contents of the EndValve1PulseDuration register.

        Returns
        -------
        int
            Value read from the EndValve1PulseDuration register.
        """
        address = OlfactometerRegisters.END_VALVE1_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("EndValve1PulseDuration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_end_valve1_pulse_duration(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the EndValve1PulseDuration register.

        Parameters
        ----------
        value : int
            Value to write to the EndValve1PulseDuration register.
        """
        address = OlfactometerRegisters.END_VALVE1_PULSE_DURATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EndValve1PulseDuration")

        return reply

    def read_do0_sync(self) -> DO0SyncConfig:
        """
        Reads the contents of the DO0Sync register.

        Returns
        -------
        DO0SyncConfig
            Value read from the DO0Sync register.
        """
        address = OlfactometerRegisters.DO0_SYNC
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO0Sync")

        return DO0SyncConfig(reply.payload)

    def write_do0_sync(self, value: DO0SyncConfig) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO0Sync register.

        Parameters
        ----------
        value : DO0SyncConfig
            Value to write to the DO0Sync register.
        """
        address = OlfactometerRegisters.DO0_SYNC
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO0Sync")

        return reply

    def read_do1_sync(self) -> DO1SyncConfig:
        """
        Reads the contents of the DO1Sync register.

        Returns
        -------
        DO1SyncConfig
            Value read from the DO1Sync register.
        """
        address = OlfactometerRegisters.DO1_SYNC
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO1Sync")

        return DO1SyncConfig(reply.payload)

    def write_do1_sync(self, value: DO1SyncConfig) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO1Sync register.

        Parameters
        ----------
        value : DO1SyncConfig
            Value to write to the DO1Sync register.
        """
        address = OlfactometerRegisters.DO1_SYNC
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO1Sync")

        return reply

    def read_di0_trigger(self) -> DI0TriggerConfig:
        """
        Reads the contents of the DI0Trigger register.

        Returns
        -------
        DI0TriggerConfig
            Value read from the DI0Trigger register.
        """
        address = OlfactometerRegisters.DI0_TRIGGER
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DI0Trigger")

        return DI0TriggerConfig(reply.payload)

    def write_di0_trigger(self, value: DI0TriggerConfig) -> ReplyHarpMessage | None:
        """
        Writes a value to the DI0Trigger register.

        Parameters
        ----------
        value : DI0TriggerConfig
            Value to write to the DI0Trigger register.
        """
        address = OlfactometerRegisters.DI0_TRIGGER
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DI0Trigger")

        return reply

    def read_mimic_valve0(self) -> MimicOutputs:
        """
        Reads the contents of the MimicValve0 register.

        Returns
        -------
        MimicOutputs
            Value read from the MimicValve0 register.
        """
        address = OlfactometerRegisters.MIMIC_VALVE0
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("MimicValve0")

        return MimicOutputs(reply.payload)

    def write_mimic_valve0(self, value: MimicOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the MimicValve0 register.

        Parameters
        ----------
        value : MimicOutputs
            Value to write to the MimicValve0 register.
        """
        address = OlfactometerRegisters.MIMIC_VALVE0
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("MimicValve0")

        return reply

    def read_mimic_valve1(self) -> MimicOutputs:
        """
        Reads the contents of the MimicValve1 register.

        Returns
        -------
        MimicOutputs
            Value read from the MimicValve1 register.
        """
        address = OlfactometerRegisters.MIMIC_VALVE1
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("MimicValve1")

        return MimicOutputs(reply.payload)

    def write_mimic_valve1(self, value: MimicOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the MimicValve1 register.

        Parameters
        ----------
        value : MimicOutputs
            Value to write to the MimicValve1 register.
        """
        address = OlfactometerRegisters.MIMIC_VALVE1
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("MimicValve1")

        return reply

    def read_mimic_valve2(self) -> MimicOutputs:
        """
        Reads the contents of the MimicValve2 register.

        Returns
        -------
        MimicOutputs
            Value read from the MimicValve2 register.
        """
        address = OlfactometerRegisters.MIMIC_VALVE2
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("MimicValve2")

        return MimicOutputs(reply.payload)

    def write_mimic_valve2(self, value: MimicOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the MimicValve2 register.

        Parameters
        ----------
        value : MimicOutputs
            Value to write to the MimicValve2 register.
        """
        address = OlfactometerRegisters.MIMIC_VALVE2
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("MimicValve2")

        return reply

    def read_mimic_valve3(self) -> MimicOutputs:
        """
        Reads the contents of the MimicValve3 register.

        Returns
        -------
        MimicOutputs
            Value read from the MimicValve3 register.
        """
        address = OlfactometerRegisters.MIMIC_VALVE3
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("MimicValve3")

        return MimicOutputs(reply.payload)

    def write_mimic_valve3(self, value: MimicOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the MimicValve3 register.

        Parameters
        ----------
        value : MimicOutputs
            Value to write to the MimicValve3 register.
        """
        address = OlfactometerRegisters.MIMIC_VALVE3
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("MimicValve3")

        return reply

    def read_mimic_end_valve0(self) -> MimicOutputs:
        """
        Reads the contents of the MimicEndValve0 register.

        Returns
        -------
        MimicOutputs
            Value read from the MimicEndValve0 register.
        """
        address = OlfactometerRegisters.MIMIC_END_VALVE0
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("MimicEndValve0")

        return MimicOutputs(reply.payload)

    def write_mimic_end_valve0(self, value: MimicOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the MimicEndValve0 register.

        Parameters
        ----------
        value : MimicOutputs
            Value to write to the MimicEndValve0 register.
        """
        address = OlfactometerRegisters.MIMIC_END_VALVE0
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("MimicEndValve0")

        return reply

    def read_mimic_end_valve1(self) -> MimicOutputs:
        """
        Reads the contents of the MimicEndValve1 register.

        Returns
        -------
        MimicOutputs
            Value read from the MimicEndValve1 register.
        """
        address = OlfactometerRegisters.MIMIC_END_VALVE1
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("MimicEndValve1")

        return MimicOutputs(reply.payload)

    def write_mimic_end_valve1(self, value: MimicOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the MimicEndValve1 register.

        Parameters
        ----------
        value : MimicOutputs
            Value to write to the MimicEndValve1 register.
        """
        address = OlfactometerRegisters.MIMIC_END_VALVE1
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("MimicEndValve1")

        return reply

    def read_enable_valve_external_control(self) -> bool:
        """
        Reads the contents of the EnableValveExternalControl register.

        Returns
        -------
        bool
            Value read from the EnableValveExternalControl register.
        """
        address = OlfactometerRegisters.ENABLE_VALVE_EXTERNAL_CONTROL
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("EnableValveExternalControl")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_enable_valve_external_control(self, value: bool) -> ReplyHarpMessage | None:
        """
        Writes a value to the EnableValveExternalControl register.

        Parameters
        ----------
        value : bool
            Value to write to the EnableValveExternalControl register.
        """
        address = OlfactometerRegisters.ENABLE_VALVE_EXTERNAL_CONTROL
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EnableValveExternalControl")

        return reply

    def read_channel3_range(self) -> Channel3RangeConfig:
        """
        Reads the contents of the Channel3Range register.

        Returns
        -------
        Channel3RangeConfig
            Value read from the Channel3Range register.
        """
        address = OlfactometerRegisters.CHANNEL3_RANGE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("Channel3Range")

        return Channel3RangeConfig(reply.payload)

    def write_channel3_range(self, value: Channel3RangeConfig) -> ReplyHarpMessage | None:
        """
        Writes a value to the Channel3Range register.

        Parameters
        ----------
        value : Channel3RangeConfig
            Value to write to the Channel3Range register.
        """
        address = OlfactometerRegisters.CHANNEL3_RANGE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Channel3Range")

        return reply

    def read_temperature_value(self) -> int:
        """
        Reads the contents of the TemperatureValue register.

        Returns
        -------
        int
            Value read from the TemperatureValue register.
        """
        address = OlfactometerRegisters.TEMPERATURE_VALUE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("TemperatureValue")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def read_enable_temperature_calibration(self) -> int:
        """
        Reads the contents of the EnableTemperatureCalibration register.

        Returns
        -------
        int
            Value read from the EnableTemperatureCalibration register.
        """
        address = OlfactometerRegisters.ENABLE_TEMPERATURE_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("EnableTemperatureCalibration")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_enable_temperature_calibration(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the EnableTemperatureCalibration register.

        Parameters
        ----------
        value : int
            Value to write to the EnableTemperatureCalibration register.
        """
        address = OlfactometerRegisters.ENABLE_TEMPERATURE_CALIBRATION
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EnableTemperatureCalibration")

        return reply

    def read_temperature_calibration_value(self) -> int:
        """
        Reads the contents of the TemperatureCalibrationValue register.

        Returns
        -------
        int
            Value read from the TemperatureCalibrationValue register.
        """
        address = OlfactometerRegisters.TEMPERATURE_CALIBRATION_VALUE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("TemperatureCalibrationValue")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_temperature_calibration_value(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the TemperatureCalibrationValue register.

        Parameters
        ----------
        value : int
            Value to write to the TemperatureCalibrationValue register.
        """
        address = OlfactometerRegisters.TEMPERATURE_CALIBRATION_VALUE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("TemperatureCalibrationValue")

        return reply

    def read_enable_events(self) -> OlfactometerEvents:
        """
        Reads the contents of the EnableEvents register.

        Returns
        -------
        OlfactometerEvents
            Value read from the EnableEvents register.
        """
        address = OlfactometerRegisters.ENABLE_EVENTS
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("EnableEvents")

        return OlfactometerEvents(reply.payload)

    def write_enable_events(self, value: OlfactometerEvents) -> ReplyHarpMessage | None:
        """
        Writes a value to the EnableEvents register.

        Parameters
        ----------
        value : OlfactometerEvents
            Value to write to the EnableEvents register.
        """
        address = OlfactometerRegisters.ENABLE_EVENTS
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EnableEvents")

        return reply

