from dataclasses import dataclass
from enum import IntEnum, IntFlag

from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage, ReplyHarpMessage
from harp.serial import Device

@dataclass
class LoadCellDataPayload:
    Channel0: int
    Channel1: int
    Channel2: int
    Channel3: int
    Channel4: int
    Channel5: int
    Channel6: int
    Channel7: int


class DigitalInputs(IntFlag):
    """
    Available digital input lines.

    Attributes
    ----------
    DI0 : int
        _No description currently available_
    """

    NONE = 0x0
    DI0 = 0x1


class SyncOutputs(IntFlag):
    """
    Specifies the state output synchronization lines.

    Attributes
    ----------
    DO0 : int
        _No description currently available_
    """

    NONE = 0x0
    DO0 = 0x1


class DigitalOutputs(IntFlag):
    """
    Specifies the state of port digital output lines.

    Attributes
    ----------
    DO1 : int
        _No description currently available_
    DO2 : int
        _No description currently available_
    DO3 : int
        _No description currently available_
    DO4 : int
        _No description currently available_
    DO5 : int
        _No description currently available_
    DO6 : int
        _No description currently available_
    DO7 : int
        _No description currently available_
    DO8 : int
        _No description currently available_
    """

    NONE = 0x0
    DO1 = 0x1
    DO2 = 0x2
    DO3 = 0x4
    DO4 = 0x8
    DO5 = 0x10
    DO6 = 0x20
    DO7 = 0x40
    DO8 = 0x80


class LoadCellEvents(IntFlag):
    """
    The events that can be enabled/disabled.

    Attributes
    ----------
    LOAD_CELL_DATA : int
        _No description currently available_
    DIGITAL_INPUT : int
        _No description currently available_
    SYNC_OUTPUT : int
        _No description currently available_
    THRESHOLDS : int
        _No description currently available_
    """

    NONE = 0x0
    LOAD_CELL_DATA = 0x1
    DIGITAL_INPUT = 0x2
    SYNC_OUTPUT = 0x4
    THRESHOLDS = 0x8


class TriggerConfig(IntEnum):
    """
    Available configurations when using a digital input as an acquisition trigger.

    Attributes
    ----------
    NONE : int
        _No description currently available_
    RISING_EDGE : int
        _No description currently available_
    FALLING_EDGE : int
        _No description currently available_
    """

    NONE = 0
    RISING_EDGE = 1
    FALLING_EDGE = 2


class SyncConfig(IntEnum):
    """
    Available configurations when using a digital output pin to report firmware events.

    Attributes
    ----------
    NONE : int
        _No description currently available_
    HEARTBEAT : int
        _No description currently available_
    PULSE : int
        _No description currently available_
    """

    NONE = 0
    HEARTBEAT = 1
    PULSE = 2


class LoadCellChannel(IntEnum):
    """
    Available target load cells to be targeted on threshold events.

    Attributes
    ----------
    CHANNEL0 : int
        _No description currently available_
    CHANNEL1 : int
        _No description currently available_
    CHANNEL2 : int
        _No description currently available_
    CHANNEL3 : int
        _No description currently available_
    CHANNEL4 : int
        _No description currently available_
    CHANNEL5 : int
        _No description currently available_
    CHANNEL6 : int
        _No description currently available_
    CHANNEL7 : int
        _No description currently available_
    NONE : int
        _No description currently available_
    """

    CHANNEL0 = 0
    CHANNEL1 = 1
    CHANNEL2 = 2
    CHANNEL3 = 3
    CHANNEL4 = 4
    CHANNEL5 = 5
    CHANNEL6 = 6
    CHANNEL7 = 7
    NONE = 8


