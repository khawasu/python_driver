from enum import Enum
from typing import Any


class ActionType(Enum):
    UNKNOWN = 0
    IMMEDIATE = 1
    TOGGLE = 2
    RANGE = 3
    LABEL = 4
    TEMPERATURE = 5
    HUMIDITY = 6


class Action:
    def __init__(self, name: str, type: int):
        self.name = name
        self.type = ActionType(type)

    def format_args_to_bytes(self, data: Any):
        # Row bytes
        if self.type == ActionType.IMMEDIATE:
            return bytes([data])

        # 1 or 0
        if self.type == ActionType.TOGGLE:
            return bytes([int(bool(data))])

        # byte from 0 to 255
        if self.type == ActionType.RANGE:
            return bytes([int(float(data) * 255)])

        # Does not matter
        if self.type == ActionType.LABEL:
            return bytes([data])

        if self.type == ActionType.TEMPERATURE:
            return bytes([data])

        if self.type == ActionType.HUMIDITY:
            return bytes([data])

        raise NotImplementedError(str(self.type))

    def format_bytes_to_data(self, row_data: bytes) -> Any:
        # Row bytes
        if self.type == ActionType.IMMEDIATE:
            return row_data

        # Bool value
        if self.type == ActionType.TOGGLE:
            return bool(row_data[0] if len(row_data) > 0 else 0)

        # float from 0 to 1
        if self.type == ActionType.RANGE:
            return int.from_bytes(row_data[:1], byteorder='little') / 255

        # Temperature (float)
        if self.type == ActionType.TEMPERATURE:
            return int.from_bytes(row_data[:2] if len(row_data) >= 2 else bytes(2), byteorder='little') / 256

        # Humidity percent (float)
        if self.type == ActionType.HUMIDITY:
            return int.from_bytes(row_data[:2] if len(row_data) >= 2 else bytes(2), byteorder='little') / 256

        raise NotImplementedError(str(self.type))


