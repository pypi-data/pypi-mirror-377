from dataclasses import dataclass
from enum import IntEnum, IntFlag

from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage, ReplyHarpMessage
from harp.serial import Device


class DigitalInputs(IntFlag):
    """
    

    Attributes
    ----------
    DI0 : int
        _No description currently available_
    """

    NONE = 0x0
    DI0 = 0x1


class DigitalOutputs(IntFlag):
    """
    

    Attributes
    ----------
    DO0 : int
        Digital Output 0
    DO1 : int
        Digital Output 1
    DO2 : int
        Digital Output 2
    DO3 : int
        Digital Output 3
    DO4 : int
        Digital Output 4
    """

    NONE = 0x0
    DO0 = 0x1
    DO1 = 0x2
    DO2 = 0x4
    DO3 = 0x8
    DO4 = 0x16


class DI0ModeConfig(IntEnum):
    """
    Specifies the operation mode of the DI0 pin.

    Attributes
    ----------
    NONE : int
        The DI0 pin functions as a passive digital input.
    UPDATE_ON_RISING_EDGE : int
        Update the LED colors when the DI0 pin transitions from low to high.
    UPDATE_ON_HIGH : int
        Able to update RGBs when the pin is HIGH. Turn LEDs off when rising edge is detected.
    """

    NONE = 0
    UPDATE_ON_RISING_EDGE = 1
    UPDATE_ON_HIGH = 2


class DOModeConfig(IntEnum):
    """
    Specifies the operation mode of a Digital Output pin.

    Attributes
    ----------
    NONE : int
        The pin will function as a pure digital output.
    PULSE_ON_UPDATE : int
        A 1ms pulse will be triggered each time an RGB is updated.
    PULSE_ON_LOAD : int
        A 1ms pulse will be triggered each time an new array is loaded RGB.
    TOGGLE_ON_UPDATE : int
        The output pin will toggle each time an RGB is updated.
    TOGGLE_ON_LOAD : int
        The output pin will toggle each time an new array is loaded RGB.
    """

    NONE = 0
    PULSE_ON_UPDATE = 1
    PULSE_ON_LOAD = 2
    TOGGLE_ON_UPDATE = 3
    TOGGLE_ON_LOAD = 4


class RgbArrayEvents(IntEnum):
    """
    Available events to be enable in the board.

    Attributes
    ----------
    LED_STATUS : int
        _No description currently available_
    DIGITAL_INPUTS : int
        _No description currently available_
    """

    LED_STATUS = 1
    DIGITAL_INPUTS = 2


class RgbArrayRegisters(IntEnum):
    """Enum for all available registers in the RgbArray device.

    Attributes
    ----------
    LED_STATUS : int
        
    LED_COUNT : int
        The number of LEDs connected on each bus of the device.
    RGB_STATE : int
        The RGB color of each LED. [R0 G0 B0 R1 G1 B1 ...].
    RGB_BUS0_STATE : int
        The RGB color of each LED. [R0 G0 B0 R1 G1 B1 ...].
    RGB_BUS1_STATE : int
        The RGB color of each LED. [R0 G0 B0 R1 G1 B1 ...].
    RGB_OFF_STATE : int
        The RGB color of the LEDs when they are off.
    DI0_MODE : int
        
    DO0_MODE : int
        
    DO1_MODE : int
        
    LATCH_ON_NEXT_UPDATE : int
        Updates the settings of the RGBs, but will queue the instruction until a valid LedStatus command.
    DIGITAL_INPUT_STATE : int
        Reflects the state of DI digital lines of each Port
    OUTPUT_SET : int
        Set the specified digital output lines.
    OUTPUT_CLEAR : int
        Clear the specified digital output lines
    OUTPUT_TOGGLE : int
        Toggle the specified digital output lines
    OUTPUT_STATE : int
        Write the state of all digital output lines
    DIGITAL_OUTPUT_PULSE_PERIOD : int
        The pulse period in milliseconds for digital outputs.
    DIGITAL_OUTPUT_PULSE_COUNT : int
        Triggers the specified number of pulses on the digital output lines.
    EVENT_ENABLE : int
        Specifies the active events in the device.
    """

    LED_STATUS = 32
    LED_COUNT = 33
    RGB_STATE = 34
    RGB_BUS0_STATE = 35
    RGB_BUS1_STATE = 36
    RGB_OFF_STATE = 37
    DI0_MODE = 39
    DO0_MODE = 40
    DO1_MODE = 41
    LATCH_ON_NEXT_UPDATE = 43
    DIGITAL_INPUT_STATE = 44
    OUTPUT_SET = 45
    OUTPUT_CLEAR = 46
    OUTPUT_TOGGLE = 47
    OUTPUT_STATE = 48
    DIGITAL_OUTPUT_PULSE_PERIOD = 49
    DIGITAL_OUTPUT_PULSE_COUNT = 50
    EVENT_ENABLE = 51


