# SPDX-FileCopyrightText: 2022-present Inria
# SPDX-FileCopyrightText: 2022-present Alexandre Abadie <alexandre.abadie@inria.fr>
# SPDX-FileCopyrightText: 2025-present Geovane Fedrecheski <geovane.fedrecheski@inria.fr>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Serial interface."""

import logging
import sys
import threading
import time
from typing import Callable

import serial
from serial.tools import list_ports

SERIAL_PAYLOAD_CHUNK_SIZE = 64
SERIAL_PAYLOAD_CHUNK_SIZE_WITH_TRIGGER_BYTE = 63
SERIAL_PAYLOAD_CHUNK_DELAY = 0.003  # 2 ms
SERIAL_DEFAULT_PORT = "/dev/ttyACM0"
SERIAL_DEFAULT_BAUDRATE = 1_000_000
# SERIAL_DEFAULT_BAUDRATE = 460_800


def get_default_port():
    """Return default serial port."""
    ports = [port for port in list_ports.comports()]
    if sys.platform != "win32":
        ports = sorted([port for port in ports if "J-Link" == port.product])
    if not ports:
        return SERIAL_DEFAULT_PORT
    # return first JLink port available
    return ports[0].device


class SerialInterfaceException(Exception):
    """Exception raised when serial port is disconnected."""


class SerialInterface(threading.Thread):
    """Bidirectional serial interface."""

    def __init__(self, port: str, baudrate: int, callback: Callable):
        self.lock = threading.Lock()
        self.callback = callback
        self.serial = serial.Serial(port, baudrate)
        super().__init__(daemon=True)
        self._logger = logging.getLogger(__name__)
        self.start()
        self._logger.info("Serial port thread started")

    def run(self):
        """Listen continuously at each byte received on serial."""
        self.serial.flush()
        try:
            while 1:
                try:
                    byte = self.serial.read(1)
                except (TypeError, serial.serialutil.SerialException):
                    byte = None
                if byte is None:
                    self._logger.info("Serial port disconnected")
                    break
                self.callback(byte)
        except serial.serialutil.PortNotOpenError as exc:
            self._logger.error(f"{exc}")
            raise SerialInterfaceException(f"{exc}") from exc
        except serial.serialutil.SerialException as exc:
            self._logger.error(f"{exc}")
            raise SerialInterfaceException(f"{exc}") from exc

    def stop(self):
        self.serial.close()
        self.join()

    def write_chunked(self, bytes_):
        """Write bytes on serial using the chunked strategy. (deprecated)"""
        # Send 64 bytes at a time
        pos = 0
        while pos < len(bytes_):
            chunk_end = min(pos + SERIAL_PAYLOAD_CHUNK_SIZE, len(bytes_))
            self.serial.write(bytes_[pos:chunk_end])
            self.serial.flush()
            pos = chunk_end
            if pos < len(bytes_):  # Only sleep if there are more chunks
                time.sleep(SERIAL_PAYLOAD_CHUNK_DELAY)

    def write_trigger_byte(self, bytes_):
        """Write bytes on serial using the trigger byte strategy. (deprecated)"""
        self.serial.write(bytes_[0:1])
        time.sleep(
            0.0001
        )  # 100 us -- this time is important because of the trigger byte timeout on the nRF side
        self.serial.write(bytes_[1:])
        self.serial.flush()
        time.sleep(SERIAL_PAYLOAD_CHUNK_DELAY)

    def write_chunked_with_trigger_byte(self, bytes_):
        """Write bytes on serial using the chunked strategy with trigger byte."""
        # Send 64 bytes at a time
        pos = 0
        while pos < len(bytes_):
            # send trigger byte
            trigger_byte = bytes_[pos : pos + 1]
            self.serial.write(trigger_byte)
            time.sleep(
                0.0001
            )  # 100 us -- this time is important because of the trigger byte timeout on the nRF side
            pos += 1

            # send chunk
            chunk_end = min(pos + SERIAL_PAYLOAD_CHUNK_SIZE_WITH_TRIGGER_BYTE, len(bytes_))
            self.serial.write(bytes_[pos:chunk_end])
            self.serial.flush()
            pos = chunk_end

            # sleep to force a delay between chunks (or between calls to this function)
            time.sleep(SERIAL_PAYLOAD_CHUNK_DELAY)

    def write(self, bytes_):
        """Write bytes on serial."""
        self.write_chunked_with_trigger_byte(bytes_)