class LoadCellsRegisters(IntEnum):
    """Enum for all available registers in the LoadCells device.

    Attributes
    ----------
    ACQUISITION_STATE : int
        Enables the data acquisition.
    LOAD_CELL_DATA : int
        Value of single ADC read from all load cell channels.
    DIGITAL_INPUT_STATE : int
        Status of the digital input pin 0. An event will be emitted when DI0Trigger == None.
    SYNC_OUTPUT_STATE : int
        Status of the digital output pin 0. An periodic event will be emitted when DO0Sync == ToggleEachSecond.
    DI0_TRIGGER : int
        Configuration of the digital input pin 0.
    DO0_SYNC : int
        Configuration of the digital output pin 0.
    DO0_PULSE_WIDTH : int
        Pulse duration (ms) for the digital output pin 0. The pulse will only be emitted when DO0Sync == Pulse.
    DIGITAL_OUTPUT_SET : int
        Set the specified digital output lines.
    DIGITAL_OUTPUT_CLEAR : int
        Clear the specified digital output lines.
    DIGITAL_OUTPUT_TOGGLE : int
        Toggle the specified digital output lines
    DIGITAL_OUTPUT_STATE : int
        Write the state of all digital output lines. An event will be emitted when the value of any pin was changed by a threshold event.
    OFFSET_LOAD_CELL0 : int
        Offset value for Load Cell channel 0.
    OFFSET_LOAD_CELL1 : int
        Offset value for Load Cell channel 1.
    OFFSET_LOAD_CELL2 : int
        Offset value for Load Cell channel 2.
    OFFSET_LOAD_CELL3 : int
        Offset value for Load Cell channel 3.
    OFFSET_LOAD_CELL4 : int
        Offset value for Load Cell channel 4.
    OFFSET_LOAD_CELL5 : int
        Offset value for Load Cell channel 5.
    OFFSET_LOAD_CELL6 : int
        Offset value for Load Cell channel 6.
    OFFSET_LOAD_CELL7 : int
        Offset value for Load Cell channel 7.
    DO1_TARGET_LOAD_CELL : int
        Target Load Cell that will be used to trigger a threshold event on DO1 pin.
    DO2_TARGET_LOAD_CELL : int
        Target Load Cell that will be used to trigger a threshold event on DO2 pin.
    DO3_TARGET_LOAD_CELL : int
        Target Load Cell that will be used to trigger a threshold event on DO3 pin.
    DO4_TARGET_LOAD_CELL : int
        Target Load Cell that will be used to trigger a threshold event on DO4 pin.
    DO5_TARGET_LOAD_CELL : int
        Target Load Cell that will be used to trigger a threshold event on DO5 pin.
    DO6_TARGET_LOAD_CELL : int
        Target Load Cell that will be used to trigger a threshold event on DO6 pin.
    DO7_TARGET_LOAD_CELL : int
        Target Load Cell that will be used to trigger a threshold event on DO7 pin.
    DO8_TARGET_LOAD_CELL : int
        Target Load Cell that will be used to trigger a threshold event on DO8 pin.
    DO1_THRESHOLD : int
        Value used to threshold a Load Cell read, and trigger DO1 pin.
    DO2_THRESHOLD : int
        Value used to threshold a Load Cell read, and trigger DO2 pin.
    DO3_THRESHOLD : int
        Value used to threshold a Load Cell read, and trigger DO3 pin.
    DO4_THRESHOLD : int
        Value used to threshold a Load Cell read, and trigger DO4 pin.
    DO5_THRESHOLD : int
        Value used to threshold a Load Cell read, and trigger DO5 pin.
    DO6_THRESHOLD : int
        Value used to threshold a Load Cell read, and trigger DO6 pin.
    DO7_THRESHOLD : int
        Value used to threshold a Load Cell read, and trigger DO7 pin.
    DO8_THRESHOLD : int
        Value used to threshold a Load Cell read, and trigger DO8 pin.
    DO1_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO1 pin event.
    DO2_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO2 pin event.
    DO3_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO3 pin event.
    DO4_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO4 pin event.
    DO5_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO5 pin event.
    DO6_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO6 pin event.
    DO7_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO7 pin event.
    DO8_TIME_ABOVE_THRESHOLD : int
        Time (ms) above threshold value that is required to trigger a DO8 pin event.
    DO1_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO1 pin event.
    DO2_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO2 pin event.
    DO3_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO3 pin event.
    DO4_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO4 pin event.
    DO5_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO5 pin event.
    DO6_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO6 pin event.
    DO7_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO7 pin event.
    DO8_TIME_BELOW_THRESHOLD : int
        Time (ms) below threshold value that is required to trigger a DO8 pin event.
    ENABLE_EVENTS : int
        Specifies the active events in the device.
    """

    ACQUISITION_STATE = 32
    LOAD_CELL_DATA = 33
    DIGITAL_INPUT_STATE = 34
    SYNC_OUTPUT_STATE = 35
    DI0_TRIGGER = 39
    DO0_SYNC = 40
    DO0_PULSE_WIDTH = 41
    DIGITAL_OUTPUT_SET = 42
    DIGITAL_OUTPUT_CLEAR = 43
    DIGITAL_OUTPUT_TOGGLE = 44
    DIGITAL_OUTPUT_STATE = 45
    OFFSET_LOAD_CELL0 = 48
    OFFSET_LOAD_CELL1 = 49
    OFFSET_LOAD_CELL2 = 50
    OFFSET_LOAD_CELL3 = 51
    OFFSET_LOAD_CELL4 = 52
    OFFSET_LOAD_CELL5 = 53
    OFFSET_LOAD_CELL6 = 54
    OFFSET_LOAD_CELL7 = 55
    DO1_TARGET_LOAD_CELL = 58
    DO2_TARGET_LOAD_CELL = 59
    DO3_TARGET_LOAD_CELL = 60
    DO4_TARGET_LOAD_CELL = 61
    DO5_TARGET_LOAD_CELL = 62
    DO6_TARGET_LOAD_CELL = 63
    DO7_TARGET_LOAD_CELL = 64
    DO8_TARGET_LOAD_CELL = 65
    DO1_THRESHOLD = 66
    DO2_THRESHOLD = 67
    DO3_THRESHOLD = 68
    DO4_THRESHOLD = 69
    DO5_THRESHOLD = 70
    DO6_THRESHOLD = 71
    DO7_THRESHOLD = 72
    DO8_THRESHOLD = 73
    DO1_TIME_ABOVE_THRESHOLD = 74
    DO2_TIME_ABOVE_THRESHOLD = 75
    DO3_TIME_ABOVE_THRESHOLD = 76
    DO4_TIME_ABOVE_THRESHOLD = 77
    DO5_TIME_ABOVE_THRESHOLD = 78
    DO6_TIME_ABOVE_THRESHOLD = 79
    DO7_TIME_ABOVE_THRESHOLD = 80
    DO8_TIME_ABOVE_THRESHOLD = 81
    DO1_TIME_BELOW_THRESHOLD = 82
    DO2_TIME_BELOW_THRESHOLD = 83
    DO3_TIME_BELOW_THRESHOLD = 84
    DO4_TIME_BELOW_THRESHOLD = 85
    DO5_TIME_BELOW_THRESHOLD = 86
    DO6_TIME_BELOW_THRESHOLD = 87
    DO7_TIME_BELOW_THRESHOLD = 88
    DO8_TIME_BELOW_THRESHOLD = 89
    ENABLE_EVENTS = 90


