import serial
import time
import struct # Required for packing/unpacking length prefixes
import LogicWeave.proto_gen.all_pb2 as all_pb2 # Changed import to the standard protobuf generated file
from LogicWeave.exceptions import DeviceFirmwareError, DeviceResponseError, DeviceConnectionError
from .definitions import GPIOMode, BankVoltage
import serial.tools.list_ports

class PDChannel:
    """Represents a single USB Power Delivery (PD) channel on the device."""
    def __init__(self, controller: 'LogicWeave', channel_num: int):
        """
        Initializes a PDChannel object. Users should get this from LogicWeave.pd_channel().

        Args:
            controller (LogicWeave): The main device controller instance.
            channel_num (int): The USB PD channel number this object will control.
        """
        self._controller = controller
        self.channel_num = channel_num

    def enable_output(self, on: bool):
        """
        Enables or disables the output of this PD channel.

        Args:
            on (bool): True to enable output, False to disable.
        """
        request = all_pb2.UsbPDEnableRequest(channel=self.channel_num, on=on)
        self._controller._send_and_parse(request, "usb_pd_enable_response")

    def read_status(self) -> all_pb2.UsbPDReadResponse:
        """
        Reads the current voltage and current of this USB PD channel.

        Returns:
            all_pb2.UsbPDReadResponse: The response containing voltage and current.
        """
        request = all_pb2.UsbPDReadRequest(channel=self.channel_num)
        response = self._controller._send_and_parse(request, "usb_pd_read_response")
        return response

    def read_source_capability(self, pdo_index: int) -> all_pb2.UsbPDReadPDOResponse:
        """
        Reads a specific Power Data Object (PDO) from this USB PD source,
        describing its power capabilities.

        Args:
            pdo_index (int): The index of the PDO to read.

        Returns:
            all_pb2.UsbPDReadPDOResponse: The response containing the PDO information.
        """
        request = all_pb2.UsbPDReadPDORequest(channel=self.channel_num, index=pdo_index)
        response = self._controller._send_and_parse(request, "usb_pd_read_pdo_response")
        return response

    def request_power(self, voltage_mv: int, current_limit_ma: int, pdo_index: int = 0):
        """
        Requests a specific voltage and current from this USB PD source.

        Args:
            voltage_mv (int): The requested voltage in millivolts.
            current_limit_ma (int): The requested current limit in milliamps.
            pdo_index (int): The index of the PDO to request (defaults to 0).
        """
        request = all_pb2.UsbPDWritePDORequest(
            channel=self.channel_num,
            voltage_mv=voltage_mv,
            current_limit_ma=current_limit_ma,
            pdo_index=pdo_index
        )
        self._controller._send_and_parse(request, "usb_pd_write_pdo_response")

    def __repr__(self):
        return f"<PDChannel channel={self.channel_num}>"

