import select
import socket
import threading
import time
from dataclasses import dataclass

import msgpack

from src.driver_khawasu.common.device import Device


@dataclass
class Subscribe:
    address: str
    method_name: str
    handler: any


class LogicalDriver:
    current_supported_version = 0

    def __init__(self, addr, port):
        self.sem_in_packets = threading.Semaphore(value=1)
        self.sem_out_packets = threading.Semaphore(value=1)
        self.sem_idx = threading.Semaphore(value=1)
        self.incoming_packets = {}
        self.outcoming_packets = []
        self.subscribe_packets = {}
        self.subscribes = {}
        self.devices = []
        self.idx_buf = 0
        self.DEBUG_MODE = False

        self.sock = socket.socket()
        self.sock.connect((addr, port))
        self.sock.settimeout(15)

        self.socket_thread_handle = threading.Thread(target=self.socket_thread)
        self.socket_thread_handle.start()

        version = self.get("version")

        if version is None:
            raise Exception("Version not found")

        self.version = int(version["version"])

        if self.version > self.current_supported_version:
            print(f"WARNING! Version from server ({self.version}) is higher than supported "
                  f"({self.current_supported_version}). Errors may occur due to the addition of new features.")

    def get(self, method_name, args=None):
        """
        Request to Khawasu server with method_name and args and return response
        """
        if args is None:
            args = {}
        if not self.sem_idx.acquire(timeout=15):
            raise IOError("Semaphore not released")

        self.idx_buf += 1
        cur_idx = self.idx_buf + 0
        self.sem_idx.release()

        self.send(method_name, args, cur_idx)

        start_time = time.time()
        while cur_idx not in self.incoming_packets:
            if time.time() - start_time > 15:
                raise IOError("Response timeout")

        return self.incoming_packets.pop(cur_idx)["data"]

    def get_device_by_address(self, address: str) -> Device | None:
        for dev in self.get_devices():
            if dev.address == address:
                return dev

        return None

    def get_devices_force(self) -> list[Device]:
        """Return devices list by directly request to khawasu server"""
        self.devices = Device.get_all(self)
        return self.devices

    def get_devices(self) -> list[Device]:
        """Return devices list by internal cache"""
        return self.get_devices_force() if self.devices == None else self.devices

    def execute(self, address, action_name, row_data: bytes):
        """Execute action on device with row bytes as data"""
        self.send("action", {"action_name": action_name, "address": address, "data": row_data}, 0)

    def action_get(self, address, action_name):
        """Get action state from device"""
        return self.get("action_fetch", {"action_name": action_name, "address": address})

    def subscribe(self, address, action_name, period, duration, handler):
        """Subscribe to action
        :param address: Address of device
        :param action_name: Name of subscribe action on device
        :param period: Latency between requests for data (in milliseconds)
        :param duration: Subscription time (in seconds)
        :param handler: Function for callback"""
        try:
            answ = self.get("action_subscribe_new",
                            {"address": address, "action_name": action_name, "period": period, "duration": duration})
        except:
            return {"data": {"status": "socket-error"}, "method": "action_subscribe_new"}

        if "error" in answ:
            return {"data": {"status": "webhook-add-error"}, "method": "action_subscribe"}

        self.subscribes[int(answ["id"])] = Subscribe(address, action_name, handler)

    def on_subscribe_response(self, msg):
        subscribe_data = self.subscribes[int(msg["id"])]
        subscribe_data.handler(subscribe_data.address, subscribe_data.method_name, msg)

    def send(self, method_name, args=None, id=0):
        if args is None:
            args = {}

        if self.sem_out_packets.acquire(timeout=15):
            self.outcoming_packets.append({"method_name": method_name, "data": args, "id": id})
            self.sem_out_packets.release()
        else:
            raise IOError("Semaphore not released")

    def socket_thread(self):
        self.sock.setblocking(False)
        while True:
            ready = select.select([self.sock], [self.sock], [], 1)
            if ready[1] and len(self.outcoming_packets) > 0 and self.sem_out_packets.acquire(blocking=False):
                packet_data = self.outcoming_packets.pop()
                self.sem_out_packets.release()

                _bytes = msgpack.packb(packet_data)
                self.sock.send(len(_bytes).to_bytes(4, 'little') + _bytes)

                if self.DEBUG_MODE:
                    print("SEND", packet_data)

            if ready[0] and self.sem_in_packets.acquire(blocking=False):
                msg = msgpack.unpackb(self.sock.recv(int.from_bytes(self.sock.recv(4), "little")))

                if self.DEBUG_MODE:
                    print("RECV", msg)

                if msg["method"] == "action_subscribe":
                    self.on_subscribe_response(msg)
                elif msg["id"] != 0:
                    self.incoming_packets[msg["id"]] = {**msg, "recv_time": time.time()}

                self.sem_in_packets.release()

            time.sleep(0)
