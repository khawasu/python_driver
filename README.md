![PyPI](https://img.shields.io/pypi/v/driver-khawasu)

# Description
Provides a simple usage for Khawasu socket-server.

# How to install

Just make it: `pip install driver-khawasu`
# Examples:
### Create new Driver Instance
```python
from driver_khawasu.driver import LogicalDriver

# Create instance and connect to server
driver = LogicalDriver("127.0.0.1", 1234)
```

### Execute action
```python
# Execute "power_level" action for device "103.47.177.100/29" with args: b'\125'
# No response returned
driver.execute("103.47.177.100/29", "power_level", bytes([125]))

# Or 
# (note that the arguments here are bytes, and the special data that this Action accepts)
driver.get_device_by_address("103.47.177.100/29").execute("power_level", 125 / 255)
```

### Get action state
```python
# Get state for "power_level" action at device "103.47.177.100/29"
# Return a state of action (action-spec)
driver.action_get("103.47.177.100/29", "power_level")

# Or
# Returns special data, not bytes
# (see item "How to do anything with the device")
driver.get_device_by_address("103.47.177.100/29").get("power_level") # returned float [0, 1]
```

### Subscribe to action
```python
# Action handler for subscribe
def action_handler(address, method_name, data):
    print(  f"Wow, {method_name} was executed on" 
            f"{address} and returned {len(data)} bytes!")

# Subscribe to device "103.47.177.100/29" at action "power_level" with:
# duration: 60 sec
# timeout: 0 sec (for immediate subscribe)
# No response returned
# Will call action_handler when the answer comes
driver.subscribe("103.47.177.100/29", "power_level", 0, 60, action_handler)

# For subscribe on duration - 60 sec and timeout - 1 sec:
driver.subscribe("103.47.177.100/29", "power_level", 1000, 60, action_handler)

# OR
driver.get_device_by_address("103.47.177.100/29").subscribe("power_level", 1000, 60, action_handler)

```

### Send request to socket server with response
```python
# Send request to socket server and get response at command "list-devices"
# Return a data from socket server
driver.get("list-devices")
```

# Class Device
## Get list of devices
```python
# Functions return List[Device]
driver.get_devices() # Get devices from khawasu server or internal cache
driver.get_devices_force() # Get devices from khawasu server
```

## Get device by address
```python
# Function return Device or None (if not found)
driver.get_device_by_address("103.47.177.100/29") # Get device by address
```

## How to do anything with the device
```python
# Get device by address
dev = driver.get_device_by_address("103.47.177.100/29")

# ActionType.TOGGLE
dev.get("power_state") # Return bool
dev.execute("power_state", True) # Specify bool in arg

# ActionType.RANGE
dev.get("power_level") # Return float [0, 1]
dev.execute("power_level", 0.41) # Specify float in arg

# ActionType.TEMPERATURE
dev.get("temperature") # Return float temperature in celsius

# ActionType.HUMIDITY
dev.get("humudity") # Return float [0, 1]
```

# Class Action
Has methods to convert special objects to bytes and back: `format_bytes_to_data(..)` and `format_data_to_bytes(..)`

```python 
Action(name, dev_class: int)
```

```python
class ActionType(Enum):
    UNKNOWN = 0
    IMMEDIATE = 1
    TOGGLE = 2
    RANGE = 3
    LABEL = 4
    TEMPERATURE = 5
    HUMIDITY = 6
```