class UART:
    """Represents a configured UART peripheral instance."""
    def __init__(self, controller: 'LogicWeave', instance_num: int, tx_pin: int, rx_pin: int, baud_rate: int):
        """
        Initializes and configures a UART bus. Users should get this from LogicWeave.uart().

        Args:
            controller (LogicWeave): The main device controller instance.
            instance_num (int): The hardware instance number assigned by the controller.
            tx_pin (int): The pin to use for UART TX.
            rx_pin (int): The pin to use for UART RX.
            baud_rate (int): The communication speed in bits per second.
        """
        self._controller = controller
        self._instance_num = instance_num
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.baud_rate = baud_rate

        # Automatically configure the peripheral on the device upon creation
        self._setup()

    def _setup(self):
        """Sends the UART setup command to the device."""
        request = all_pb2.UartSetupRequest(
            instance_num=self._instance_num,
            tx_pin=self.tx_pin,
            rx_pin=self.rx_pin,
            baud_rate=self.baud_rate
        )
        self._controller._send_and_parse(request, "uart_setup_response")

    def write(self, data: bytes, timeout_ms: int = 1000):
        """
        Writes data to this UART bus.

        Args:
            data (bytes): The data to write.
            timeout_ms (int): The timeout for the write operation in milliseconds.
        """
        request = all_pb2.UartWriteRequest(
            instance_num=self._instance_num,
            data=data,
            timeout_ms=timeout_ms
        )
        self._controller._send_and_parse(request, "uart_write_response")

    def read(self, byte_count: int, timeout_ms: int = 1000) -> bytes:
        """
        Reads a number of bytes from this UART bus.

        Args:
            byte_count (int): The number of bytes to read.

        Returns:
            bytes: The data read from the device.
        """
        request = all_pb2.UartReadRequest(
            instance_num=self._instance_num,
            byte_count=byte_count,
            timeout_ms=timeout_ms
        )
        response = self._controller._send_and_parse(request, "uart_read_response")
        return response.data if self._controller.mode == "serial" else b""

    def __repr__(self):
        return f"<UART instance={self._instance_num} tx={self.tx_pin} rx={self.rx_pin} baud={self.baud_rate}>"

class GPIO:
    """Represents a single GPIO pin on the device."""
    def __init__(self, controller: 'LogicWeave', pin: int):
        """
        Initializes a GPIO object. Users should get this from LogicWeave.gpio().

        Args:
            controller (LogicWeave): The main device controller instance.
            pin (int): The GPIO pin number this object will control.
        """
        self._controller = controller
        self.pin = pin
        self.mode = None

    def set_mode(self, mode: all_pb2.Mode):
        """
        Sets the mode (input, output, etc.) for this GPIO pin.

        Args:
            mode (all_pb2.Mode): The desired mode from the protobuf enum.
        """
        request = all_pb2.GPIOModeRequest(gpio_pin=self.pin, mode=mode)
        self._controller._send_and_parse(request, "gpio_mode_response")
        self.mode = mode

    def set_pull(self, state: all_pb2.PinPullState):
        """
        Sets the mode (input, output, etc.) for this GPIO pin.

        Args:
            mode (all_pb2.Mode): The desired mode from the protobuf enum.
        """
        request = all_pb2.GpioPinPullRequest(gpio_pin=self.pin, state=state)
        self._controller._send_and_parse(request, "gpio_pin_pull_response")
        self.pull = state

    def write(self, state: bool):
        """Writes a boolean state (True for HIGH, False for LOW) to this pin."""
        if self.mode != GPIOMode.OUTPUT:
            self.set_mode(GPIOMode.OUTPUT)

        request = all_pb2.GPIOWriteRequest(gpio_pin=self.pin, state=state)
        self._controller._send_and_parse(request, "gpio_write_response")

    def read(self) -> bool:
        """Reads the state of this pin. Returns True for HIGH, False for LOW."""
        if self.mode != GPIOMode.INPUT:
            self.set_mode(GPIOMode.INPUT)

        request = all_pb2.GPIOReadRequest(gpio_pin=self.pin)
        response = self._controller._send_and_parse(request, "gpio_read_response")
        return response.state if self._controller.mode == "serial" else False

    def __repr__(self):
        return f"<GPIO pin={self.pin}>"


