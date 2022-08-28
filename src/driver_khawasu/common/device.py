from __future__ import annotations
from enum import Enum
from typing import Any

from src.driver_khawasu import driver
from src.driver_khawasu.common.action import Action, ActionType


class DeviceType(Enum):
    UNKNOWN = 0
    BUTTON = 1
    RELAY = 2
    TEMPERATURE_SENSOR = 3
    TEMP_HUM_SENSOR = 4
    CONTROLLER = 5
    PC2LOGICAL_ADAPTER = 6
    LUA_INTERPRETER = 7
    LED_1_DIM = 8


class Device:
    def __init__(self, row, khawasu_inst: driver.LogicalDriver):
        self.actions = [Action(name, type) for name, type in row["actions"].items()]
        self.address = row["address"]
        self.attribs = row["attribs"]
        self.dev_class = row["dev_class"]
        self.type = DeviceType(int(self.dev_class))
        self.group = row["group_name"]
        self.name = row["name"]
        self.khawasu_inst = khawasu_inst

    def execute(self, action_name: str, data: Any) -> bool:
        """Execute action
        :param action_name: Name of execute Action
        :param data: Specified data for this action type. Please read this in common/action.py in format_args_to_bytes"""
        for action in self.actions:
            if action.name != action_name:
                continue

            self.khawasu_inst.execute(self.address, action_name, action.format_args_to_bytes(data))
            return True

        return False

    def get(self, action_name: str) -> Any:
        """Request action state
        :param action_name: Name of request Action"""
        for action in self.actions:
            if action.name != action_name:
                continue
            data = self.khawasu_inst.action_get(self.address, action_name)

            if "status" in data:
                print("Error in action fetch: ", data["status"])
                return None

            result = action.format_bytes_to_data(data["data"])

            return result

        return None

    def subscribe(self, action_name: str, period: int, duration: int, handler) -> Any:
        """Subscribe to action device
        :param action_name: Name of subscribe action on device
        :param period: Latency between requests for data (in milliseconds)
        :param duration: Subscription time (in seconds)
        :param handler: Function for callback"""

        for action in self.actions:
            if action != action_name:
                continue

            self.khawasu_inst.subscribe(self.address, action_name, period, duration, handler)
            return False

        return True

    @classmethod
    def get_all(cls, khawasu_inst: driver.LogicalDriver) -> list[Device]:
        return [cls(dev, khawasu_inst) for dev in khawasu_inst.get("list-devices")]
