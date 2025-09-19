from dataclasses import dataclass
from enum import IntEnum, IntFlag

from harp.protocol import MessageType, PayloadType
from harp.protocol.exceptions import HarpReadException, HarpWriteException
from harp.protocol.messages import HarpMessage, ReplyHarpMessage
from harp.serial import Device


class DigitalInputs(IntFlag):
    """
    Specifies the state of port digital input lines

    Attributes
    ----------
    DI0 : int
        _No description currently available_
    DI1 : int
        _No description currently available_
    """

    NONE = 0x0
    DI0 = 0x1
    DI1 = 0x2


class DigitalOutputs(IntFlag):
    """
    Specifies the state of port digital output lines

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


class LedOutputs(IntFlag):
    """
    Specifies the state of LED driver's outputs

    Attributes
    ----------
    LED0 : int
        _No description currently available_
    LED1 : int
        _No description currently available_
    """

    NONE = 0x0
    LED0 = 0x1
    LED1 = 0x2


class LedRamps(IntFlag):
    """
    Specifies the configuration of LED driver's ramps

    Attributes
    ----------
    LED0_UP : int
        _No description currently available_
    LED0_DOWN : int
        _No description currently available_
    LED1_UP : int
        _No description currently available_
    LED1_DOWN : int
        _No description currently available_
    """

    NONE = 0x0
    LED0_UP = 0x1
    LED0_DOWN = 0x2
    LED1_UP = 0x4
    LED1_DOWN = 0x8


class CurrentDriverEvents(IntFlag):
    """
    Specifies the active events in the device.

    Attributes
    ----------
    DIS : int
        _No description currently available_
    """

    NONE = 0x0
    DIS = 0x1


class CurrentDriverRegisters(IntEnum):
    """Enum for all available registers in the CurrentDriver device.

    Attributes
    ----------
    DIGITAL_INPUT_STATE : int
        Reflects the state of DI digital lines
    OUTPUT_SET : int
        Set the specified digital output lines
    OUTPUT_CLEAR : int
        Clear the specified digital output lines
    OUTPUT_TOGGLE : int
        Toggle the specified digital output lines
    OUTPUT_STATE : int
        Write the state of all digital output lines
    LED0_CURRENT : int
        Configuration of current to drive LED 0 [0:1000] mA
    LED1_CURRENT : int
        Configuration of current to drive LED 1 [0:1000] mA
    DAC0_VOLTAGE : int
        Configuration of DAC 0 voltage [0:5000] mV
    DAC1_VOLTAGE : int
        Configuration of DAC 1 voltage [0:5000] mV
    LED_ENABLE : int
        Enable driver on the selected output
    LED_DISABLE : int
        Disable driver on the selected output
    LED_STATE : int
        Control the correspondent LED output
    LED0_MAX_CURRENT : int
        Configuration of current to drive LED 0 [0:1000] mA
    LED1_MAX_CURRENT : int
        Configuration of current to drive LED 1 [0:1000] mA
    PULSE_ENABLE : int
        Enables the pulse function for the specified output DACs/LEDs
    PULSE_DUTY_CYCLE_LED0 : int
        Specifies the duty cycle of the output pulse from 1 to 100
    PULSE_DUTY_CYCLE_LED1 : int
        Specifies the duty cycle of the output pulse from 1 to 100
    PULSE_FREQUENCY_LED0 : int
        Specifies the frequency of the output pulse in Hz
    PULSE_FREQUENCY_LED1 : int
        Specifies the frequency of the output pulse in Hz
    RAMP_LED0 : int
        Specifies the ramp time of the transitions between different current/voltage values in milliseconds. The ramp will only work if the pulse function is off
    RAMP_LED1 : int
        Specifies the ramp time of the transitions between different current/voltage values in milliseconds. The ramp will only work if the pulse function is off
    RAMP_CONFIG : int
        Specifies when the ramps are applied for each DAC/LED
    ENABLE_EVENTS : int
        Specifies the active events in the device
    """

    DIGITAL_INPUT_STATE = 32
    OUTPUT_SET = 33
    OUTPUT_CLEAR = 34
    OUTPUT_TOGGLE = 35
    OUTPUT_STATE = 36
    LED0_CURRENT = 37
    LED1_CURRENT = 38
    DAC0_VOLTAGE = 39
    DAC1_VOLTAGE = 40
    LED_ENABLE = 41
    LED_DISABLE = 42
    LED_STATE = 43
    LED0_MAX_CURRENT = 44
    LED1_MAX_CURRENT = 45
    PULSE_ENABLE = 46
    PULSE_DUTY_CYCLE_LED0 = 47
    PULSE_DUTY_CYCLE_LED1 = 48
    PULSE_FREQUENCY_LED0 = 49
    PULSE_FREQUENCY_LED1 = 50
    RAMP_LED0 = 51
    RAMP_LED1 = 52
    RAMP_CONFIG = 53
    ENABLE_EVENTS = 58


class CurrentDriver(Device):
    """
    CurrentDriver class for controlling the device.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # connect and load already happened in the base class
        # verify that WHO_AM_I matches the expected value
        if self.WHO_AM_I != 1282:
            self.disconnect()
            raise Exception(f"WHO_AM_I mismatch: expected {1282}, got {self.WHO_AM_I}")

    def read_digital_input_state(self) -> DigitalInputs:
        """
        Reads the contents of the DigitalInputState register.

        Returns
        -------
        DigitalInputs
            Value read from the DigitalInputState register.
        """
        address = CurrentDriverRegisters.DIGITAL_INPUT_STATE
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
        address = CurrentDriverRegisters.OUTPUT_SET
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
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
        address = CurrentDriverRegisters.OUTPUT_SET
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
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
        address = CurrentDriverRegisters.OUTPUT_CLEAR
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
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
        address = CurrentDriverRegisters.OUTPUT_CLEAR
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
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
        address = CurrentDriverRegisters.OUTPUT_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
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
        address = CurrentDriverRegisters.OUTPUT_TOGGLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
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
        address = CurrentDriverRegisters.OUTPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
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
        address = CurrentDriverRegisters.OUTPUT_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("OutputState")

        return reply

    def read_led0_current(self) -> float:
        """
        Reads the contents of the Led0Current register.

        Returns
        -------
        float
            Value read from the Led0Current register.
        """
        address = CurrentDriverRegisters.LED0_CURRENT
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Led0Current")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_led0_current(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Led0Current register.

        Parameters
        ----------
        value : float
            Value to write to the Led0Current register.
        """
        address = CurrentDriverRegisters.LED0_CURRENT
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Led0Current")

        return reply

    def read_led1_current(self) -> float:
        """
        Reads the contents of the Led1Current register.

        Returns
        -------
        float
            Value read from the Led1Current register.
        """
        address = CurrentDriverRegisters.LED1_CURRENT
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Led1Current")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_led1_current(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Led1Current register.

        Parameters
        ----------
        value : float
            Value to write to the Led1Current register.
        """
        address = CurrentDriverRegisters.LED1_CURRENT
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Led1Current")

        return reply

    def read_dac0_voltage(self) -> float:
        """
        Reads the contents of the Dac0Voltage register.

        Returns
        -------
        float
            Value read from the Dac0Voltage register.
        """
        address = CurrentDriverRegisters.DAC0_VOLTAGE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Dac0Voltage")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_dac0_voltage(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Dac0Voltage register.

        Parameters
        ----------
        value : float
            Value to write to the Dac0Voltage register.
        """
        address = CurrentDriverRegisters.DAC0_VOLTAGE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Dac0Voltage")

        return reply

    def read_dac1_voltage(self) -> float:
        """
        Reads the contents of the Dac1Voltage register.

        Returns
        -------
        float
            Value read from the Dac1Voltage register.
        """
        address = CurrentDriverRegisters.DAC1_VOLTAGE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Dac1Voltage")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_dac1_voltage(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Dac1Voltage register.

        Parameters
        ----------
        value : float
            Value to write to the Dac1Voltage register.
        """
        address = CurrentDriverRegisters.DAC1_VOLTAGE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Dac1Voltage")

        return reply

    def read_led_enable(self) -> LedOutputs:
        """
        Reads the contents of the LedEnable register.

        Returns
        -------
        LedOutputs
            Value read from the LedEnable register.
        """
        address = CurrentDriverRegisters.LED_ENABLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("LedEnable")

        return LedOutputs(reply.payload)

    def write_led_enable(self, value: LedOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the LedEnable register.

        Parameters
        ----------
        value : LedOutputs
            Value to write to the LedEnable register.
        """
        address = CurrentDriverRegisters.LED_ENABLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("LedEnable")

        return reply

    def read_led_disable(self) -> LedOutputs:
        """
        Reads the contents of the LedDisable register.

        Returns
        -------
        LedOutputs
            Value read from the LedDisable register.
        """
        address = CurrentDriverRegisters.LED_DISABLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("LedDisable")

        return LedOutputs(reply.payload)

    def write_led_disable(self, value: LedOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the LedDisable register.

        Parameters
        ----------
        value : LedOutputs
            Value to write to the LedDisable register.
        """
        address = CurrentDriverRegisters.LED_DISABLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("LedDisable")

        return reply

    def read_led_state(self) -> LedOutputs:
        """
        Reads the contents of the LedState register.

        Returns
        -------
        LedOutputs
            Value read from the LedState register.
        """
        address = CurrentDriverRegisters.LED_STATE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("LedState")

        return LedOutputs(reply.payload)

    def write_led_state(self, value: LedOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the LedState register.

        Parameters
        ----------
        value : LedOutputs
            Value to write to the LedState register.
        """
        address = CurrentDriverRegisters.LED_STATE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("LedState")

        return reply

    def read_led0_max_current(self) -> float:
        """
        Reads the contents of the Led0MaxCurrent register.

        Returns
        -------
        float
            Value read from the Led0MaxCurrent register.
        """
        address = CurrentDriverRegisters.LED0_MAX_CURRENT
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Led0MaxCurrent")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_led0_max_current(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Led0MaxCurrent register.

        Parameters
        ----------
        value : float
            Value to write to the Led0MaxCurrent register.
        """
        address = CurrentDriverRegisters.LED0_MAX_CURRENT
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Led0MaxCurrent")

        return reply

    def read_led1_max_current(self) -> float:
        """
        Reads the contents of the Led1MaxCurrent register.

        Returns
        -------
        float
            Value read from the Led1MaxCurrent register.
        """
        address = CurrentDriverRegisters.LED1_MAX_CURRENT
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.Float))
        if reply is not None and reply.is_error:
            raise HarpReadException("Led1MaxCurrent")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_led1_max_current(self, value: float) -> ReplyHarpMessage | None:
        """
        Writes a value to the Led1MaxCurrent register.

        Parameters
        ----------
        value : float
            Value to write to the Led1MaxCurrent register.
        """
        address = CurrentDriverRegisters.LED1_MAX_CURRENT
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.Float, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("Led1MaxCurrent")

        return reply

    def read_pulse_enable(self) -> LedOutputs:
        """
        Reads the contents of the PulseEnable register.

        Returns
        -------
        LedOutputs
            Value read from the PulseEnable register.
        """
        address = CurrentDriverRegisters.PULSE_ENABLE
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("PulseEnable")

        return LedOutputs(reply.payload)

    def write_pulse_enable(self, value: LedOutputs) -> ReplyHarpMessage | None:
        """
        Writes a value to the PulseEnable register.

        Parameters
        ----------
        value : LedOutputs
            Value to write to the PulseEnable register.
        """
        address = CurrentDriverRegisters.PULSE_ENABLE
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("PulseEnable")

        return reply

    def read_pulse_duty_cycle_led0(self) -> int:
        """
        Reads the contents of the PulseDutyCycleLed0 register.

        Returns
        -------
        int
            Value read from the PulseDutyCycleLed0 register.
        """
        address = CurrentDriverRegisters.PULSE_DUTY_CYCLE_LED0
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("PulseDutyCycleLed0")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_pulse_duty_cycle_led0(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the PulseDutyCycleLed0 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDutyCycleLed0 register.
        """
        address = CurrentDriverRegisters.PULSE_DUTY_CYCLE_LED0
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("PulseDutyCycleLed0")

        return reply

    def read_pulse_duty_cycle_led1(self) -> int:
        """
        Reads the contents of the PulseDutyCycleLed1 register.

        Returns
        -------
        int
            Value read from the PulseDutyCycleLed1 register.
        """
        address = CurrentDriverRegisters.PULSE_DUTY_CYCLE_LED1
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("PulseDutyCycleLed1")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_pulse_duty_cycle_led1(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the PulseDutyCycleLed1 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseDutyCycleLed1 register.
        """
        address = CurrentDriverRegisters.PULSE_DUTY_CYCLE_LED1
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("PulseDutyCycleLed1")

        return reply

    def read_pulse_frequency_led0(self) -> int:
        """
        Reads the contents of the PulseFrequencyLed0 register.

        Returns
        -------
        int
            Value read from the PulseFrequencyLed0 register.
        """
        address = CurrentDriverRegisters.PULSE_FREQUENCY_LED0
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("PulseFrequencyLed0")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_pulse_frequency_led0(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the PulseFrequencyLed0 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseFrequencyLed0 register.
        """
        address = CurrentDriverRegisters.PULSE_FREQUENCY_LED0
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("PulseFrequencyLed0")

        return reply

    def read_pulse_frequency_led1(self) -> int:
        """
        Reads the contents of the PulseFrequencyLed1 register.

        Returns
        -------
        int
            Value read from the PulseFrequencyLed1 register.
        """
        address = CurrentDriverRegisters.PULSE_FREQUENCY_LED1
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("PulseFrequencyLed1")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_pulse_frequency_led1(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the PulseFrequencyLed1 register.

        Parameters
        ----------
        value : int
            Value to write to the PulseFrequencyLed1 register.
        """
        address = CurrentDriverRegisters.PULSE_FREQUENCY_LED1
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("PulseFrequencyLed1")

        return reply

    def read_ramp_led0(self) -> int:
        """
        Reads the contents of the RampLed0 register.

        Returns
        -------
        int
            Value read from the RampLed0 register.
        """
        address = CurrentDriverRegisters.RAMP_LED0
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("RampLed0")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_ramp_led0(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the RampLed0 register.

        Parameters
        ----------
        value : int
            Value to write to the RampLed0 register.
        """
        address = CurrentDriverRegisters.RAMP_LED0
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("RampLed0")

        return reply

    def read_ramp_led1(self) -> int:
        """
        Reads the contents of the RampLed1 register.

        Returns
        -------
        int
            Value read from the RampLed1 register.
        """
        address = CurrentDriverRegisters.RAMP_LED1
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U16))
        if reply is not None and reply.is_error:
            raise HarpReadException("RampLed1")

        # Directly return the payload as it is a primitive type
        return reply.payload

    def write_ramp_led1(self, value: int) -> ReplyHarpMessage | None:
        """
        Writes a value to the RampLed1 register.

        Parameters
        ----------
        value : int
            Value to write to the RampLed1 register.
        """
        address = CurrentDriverRegisters.RAMP_LED1
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U16, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("RampLed1")

        return reply

    def read_ramp_config(self) -> LedRamps:
        """
        Reads the contents of the RampConfig register.

        Returns
        -------
        LedRamps
            Value read from the RampConfig register.
        """
        address = CurrentDriverRegisters.RAMP_CONFIG
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("RampConfig")

        return LedRamps(reply.payload)

    def write_ramp_config(self, value: LedRamps) -> ReplyHarpMessage | None:
        """
        Writes a value to the RampConfig register.

        Parameters
        ----------
        value : LedRamps
            Value to write to the RampConfig register.
        """
        address = CurrentDriverRegisters.RAMP_CONFIG
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("RampConfig")

        return reply

    def read_enable_events(self) -> CurrentDriverEvents:
        """
        Reads the contents of the EnableEvents register.

        Returns
        -------
        CurrentDriverEvents
            Value read from the EnableEvents register.
        """
        address = CurrentDriverRegisters.ENABLE_EVENTS
        reply = self.send(HarpMessage.create(MessageType.READ, address, PayloadType.U8))
        if reply is not None and reply.is_error:
            raise HarpReadException("EnableEvents")

        return CurrentDriverEvents(reply.payload)

    def write_enable_events(self, value: CurrentDriverEvents) -> ReplyHarpMessage | None:
        """
        Writes a value to the EnableEvents register.

        Parameters
        ----------
        value : CurrentDriverEvents
            Value to write to the EnableEvents register.
        """
        address = CurrentDriverRegisters.ENABLE_EVENTS
        reply = self.send(HarpMessage.create(MessageType.WRITE, address, PayloadType.U8, value))
        if reply is not None and reply.is_error:
            raise HarpWriteException("EnableEvents")

        return reply