class I2C:
    """Represents a configured I2C peripheral instance."""
    def __init__(self, controller: 'LogicWeave', instance_num: int, sda_pin: int, scl_pin: int):
        """
        Initializes and configures an I2C bus. Users should get this from LogicWeave.i2c().

        Args:
            controller (LogicWeave): The main device controller instance.
            instance_num (int): The hardware instance number assigned by the controller.
            sda_pin (int): The pin to use for I2C SDA.
            scl_pin (int): The pin to use for I2C SCL.
        """
        self._controller = controller
        self._instance_num = instance_num
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        
        # Automatically configure the peripheral on the device upon creation
        self._setup()

    def _setup(self):
        """Sends the I2C setup command to the device."""
        request = all_pb2.I2CSetupRequest(
            instance_num=self._instance_num,
            sda_pin=self.sda_pin,
            scl_pin=self.scl_pin
        )
        self._controller._send_and_parse(request, "i2c_setup_response")

    def write(self, device_address: int, data: bytes):
        """Writes data to a specific device on this I2C bus."""
        request = all_pb2.I2CWriteRequest(
            instance_num=self._instance_num,
            device_address=device_address,
            data=data
        )
        self._controller._send_and_parse(request, "i2c_write_response")

    def read(self, device_address: int, byte_count: int) -> bytes:
        """Reads a number of bytes from a specific device on this I2C bus."""
        request = all_pb2.I2CReadRequest(
            instance_num=self._instance_num,
            device_address=device_address,
            byte_count=byte_count
        )
        response = self._controller._send_and_parse(request, "i2c_read_response")
        return response.data if self._controller.mode == "serial" else b""

    def __repr__(self):
        return f"<I2C instance={self._instance_num} sda={self.sda_pin} scl={self.scl_pin}>"

class SPI:
    """Represents a configured SPI peripheral instance."""
    def __init__(self, controller: 'LogicWeave', instance_num: int, sclk_pin: int, mosi_pin: int, miso_pin: int, baud_rate: int, default_cs_pin: int | None = None):
        """
        Initializes and configures an SPI bus. Users should get this from LogicWeave.spi().

        Args:
            controller (LogicWeave): The main device controller instance.
            instance_num (int): The hardware instance number to use.
            sclk_pin (int): The pin for SPI Clock.
            mosi_pin (int): The pin for Master Out Slave In.
            miso_pin (int): The pin for Master In Slave Out.
            baud_rate (int): The communication speed in Hz.
            default_cs_pin (int, optional): Default Chip Select pin to use for transactions.
                                            Can be overridden in read/write calls. Defaults to None.
        """
        self._controller = controller
        self._instance_num = instance_num
        self.sclk_pin = sclk_pin
        self.mosi_pin = mosi_pin
        self.miso_pin = miso_pin
        self.baud_rate = baud_rate
        self._default_cs_pin = default_cs_pin

        # Automatically configure the peripheral on the device upon creation
        self._setup()

    def _setup(self):
        """Sends the SPI setup command to the device."""
        request = all_pb2.SPISetupRequest(
            instance_num=self._instance_num,
            sclk_pin=self.sclk_pin,
            mosi_pin=self.mosi_pin,
            miso_pin=self.miso_pin,
            baud_rate=self.baud_rate
        )
        self._controller._send_and_parse(request, "spi_setup_response")

    def write(self, data: bytes, cs_pin: int | None = None):
        """
        Writes data over this SPI interface.

        Uses the default CS pin if one was set during initialization,
        unless a specific cs_pin is provided here.

        Args:
            data (bytes): The data to write.
            cs_pin (int, optional): The CS pin to use for this transaction, overriding the default.

        Raises:
            ValueError: If no CS pin is provided here and no default was set.
        """
        active_cs_pin = cs_pin if cs_pin is not None else self._default_cs_pin
        if active_cs_pin is None:
            active_cs_pin=0

        request = all_pb2.SPIWriteRequest(
            instance_num=self._instance_num,
            data=data,
            cs_pin=active_cs_pin
        )
        self._controller._send_and_parse(request, "spi_write_response")

    def read(self, byte_count: int, cs_pin: int | None = None, data_to_send: int = 0) -> bytes:
        """
        Reads data from this SPI interface.

        Uses the default CS pin if one was set during initialization,
        unless a specific cs_pin is provided here.

        Args:
            byte_count (int): The number of bytes to read.
            cs_pin (int, optional): The CS pin to use for this transaction, overriding the default.
            data_to_send (int, optional): Dummy data to send to generate clock pulses. Defaults to 0.

        Returns:
            bytes: The data read from the device.

        Raises:
            ValueError: If no CS pin is provided here and no default was set.
        """
        active_cs_pin = cs_pin if cs_pin is not None else self._default_cs_pin
        if active_cs_pin is None:
            active_cs_pin = 0
            #raise ValueError("A Chip Select (CS) pin must be provided either during initialization or in the method call.")

        request = all_pb2.SPIReadRequest(
            instance_num=self._instance_num,
            data=data_to_send,
            cs_pin=active_cs_pin,
            byte_count=byte_count
        )
        response = self._controller._send_and_parse(request, "spi_read_response")
        return response.data if self._controller.mode == "serial" else b""

    def __repr__(self):
        parts = [
            f"<SPI instance={self._instance_num}",
            f"sclk={self.sclk_pin}",
            f"mosi={self.mosi_pin}",
            f"miso={self.miso_pin}"
        ]
        if self._default_cs_pin is not None:
            parts.append(f"default_cs={self._default_cs_pin}")
        return " ".join(parts) + ">"