class RgbArray(Device):
    """
    RgbArray class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1264:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1264}, got {self.WHO_AM_I}")

    def read_led_status(self) -> int:
        """
        Reads the contents of the LedStatus register.

        Returns
        -------
        int
            Value read from the LedStatus register.
        """
        address = RgbArrayRegisters.LED_STATUS
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("LedStatus")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_led_status(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the LedStatus register.

        Parameters
        ----------
        value : int
            Value to write to the LedStatus register.
        """
        address = RgbArrayRegisters.LED_STATUS
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("LedStatus")

        return reply

    def read_led_count(self) -> int:
        """
        Reads the contents of the LedCount register.

        Returns
        -------
        int
            Value read from the LedCount register.
        """
        address = RgbArrayRegisters.LED_COUNT
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("LedCount")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_led_count(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the LedCount register.

        Parameters
        ----------
        value : int
            Value to write to the LedCount register.
        """
        address = RgbArrayRegisters.LED_COUNT
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("LedCount")

        return reply

    def read_rgb_state(self) -> bytes:
        """
        Reads the contents of the RgbState register.

        Returns
        -------
        bytes
            Value read from the RgbState register.
        """
        address = RgbArrayRegisters.RGB_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("RgbState")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_rgb_state(self, value: bytes) -> ReplyHarpMessage | None:
        """
        Writes a value to the RgbState register.

        Parameters
        ----------
        value : bytes
            Value to write to the RgbState register.
        """
        address = RgbArrayRegisters.RGB_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("RgbState")

        return reply

    def read_rgb_bus0_state(self) -> bytes:
        """
        Reads the contents of the RgbBus0State register.

        Returns
        -------
        bytes
            Value read from the RgbBus0State register.
        """
        address = RgbArrayRegisters.RGB_BUS0_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("RgbBus0State")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_rgb_bus0_state(self, value: bytes) -> ReplyHarpMessage | None:
        """
        Writes a value to the RgbBus0State register.

        Parameters
        ----------
        value : bytes
            Value to write to the RgbBus0State register.
        """
        address = RgbArrayRegisters.RGB_BUS0_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("RgbBus0State")

        return reply

    def read_rgb_bus1_state(self) -> bytes:
        """
        Reads the contents of the RgbBus1State register.

        Returns
        -------
        bytes
            Value read from the RgbBus1State register.
        """
        address = RgbArrayRegisters.RGB_BUS1_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("RgbBus1State")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_rgb_bus1_state(self, value: bytes) -> ReplyHarpMessage | None:
        """
        Writes a value to the RgbBus1State register.

        Parameters
        ----------
        value : bytes
            Value to write to the RgbBus1State register.
        """
        address = RgbArrayRegisters.RGB_BUS1_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("RgbBus1State")

        return reply

    def read_rgb_off_state(self) -> bytes:
        """
        Reads the contents of the RgbOffState register.

        Returns
        -------
        bytes
            Value read from the RgbOffState register.
        """
        address = RgbArrayRegisters.RGB_OFF_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("RgbOffState")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_rgb_off_state(self, value: bytes) -> ReplyHarpMessage | None:
        """
        Writes a value to the RgbOffState register.

        Parameters
        ----------
        value : bytes
            Value to write to the RgbOffState register.
        """
        address = RgbArrayRegisters.RGB_OFF_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("RgbOffState")

        return reply

    def read_di0_mode(self) -> DI0ModeConfig:
        """
        Reads the contents of the DI0Mode register.

        Returns
        -------
        DI0ModeConfig
            Value read from the DI0Mode register.
        """
        address = RgbArrayRegisters.DI0_MODE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DI0Mode")

        return DI0ModeConfig(reply.payload)

    def write_di0_mode(self, value: DI0ModeConfig) -> ReplyHarpMessage | None:
        """
        Writes a value to the DI0Mode register.

        Parameters
        ----------
        value : DI0ModeConfig
            Value to write to the DI0Mode register.
        """
        address = RgbArrayRegisters.DI0_MODE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DI0Mode")

        return reply

    def read_do0_mode(self) -> DOModeConfig:
        """
        Reads the contents of the DO0Mode register.

        Returns
        -------
        DOModeConfig
            Value read from the DO0Mode register.
        """
        address = RgbArrayRegisters.DO0_MODE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO0Mode")

        return DOModeConfig(reply.payload)

    def write_do0_mode(self, value: DOModeConfig) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO0Mode register.

        Parameters
        ----------
        value : DOModeConfig
            Value to write to the DO0Mode register.
        """
        address = RgbArrayRegisters.DO0_MODE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO0Mode")

        return reply

    def read_do1_mode(self) -> DOModeConfig:
        """
        Reads the contents of the DO1Mode register.

        Returns
        -------
        DOModeConfig
            Value read from the DO1Mode register.
        """
        address = RgbArrayRegisters.DO1_MODE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO1Mode")

        return DOModeConfig(reply.payload)

    def write_do1_mode(self, value: DOModeConfig) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO1Mode register.

        Parameters
        ----------
        value : DOModeConfig
            Value to write to the DO1Mode register.
        """
        address = RgbArrayRegisters.DO1_MODE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO1Mode")

        return reply

    def read_latch_on_next_update(self) -> bool:
        """
        Reads the contents of the LatchOnNextUpdate register.

        Returns
        -------
        bool
            Value read from the LatchOnNextUpdate register.
        """
        address = RgbArrayRegisters.LATCH_ON_NEXT_UPDATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("LatchOnNextUpdate")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_latch_on_next_update(self, value: bool) -> ReplyHarpMessage | None:
        """
        Writes a value to the LatchOnNextUpdate register.

        Parameters
        ----------
        value : bool
            Value to write to the LatchOnNextUpdate register.
        """
        address = RgbArrayRegisters.LATCH_ON_NEXT_UPDATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("LatchOnNextUpdate")

        return reply

    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = RgbArrayRegisters.DIGITAL_INPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DigitalInputState")

        return DigitalInputs(reply.payload)

    def read_output_set(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputSet register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputSet register.
        """
        address = RgbArrayRegisters.OUTPUT_SET
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("OutputSet")

        return DigitalOutputs(reply.payload)

    def write_output_set(self, value: DigitalOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the OutputSet register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputSet register.
        """
        address = RgbArrayRegisters.OUTPUT_SET
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OutputSet")

        return reply

    def read_output_clear(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputClear register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputClear register.
        """
        address = RgbArrayRegisters.OUTPUT_CLEAR
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("OutputClear")

        return DigitalOutputs(reply.payload)

    def write_output_clear(self, value: DigitalOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the OutputClear register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputClear register.
        """
        address = RgbArrayRegisters.OUTPUT_CLEAR
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OutputClear")

        return reply

    def read_output_toggle(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputToggle register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputToggle register.
        """
        address = RgbArrayRegisters.OUTPUT_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("OutputToggle")

        return DigitalOutputs(reply.payload)

    def write_output_toggle(self, value: DigitalOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the OutputToggle register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputToggle register.
        """
        address = RgbArrayRegisters.OUTPUT_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OutputToggle")

        return reply

    def read_output_state(self) -> DigitalOutputs:
        """
        Reads the contents of the OutputState register.

        Returns
        -------
        DigitalOutputs
            Value read from the OutputState register.
        """
        address = RgbArrayRegisters.OUTPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("OutputState")

        return DigitalOutputs(reply.payload)

    def write_output_state(self, value: DigitalOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the OutputState register.

        Parameters
        ----------
        value : DigitalOutputs
            Value to write to the OutputState register.
        """
        address = RgbArrayRegisters.OUTPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OutputState")

        return reply

    def read_digital_output_pulse_period(self) -> int:
        """
        Reads the contents of the DigitalOutputPulsePeriod register.

        Returns
        -------
        int
            Value read from the DigitalOutputPulsePeriod register.
        """
        address = RgbArrayRegisters.DIGITAL_OUTPUT_PULSE_PERIOD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DigitalOutputPulsePeriod")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_digital_output_pulse_period(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DigitalOutputPulsePeriod register.

        Parameters
        ----------
        value : int
            Value to write to the DigitalOutputPulsePeriod register.
        """
        address = RgbArrayRegisters.DIGITAL_OUTPUT_PULSE_PERIOD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DigitalOutputPulsePeriod")

        return reply

    def read_digital_output_pulse_count(self) -> int:
        """
        Reads the contents of the DigitalOutputPulseCount register.

        Returns
        -------
        int
            Value read from the DigitalOutputPulseCount register.
        """
        address = RgbArrayRegisters.DIGITAL_OUTPUT_PULSE_COUNT
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DigitalOutputPulseCount")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_digital_output_pulse_count(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DigitalOutputPulseCount register.

        Parameters
        ----------
        value : int
            Value to write to the DigitalOutputPulseCount register.
        """
        address = RgbArrayRegisters.DIGITAL_OUTPUT_PULSE_COUNT
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DigitalOutputPulseCount")

        return reply

    def read_event_enable(self) -> RgbArrayEvents:
        """
        Reads the contents of the EventEnable register.

        Returns
        -------
        RgbArrayEvents
            Value read from the EventEnable register.
        """
        address = RgbArrayRegisters.EVENT_ENABLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("EventEnable")

        return RgbArrayEvents(reply.payload)

    def write_event_enable(self, value: RgbArrayEvents) -> ReplyHarpMessage | None:
        """
        Writes a value to the EventEnable register.

        Parameters
        ----------
        value : RgbArrayEvents
            Value to write to the EventEnable register.
        """
        address = RgbArrayRegisters.EVENT_ENABLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EventEnable")

        return reply