class LoadCells(Device):
    """
    LoadCells class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1232:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1232}, got {self.WHO_AM_I}")

    def read_acquisition_state(self) -> bool:
        """
        Reads the contents of the AcquisitionState register.

        Returns
        -------
        bool
            Value read from the AcquisitionState register.
        """
        address = LoadCellsRegisters.ACQUISITION_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("AcquisitionState")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_acquisition_state(self, value: bool) -> ReplyHarpMessage | None:
        """
        Writes a value to the AcquisitionState register.

        Parameters
        ----------
        value : bool
            Value to write to the AcquisitionState register.
        """
        address = LoadCellsRegisters.ACQUISITION_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("AcquisitionState")

        return reply

    def read_load_cell_data(self) -> LoadCellDataPayload:
        """
        Reads the contents of the LoadCellData register.

        Returns
        -------
        LoadCellDataPayload
            Value read from the LoadCellData register.
        """
        address = LoadCellsRegisters.LOAD_CELL_DATA
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("LoadCellData")

        # Map payload (list/array) to dataclass fields by offset
        payload = reply.payload
        return LoadCellDataPayload(
            Channel0=payload[0],
            Channel1=payload[1],
            Channel2=payload[2],
            Channel3=payload[3],
            Channel4=payload[4],
            Channel5=payload[5],
            Channel6=payload[6],
            Channel7=payload[7]
        )

    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = LoadCellsRegisters.DIGITAL_INPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DigitalInputState")

        return DigitalInputs(reply.payload)

    def read_sync_output_state(self) -> SyncOutputs:
        """
        Reads the contents of the SyncOutputState register.

        Returns
        -------
        SyncOutputs
            Value read from the SyncOutputState register.
        """
        address = LoadCellsRegisters.SYNC_OUTPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("SyncOutputState")

        return SyncOutputs(reply.payload)

    def read_di0_trigger(self) -> TriggerConfig:
        """
        Reads the contents of the DI0Trigger register.

        Returns
        -------
        TriggerConfig
            Value read from the DI0Trigger register.
        """
        address = LoadCellsRegisters.DI0_TRIGGER
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DI0Trigger")

        return TriggerConfig(reply.payload)

    def write_di0_trigger(self, value: TriggerConfig) -> ReplyHarpMessage | None:
        """
        Writes a value to the DI0Trigger register.

        Parameters
        ----------
        value : TriggerConfig
            Value to write to the DI0Trigger register.
        """
        address = LoadCellsRegisters.DI0_TRIGGER
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DI0Trigger")

        return reply

    def read_do0_sync(self) -> SyncConfig:
        """
        Reads the contents of the DO0Sync register.

        Returns
        -------
        SyncConfig
            Value read from the DO0Sync register.
        """
        address = LoadCellsRegisters.DO0_SYNC
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO0Sync")

        return SyncConfig(reply.payload)

    def write_do0_sync(self, value: SyncConfig) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO0Sync register.

        Parameters
        ----------
        value : SyncConfig
            Value to write to the DO0Sync register.
        """
        address = LoadCellsRegisters.DO0_SYNC
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO0Sync")

        return reply

    def read_do0_pulse_width(self) -> int:
        """
        Reads the contents of the DO0PulseWidth register.

        Returns
        -------
        int
            Value read from the DO0PulseWidth register.
        """
        address = LoadCellsRegisters.DO0_PULSE_WIDTH
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO0PulseWidth")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do0_pulse_width(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO0PulseWidth register.

        Parameters
        ----------
        value : int
            Value to write to the DO0PulseWidth register.
        """
        address = LoadCellsRegisters.DO0_PULSE_WIDTH
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO0PulseWidth")

        return reply

    def read_digital_output_set(self) -> DigitalOutputs:
        """
        Reads the contents of the DigitalOutputSet register.

        Returns
        -------
        DigitalOutputs
            Value read from the DigitalOutputSet register.
        """
        address = LoadCellsRegisters.DIGITAL_OUTPUT_SET
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
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
        address = LoadCellsRegisters.DIGITAL_OUTPUT_SET
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
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
        address = LoadCellsRegisters.DIGITAL_OUTPUT_CLEAR
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
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
        address = LoadCellsRegisters.DIGITAL_OUTPUT_CLEAR
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
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
        address = LoadCellsRegisters.DIGITAL_OUTPUT_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
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
        address = LoadCellsRegisters.DIGITAL_OUTPUT_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
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
        address = LoadCellsRegisters.DIGITAL_OUTPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
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
        address = LoadCellsRegisters.DIGITAL_OUTPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DigitalOutputState")

        return reply

    def read_offset_load_cell0(self) -> int:
        """
        Reads the contents of the OffsetLoadCell0 register.

        Returns
        -------
        int
            Value read from the OffsetLoadCell0 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL0
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("OffsetLoadCell0")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_offset_load_cell0(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the OffsetLoadCell0 register.

        Parameters
        ----------
        value : int
            Value to write to the OffsetLoadCell0 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL0
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OffsetLoadCell0")

        return reply

    def read_offset_load_cell1(self) -> int:
        """
        Reads the contents of the OffsetLoadCell1 register.

        Returns
        -------
        int
            Value read from the OffsetLoadCell1 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL1
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("OffsetLoadCell1")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_offset_load_cell1(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the OffsetLoadCell1 register.

        Parameters
        ----------
        value : int
            Value to write to the OffsetLoadCell1 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL1
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OffsetLoadCell1")

        return reply

    def read_offset_load_cell2(self) -> int:
        """
        Reads the contents of the OffsetLoadCell2 register.

        Returns
        -------
        int
            Value read from the OffsetLoadCell2 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL2
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("OffsetLoadCell2")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_offset_load_cell2(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the OffsetLoadCell2 register.

        Parameters
        ----------
        value : int
            Value to write to the OffsetLoadCell2 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL2
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OffsetLoadCell2")

        return reply

    def read_offset_load_cell3(self) -> int:
        """
        Reads the contents of the OffsetLoadCell3 register.

        Returns
        -------
        int
            Value read from the OffsetLoadCell3 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL3
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("OffsetLoadCell3")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_offset_load_cell3(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the OffsetLoadCell3 register.

        Parameters
        ----------
        value : int
            Value to write to the OffsetLoadCell3 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL3
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OffsetLoadCell3")

        return reply

    def read_offset_load_cell4(self) -> int:
        """
        Reads the contents of the OffsetLoadCell4 register.

        Returns
        -------
        int
            Value read from the OffsetLoadCell4 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL4
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("OffsetLoadCell4")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_offset_load_cell4(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the OffsetLoadCell4 register.

        Parameters
        ----------
        value : int
            Value to write to the OffsetLoadCell4 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL4
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OffsetLoadCell4")

        return reply

    def read_offset_load_cell5(self) -> int:
        """
        Reads the contents of the OffsetLoadCell5 register.

        Returns
        -------
        int
            Value read from the OffsetLoadCell5 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL5
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("OffsetLoadCell5")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_offset_load_cell5(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the OffsetLoadCell5 register.

        Parameters
        ----------
        value : int
            Value to write to the OffsetLoadCell5 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL5
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OffsetLoadCell5")

        return reply

    def read_offset_load_cell6(self) -> int:
        """
        Reads the contents of the OffsetLoadCell6 register.

        Returns
        -------
        int
            Value read from the OffsetLoadCell6 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL6
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("OffsetLoadCell6")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_offset_load_cell6(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the OffsetLoadCell6 register.

        Parameters
        ----------
        value : int
            Value to write to the OffsetLoadCell6 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL6
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OffsetLoadCell6")

        return reply

    def read_offset_load_cell7(self) -> int:
        """
        Reads the contents of the OffsetLoadCell7 register.

        Returns
        -------
        int
            Value read from the OffsetLoadCell7 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL7
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("OffsetLoadCell7")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_offset_load_cell7(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the OffsetLoadCell7 register.

        Parameters
        ----------
        value : int
            Value to write to the OffsetLoadCell7 register.
        """
        address = LoadCellsRegisters.OFFSET_LOAD_CELL7
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OffsetLoadCell7")

        return reply

    def read_do1_target_load_cell(self) -> LoadCellChannel:
        """
        Reads the contents of the DO1TargetLoadCell register.

        Returns
        -------
        LoadCellChannel
            Value read from the DO1TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO1_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO1TargetLoadCell")

        return LoadCellChannel(reply.payload)

    def write_do1_target_load_cell(self, value: LoadCellChannel) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO1TargetLoadCell register.

        Parameters
        ----------
        value : LoadCellChannel
            Value to write to the DO1TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO1_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO1TargetLoadCell")

        return reply

    def read_do2_target_load_cell(self) -> LoadCellChannel:
        """
        Reads the contents of the DO2TargetLoadCell register.

        Returns
        -------
        LoadCellChannel
            Value read from the DO2TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO2_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO2TargetLoadCell")

        return LoadCellChannel(reply.payload)

    def write_do2_target_load_cell(self, value: LoadCellChannel) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO2TargetLoadCell register.

        Parameters
        ----------
        value : LoadCellChannel
            Value to write to the DO2TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO2_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO2TargetLoadCell")

        return reply

    def read_do3_target_load_cell(self) -> LoadCellChannel:
        """
        Reads the contents of the DO3TargetLoadCell register.

        Returns
        -------
        LoadCellChannel
            Value read from the DO3TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO3_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO3TargetLoadCell")

        return LoadCellChannel(reply.payload)

    def write_do3_target_load_cell(self, value: LoadCellChannel) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO3TargetLoadCell register.

        Parameters
        ----------
        value : LoadCellChannel
            Value to write to the DO3TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO3_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO3TargetLoadCell")

        return reply

    def read_do4_target_load_cell(self) -> LoadCellChannel:
        """
        Reads the contents of the DO4TargetLoadCell register.

        Returns
        -------
        LoadCellChannel
            Value read from the DO4TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO4_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO4TargetLoadCell")

        return LoadCellChannel(reply.payload)

    def write_do4_target_load_cell(self, value: LoadCellChannel) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO4TargetLoadCell register.

        Parameters
        ----------
        value : LoadCellChannel
            Value to write to the DO4TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO4_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO4TargetLoadCell")

        return reply

    def read_do5_target_load_cell(self) -> LoadCellChannel:
        """
        Reads the contents of the DO5TargetLoadCell register.

        Returns
        -------
        LoadCellChannel
            Value read from the DO5TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO5_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO5TargetLoadCell")

        return LoadCellChannel(reply.payload)

    def write_do5_target_load_cell(self, value: LoadCellChannel) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO5TargetLoadCell register.

        Parameters
        ----------
        value : LoadCellChannel
            Value to write to the DO5TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO5_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO5TargetLoadCell")

        return reply

    def read_do6_target_load_cell(self) -> LoadCellChannel:
        """
        Reads the contents of the DO6TargetLoadCell register.

        Returns
        -------
        LoadCellChannel
            Value read from the DO6TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO6_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO6TargetLoadCell")

        return LoadCellChannel(reply.payload)

    def write_do6_target_load_cell(self, value: LoadCellChannel) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO6TargetLoadCell register.

        Parameters
        ----------
        value : LoadCellChannel
            Value to write to the DO6TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO6_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO6TargetLoadCell")

        return reply

    def read_do7_target_load_cell(self) -> LoadCellChannel:
        """
        Reads the contents of the DO7TargetLoadCell register.

        Returns
        -------
        LoadCellChannel
            Value read from the DO7TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO7_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO7TargetLoadCell")

        return LoadCellChannel(reply.payload)

    def write_do7_target_load_cell(self, value: LoadCellChannel) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO7TargetLoadCell register.

        Parameters
        ----------
        value : LoadCellChannel
            Value to write to the DO7TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO7_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO7TargetLoadCell")

        return reply

    def read_do8_target_load_cell(self) -> LoadCellChannel:
        """
        Reads the contents of the DO8TargetLoadCell register.

        Returns
        -------
        LoadCellChannel
            Value read from the DO8TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO8_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO8TargetLoadCell")

        return LoadCellChannel(reply.payload)

    def write_do8_target_load_cell(self, value: LoadCellChannel) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO8TargetLoadCell register.

        Parameters
        ----------
        value : LoadCellChannel
            Value to write to the DO8TargetLoadCell register.
        """
        address = LoadCellsRegisters.DO8_TARGET_LOAD_CELL
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO8TargetLoadCell")

        return reply

    def read_do1_threshold(self) -> int:
        """
        Reads the contents of the DO1Threshold register.

        Returns
        -------
        int
            Value read from the DO1Threshold register.
        """
        address = LoadCellsRegisters.DO1_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO1Threshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do1_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO1Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO1Threshold register.
        """
        address = LoadCellsRegisters.DO1_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO1Threshold")

        return reply

    def read_do2_threshold(self) -> int:
        """
        Reads the contents of the DO2Threshold register.

        Returns
        -------
        int
            Value read from the DO2Threshold register.
        """
        address = LoadCellsRegisters.DO2_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO2Threshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do2_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO2Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO2Threshold register.
        """
        address = LoadCellsRegisters.DO2_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO2Threshold")

        return reply

    def read_do3_threshold(self) -> int:
        """
        Reads the contents of the DO3Threshold register.

        Returns
        -------
        int
            Value read from the DO3Threshold register.
        """
        address = LoadCellsRegisters.DO3_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO3Threshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do3_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO3Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO3Threshold register.
        """
        address = LoadCellsRegisters.DO3_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO3Threshold")

        return reply

    def read_do4_threshold(self) -> int:
        """
        Reads the contents of the DO4Threshold register.

        Returns
        -------
        int
            Value read from the DO4Threshold register.
        """
        address = LoadCellsRegisters.DO4_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO4Threshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do4_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO4Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO4Threshold register.
        """
        address = LoadCellsRegisters.DO4_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO4Threshold")

        return reply

    def read_do5_threshold(self) -> int:
        """
        Reads the contents of the DO5Threshold register.

        Returns
        -------
        int
            Value read from the DO5Threshold register.
        """
        address = LoadCellsRegisters.DO5_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO5Threshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do5_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO5Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO5Threshold register.
        """
        address = LoadCellsRegisters.DO5_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO5Threshold")

        return reply

    def read_do6_threshold(self) -> int:
        """
        Reads the contents of the DO6Threshold register.

        Returns
        -------
        int
            Value read from the DO6Threshold register.
        """
        address = LoadCellsRegisters.DO6_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO6Threshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do6_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO6Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO6Threshold register.
        """
        address = LoadCellsRegisters.DO6_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO6Threshold")

        return reply

    def read_do7_threshold(self) -> int:
        """
        Reads the contents of the DO7Threshold register.

        Returns
        -------
        int
            Value read from the DO7Threshold register.
        """
        address = LoadCellsRegisters.DO7_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO7Threshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do7_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO7Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO7Threshold register.
        """
        address = LoadCellsRegisters.DO7_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO7Threshold")

        return reply

    def read_do8_threshold(self) -> int:
        """
        Reads the contents of the DO8Threshold register.

        Returns
        -------
        int
            Value read from the DO8Threshold register.
        """
        address = LoadCellsRegisters.DO8_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.S16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO8Threshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do8_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO8Threshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO8Threshold register.
        """
        address = LoadCellsRegisters.DO8_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.S16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO8Threshold")

        return reply

    def read_do1_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO1TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO1TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO1_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO1TimeAboveThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do1_time_above_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO1TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO1TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO1_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO1TimeAboveThreshold")

        return reply

    def read_do2_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO2TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO2TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO2_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO2TimeAboveThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do2_time_above_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO2TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO2TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO2_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO2TimeAboveThreshold")

        return reply

    def read_do3_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO3TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO3TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO3_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO3TimeAboveThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do3_time_above_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO3TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO3TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO3_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO3TimeAboveThreshold")

        return reply

    def read_do4_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO4TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO4TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO4_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO4TimeAboveThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do4_time_above_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO4TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO4TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO4_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO4TimeAboveThreshold")

        return reply

    def read_do5_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO5TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO5TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO5_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO5TimeAboveThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do5_time_above_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO5TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO5TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO5_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO5TimeAboveThreshold")

        return reply

    def read_do6_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO6TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO6TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO6_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO6TimeAboveThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do6_time_above_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO6TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO6TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO6_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO6TimeAboveThreshold")

        return reply

    def read_do7_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO7TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO7TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO7_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO7TimeAboveThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do7_time_above_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO7TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO7TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO7_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO7TimeAboveThreshold")

        return reply

    def read_do8_time_above_threshold(self) -> int:
        """
        Reads the contents of the DO8TimeAboveThreshold register.

        Returns
        -------
        int
            Value read from the DO8TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO8_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO8TimeAboveThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do8_time_above_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO8TimeAboveThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO8TimeAboveThreshold register.
        """
        address = LoadCellsRegisters.DO8_TIME_ABOVE_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO8TimeAboveThreshold")

        return reply

    def read_do1_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO1TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO1TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO1_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO1TimeBelowThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do1_time_below_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO1TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO1TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO1_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO1TimeBelowThreshold")

        return reply

    def read_do2_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO2TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO2TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO2_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO2TimeBelowThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do2_time_below_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO2TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO2TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO2_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO2TimeBelowThreshold")

        return reply

    def read_do3_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO3TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO3TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO3_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO3TimeBelowThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do3_time_below_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO3TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO3TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO3_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO3TimeBelowThreshold")

        return reply

    def read_do4_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO4TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO4TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO4_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO4TimeBelowThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do4_time_below_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO4TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO4TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO4_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO4TimeBelowThreshold")

        return reply

    def read_do5_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO5TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO5TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO5_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO5TimeBelowThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do5_time_below_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO5TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO5TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO5_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO5TimeBelowThreshold")

        return reply

    def read_do6_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO6TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO6TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO6_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO6TimeBelowThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do6_time_below_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO6TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO6TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO6_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO6TimeBelowThreshold")

        return reply

    def read_do7_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO7TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO7TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO7_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO7TimeBelowThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do7_time_below_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO7TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO7TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO7_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO7TimeBelowThreshold")

        return reply

    def read_do8_time_below_threshold(self) -> int:
        """
        Reads the contents of the DO8TimeBelowThreshold register.

        Returns
        -------
        int
            Value read from the DO8TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO8_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("DO8TimeBelowThreshold")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_do8_time_below_threshold(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the DO8TimeBelowThreshold register.

        Parameters
        ----------
        value : int
            Value to write to the DO8TimeBelowThreshold register.
        """
        address = LoadCellsRegisters.DO8_TIME_BELOW_THRESHOLD
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("DO8TimeBelowThreshold")

        return reply

    def read_enable_events(self) -> LoadCellEvents:
        """
        Reads the contents of the EnableEvents register.

        Returns
        -------
        LoadCellEvents
            Value read from the EnableEvents register.
        """
        address = LoadCellsRegisters.ENABLE_EVENTS
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("EnableEvents")

        return LoadCellEvents(reply.payload)

    def write_enable_events(self, value: LoadCellEvents) -> ReplyHarpMessage | None:
        """
        Writes a value to the EnableEvents register.

        Parameters
        ----------
        value : LoadCellEvents
            Value to write to the EnableEvents register.
        """
        address = LoadCellsRegisters.ENABLE_EVENTS
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EnableEvents")

        return reply