def _get_device_port():
    vid = 0x1E8B
    pid = 0x0001
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.vid == vid and port.pid == pid:
            return port.device
    return None

class LogicWeave:
    """
    A self-contained, high-level wrapper for communicating with the device over
    a serial connection using the defined protobuf messages. This class handles
    all serial communication and protobuf message handling internally.

    Includes a 'file' mode to log serialized commands to a file instead of
    sending them over serial.
    """

    def __init__(self, port=None, baudrate=115200, timeout=1, write_delay=0, mode="serial", output_file=None, **kwargs):
        """
        Initializes the Device and establishes a serial connection or prepares for file logging.

        Args:
            port (str, optional): The serial port (e.g., 'COM3' or '/dev/ttyUSB0').
                                  Required if mode is "serial".
            baudrate (int): The serial communication speed.
            timeout (int): The read timeout for the serial connection in seconds.
            write_delay (float): The delay in seconds after a write operation (only for serial mode).
            mode (str): The operational mode: "serial" for actual communication,
                        "file" to write commands to a file. Defaults to "serial".
            output_file (str, optional): The path to the file where commands will be logged
                                         if mode is "file". Required if mode is "file".
            **kwargs: Additional arguments for pyserial's Serial constructor.
        """
        self.mode = mode
        self.output_file = output_file
        self.ser = None
        self.file_handle = None  # New attribute for file handle when in 'file' mode
        self.write_delay = write_delay

        if self.mode == "serial":
            if not port:
                port = _get_device_port()
                if not port:
                    raise ValueError("Port must be specified when mode is 'serial'.")
            try:
                self.ser = serial.Serial(
                    port=port,
                    baudrate=baudrate,
                    timeout=timeout,
                    **kwargs
                )
            except serial.SerialException as e:
                raise DeviceConnectionError(f"Failed to connect to {port}: {e}") from e
        elif self.mode == "file":
            if not self.output_file:
                raise ValueError("output_file must be specified when mode is 'file'.")
            try:
                # Open in append binary mode, so multiple commands can be logged
                self.file_handle = open(self.output_file, "ab")
            except IOError as e:
                raise DeviceConnectionError(f"Failed to open output file {self.output_file}: {e}") from e
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'serial' or 'file'.")

        # This map is used to construct the AppMessage for sending.
        # Keys are the request message classes, values are the corresponding
        # field names in the AppMessage 'kind' oneof group.
        # Note: With regular protobuf, you directly assign to the oneof field.
        self._request_to_field_map = {
            all_pb2.GPIOModeRequest: "gpio_mode_request",
            all_pb2.GPIOWriteRequest: "gpio_write_request",
            all_pb2.UsbBootloaderRequest: "usb_bootloader_request",
            all_pb2.GPIOReadRequest: "gpio_read_request",
            all_pb2.EchoMessage: "echo_message",
            all_pb2.I2CSetupRequest: "i2c_setup_request",
            all_pb2.I2CWriteRequest: "i2c_write_request",
            all_pb2.I2CReadRequest: "i2c_read_request",
            all_pb2.SPISetupRequest: "spi_setup_request",
            all_pb2.SPIReadRequest: "spi_read_request",
            all_pb2.SPIWriteRequest: "spi_write_request",
            all_pb2.UsbPDReadRequest: "usb_pd_read_request",
            all_pb2.UsbPDReadPDORequest: "usb_pd_read_pdo_request",
            all_pb2.UsbPDWritePDORequest: "usb_pd_write_pdo_request",
            all_pb2.WriteTextRequest: "write_text_request",
            all_pb2.UsbPDEnableRequest: "usb_pd_enable_request",
            all_pb2.ClearScreenRequest: "clear_screen_request",
            all_pb2.RefreshScreenRequest: "refresh_screen_request",
            all_pb2.FirmwareInfoRequest: "firmware_info_request",
            all_pb2.SoftSPIWriteRequest: "soft_spi_write_request",
            all_pb2.WriteBankVoltageRequest: "write_bank_voltage_request",
            all_pb2.UartSetupRequest: "uart_setup_request", # ADDED
            all_pb2.UartReadRequest: "uart_read_request",   # ADDED
            all_pb2.UartWriteRequest: "uart_write_request"  # ADDED
        }

        # Map for response field names to their corresponding message classes.
        # Used to create dummy responses when in 'file' mode.
        self._response_field_to_class_map = {
            "firmware_info_response": all_pb2.FirmwareInfoResponse,
            "echo_message": all_pb2.EchoMessage, # EchoMessage can be both request and response
            "gpio_read_response": all_pb2.GPIOReadResponse,
            "i2c_read_response": all_pb2.I2CReadResponse,
            "spi_read_response": all_pb2.SPIReadResponse,
            "usb_pd_read_response": all_pb2.UsbPDReadResponse,
            "usb_pd_read_pdo_response": all_pb2.UsbPDReadPDOResponse,
            "uart_read_response": all_pb2.UartReadResponse, # ADDED
            # For responses that are typically just Empty messages (assuming 'Empty' exists in messages_pb2.py)
            "empty": all_pb2.Empty,
            "gpio_write_response": all_pb2.Empty,
            "i2c_setup_response": all_pb2.Empty,
            "i2c_write_response": all_pb2.Empty,
            "spi_setup_response": all_pb2.Empty,
            "spi_write_response": all_pb2.Empty,
            "soft_spi_write_response": all_pb2.Empty,
            "usb_pd_enable_response": all_pb2.Empty,
            "usb_pd_write_pdo_response": all_pb2.Empty,
            "gpio_mode_response": all_pb2.Empty,
            "write_text_response": all_pb2.Empty,
            "clear_screen_response": all_pb2.Empty,
            "refresh_screen_response": all_pb2.Empty,
            "usb_bootloader_response": all_pb2.Empty,
            "write_bank_voltage_response": all_pb2.Empty,
            "uart_setup_response": all_pb2.Empty, # ADDED
            "uart_write_response": all_pb2.Empty, # ADDED
            "error_response": all_pb2.ErrorResponse, # For device-side error messages
        }

    def pd_channel(self, channel_num: int) -> 'PDChannel':
        """
        Gets a PDChannel object to control a specific USB PD channel.

        Args:
            channel_num (int): The USB PD channel number (e.g., 0 or 1).

        Returns:
            PDChannel: An object for interacting with this USB PD channel.
        """
        return PDChannel(self, channel_num)

    def uart(self, instance_num: int, tx_pin: int, rx_pin: int, baud_rate: int = 115200) -> 'UART':
        """
        Initializes a UART bus on the specified pins for a given hardware instance.

        Args:
            instance_num (int): The hardware instance number to use (e.g., 0 for UART0).
            tx_pin (int): The pin to use for UART TX.
            rx_pin (int): The pin to use for UART RX.
            baud_rate (int): The communication speed in bits per second. Defaults to 115200.

        Returns:
            UART: An object for interacting with this UART bus.
        """
        return UART(self, instance_num, tx_pin, rx_pin, baud_rate)

    def gpio(self, pin: int) -> GPIO:
        """
        Gets a GPIO object to control a single pin. This method is unchanged.
        """
        return GPIO(self, pin)

    def i2c(self, instance_num: int, sda_pin: int, scl_pin: int) -> I2C:
        """
        Initializes an I2C bus on the specified pins for a given hardware instance.

        Args:
            instance_num (int): The hardware instance number to use (e.g., 0 for I2C0).
            sda_pin (int): The pin to use for I2C SDA.
            scl_pin (int): The pin to use for I2C SCL.

        Returns:
            I2C: An object for interacting with this I2C bus.
        """
        return I2C(self, instance_num, sda_pin, scl_pin)

    def spi(self, instance_num: int, sclk_pin: int, mosi_pin: int, miso_pin: int, baud_rate: int = 1000000, default_cs_pin: int | None = None) -> SPI:
        """
        Initializes an SPI bus on the specified pins for a given hardware instance.

        Args:
            instance_num (int): The hardware instance number to use (e.g., 1 for SPI1).
            sclk_pin (int): The pin for SPI Clock.
            mosi_pin (int): The pin for Master Out Slave In.
            miso_pin (int): The pin for Master In Slave Out.
            baud_rate (int): The communication speed in Hz. Defaults to 1 MHz.
            default_cs_pin (int, optional): Sets a default Chip Select pin for the SPI object.

        Returns:
            SPI: An object for interacting with this SPI bus.
        """
        return SPI(self, instance_num, sclk_pin, mosi_pin, miso_pin, baud_rate, default_cs_pin)

    def _execute_transaction(self, specific_message_payload) -> all_pb2.AppMessage | None:
        """
        Handles the full send-and-receive cycle for a protobuf message.
        It wraps the payload, sends it (serial mode), and returns the parsed AppMessage response.
        In 'file' mode, it writes the length-prefixed message to the file and returns None.

        Args:
            specific_message_payload (google.protobuf.message.Message): The specific protobuf
                                                                         request message to send.

        Returns:
            messages_pb2.AppMessage: The parsed AppMessage response received from the device (serial mode).
            None: If operating in 'file' mode (no actual response from a device).

        Raises:
            DeviceConnectionError: If the serial port/output file is not open.
            ValueError: If the specific_message_payload type is not supported
                        or if message is too large for the 2-byte prefix.
            DeviceFirmwareError: If there's an error parsing the response bytes (serial mode).
            DeviceResponseError: If an incomplete response is received (serial mode).
        """
        message_type = type(specific_message_payload)
        field_name = self._request_to_field_map.get(message_type)

        if not field_name:
            raise ValueError(f"Unsupported message type: {message_type.__name__}")

        # Wrap the specific payload into the main AppMessage container
        app_message_request = all_pb2.AppMessage()
        
        # --- THE CRUCIAL CHANGE FOR REGULAR PROTOBUF ONEOF ASSIGNMENT ---
        # 1. Get the accessor for the oneof field (which returns a sub-message object).
        # 2. Use CopyFrom to populate that sub-message object with your specific payload.
        getattr(app_message_request, field_name).CopyFrom(specific_message_payload)
        
        # Serialize the AppMessage request
        request_bytes = app_message_request.SerializeToString() # Use regular protobuf serialization
        length = len(request_bytes)

        # Ensure the message length fits within a 2-byte unsigned integer (max 65535)
        if length > 65535:
            raise ValueError(f"Message too large for 2-byte prefix: {length} bytes. Max is 65535.")

        # Pack the length into 2 bytes, big-endian format
        length_prefix = struct.pack(">H", length) # '>H' means big-endian unsigned short

        if self.mode == "serial":
            if not self.ser or not self.ser.is_open:
                raise DeviceConnectionError("Serial port is not open.")

            # Clear input buffer to ensure we only read the response to this request
            self.ser.reset_input_buffer()
            
            # Send the 2-byte length prefix followed by the serialized request bytes
            self.ser.write(length_prefix + request_bytes)

            # This delay gives the device time to process the request and begin its response.
            if self.write_delay > 0:
                time.sleep(self.write_delay)

            # --- Read Response (assuming device sends a 1-byte length prefix for its responses) ---
            # Read the 1-byte length prefix of the response from the device
            response_length_byte = self.ser.read(1)
            if not response_length_byte:
                # If no length byte is received within timeout, return an empty AppMessage
                # This could indicate a timeout or a device that doesn't always respond.
                return all_pb2.AppMessage() # Return an empty AppMessage instance
            
            response_length = response_length_byte[0] # Convert the single byte to an integer

            # Read the actual response message bytes based on the received length
            response_bytes = self.ser.read(response_length)
            
            if len(response_bytes) != response_length:
                # This indicates an incomplete read, possibly due to timeout or data corruption
                raise DeviceResponseError(f"Incomplete response received. Expected {response_length} bytes, got {len(response_bytes)}.")

            try:
                # Parse the received response bytes into an AppMessage
                parsed_response = all_pb2.AppMessage()
                parsed_response.ParseFromString(response_bytes) # Use regular protobuf deserialization
                return parsed_response
            except Exception as e:
                # If protobuf parsing fails, wrap it in a firmware error for clarity
                raise DeviceFirmwareError(f"Client-side parse error: {e}. Raw data: {response_bytes.hex()}")

        elif self.mode == "file":
            if not self.file_handle:
                raise DeviceConnectionError("Output file is not open.")
            
            # Write the 2-byte length prefix to the file
            self.file_handle.write(length_prefix)
            # Write the serialized request bytes to the file
            self.file_handle.write(request_bytes)
            
            # In file mode, there is no actual device response, so return None
            return None

    def _send_and_parse(self, request_payload, expected_response_field: str):
        """
        A wrapper around _execute_transaction that validates the response type
        and handles generic error responses from the device (serial mode)
        or generates a dummy response (file mode).

        Args:
            request_payload (google.protobuf.message.Message): The specific protobuf
                                                                 request message to send.
            expected_response_field (str): The name of the expected field in
                                           the AppMessage 'kind' oneof group
                                           for a successful response.

        Returns:
            google.protobuf.message.Message: The specific protobuf response message payload.

        Raises:
            DeviceFirmwareError: If the device returns an error response (serial mode).
            DeviceResponseError: If the received response type does not match
                                 the expected type (serial mode).
            RuntimeError: If a dummy response cannot be generated in file mode
                          (should not happen if _response_field_to_class_map is complete).
        """
        response_app_msg = self._execute_transaction(request_payload)

        if self.mode == "file":
            # If in 'file' mode, _execute_transaction returns None, as there's no actual response.
            # We then return a default-constructed instance of the expected response type
            # to maintain the high-level API's return type consistency.
            response_class = self._response_field_to_class_map.get(expected_response_field)
            if response_class:
                return response_class() # Return an empty/default instance of the expected response message
            else:
                # This case indicates an unmapped response field. It should ideally not occur.
                raise RuntimeError(f"Cannot generate dummy response for unknown type: '{expected_response_field}' in file mode.")

        # --- Original serial mode logic continues below ---
        # With regular protobuf, to determine which oneof field is set, you use HasField
        # and then directly access the field.
        response_field = response_app_msg.WhichOneof("kind") # "kind" is the name of the oneof group

        # Check for a generic error response from the device
        if response_field == "error_response":
            raise DeviceFirmwareError(f"Device error: {response_app_msg.error_response.message}")
        
        # Validate that the received response type matches the expected type
        if response_field != expected_response_field:
            raise DeviceResponseError(expected=expected_response_field, received=response_field)

        # Access the payload directly using the determined field name
        response_payload = getattr(response_app_msg, response_field)
        return response_payload

    def close(self):
        """Closes the serial connection or output file if open."""
        if self.mode == "serial" and self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial connection closed.")
        elif self.mode == "file" and self.file_handle:
            self.file_handle.close()
            self.file_handle = None # Clear the handle
            print(f"Output file '{self.output_file}' closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # --- High-Level API Methods ---

    def read_firmware_info(self) -> all_pb2.FirmwareInfoResponse:
        """
        Reads firmware version and build information from the device.
        In 'file' mode, logs the request and returns a default FirmwareInfoResponse.
        """
        request = all_pb2.FirmwareInfoRequest(info=1)
        response = self._send_and_parse(request, "firmware_info_response")
        return response

    def write_read_echo(self, message: str) -> str:
        """
        Sends a message to the device and returns its echoed response.
        In 'file' mode, logs the request and returns an empty string.
        """
        request = all_pb2.EchoMessage(message=message)
        response = self._send_and_parse(request, "echo_message")
        return response.message if self.mode == "serial" else "" # Return empty string for file mode

    def write_bank_voltage(self, bank: int, voltage: all_pb2.BankVoltage):
        """
        Writes the desired voltage for a specific power bank.
        In 'file' mode, logs the request.
        """
        request = all_pb2.WriteBankVoltageRequest(
            bank=bank,
            voltage=voltage
        )
        self._send_and_parse(request, "write_bank_voltage_response")

    # --- Screen Methods ---

    def write_text(self, text: str, x: int = 0, y: int = 0):
        """
        Writes text to the device's screen at a specified position.
        In 'file' mode, logs the request.
        """
        request = all_pb2.WriteTextRequest(text=text, x=x, y=y)
        self._send_and_parse(request, "write_text_response")

    def write_clear_screen(self):
        """
        Writes a command to clear the device's screen.
        In 'file' mode, logs the request.
        """
        request = all_pb2.ClearScreenRequest()
        self._send_and_parse(request, "clear_screen_response")
        
    def write_refresh_screen(self):
        """
        Writes a command to refresh the device's screen to show updates.
        In 'file' mode, logs the request.
        """
        request = all_pb2.RefreshScreenRequest()
        self._send_and_parse(request, "refresh_screen_response") 

    def write_bootloader_request(self):
        """
        Writes a request for the device to enter its USB bootloader mode.
        After this command, the device typically reboots into bootloader and
        the serial connection will likely be lost.
        In 'file' mode, logs the request.
        """
        request = all_pb2.UsbBootloaderRequest(val=1)
        self._send_and_parse(request, "usb_bootloader_response")

# Utility function to read and parse commands from the generated binary file
def read_commands_from_file(file_path: str) -> list[all_pb2.AppMessage]:
    """
    Reads length-prefixed AppMessage commands from a binary file.
    Each message is expected to be prefixed with a 2-byte length.
    """
    commands = []
    with open(file_path, "rb") as f:
        while True:
            # Read the 2-byte length prefix
            length_prefix = f.read(2)
            if not length_prefix:
                break  # End of file

            # Unpack the 2-byte length (unsigned short, big-endian)
            length = struct.unpack(">H", length_prefix)[0]

            # Read the actual serialized AppMessage data
            serialized_data = f.read(length)
            if len(serialized_data) != length:
                raise EOFError(f"Incomplete message data in file '{file_path}'. Expected {length} bytes, got {len(serialized_data)}.")

            try:
                # Parse the data back into an AppMessage
                command_message = all_pb2.AppMessage() # Create an instance
                command_message.ParseFromString(serialized_data) # Parse the bytes into it
                commands.append(command_message)
            except Exception as e:
                print(f"Warning: Could not parse message from file: {e}")
    return commands