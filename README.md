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
```

### Get action state
```python
# Get state for "power_level" action at device "103.47.177.100/29"
# Return a state of action (action-spec)
driver.action_get("103.47.177.100/29", "power_level")
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

```

### Send request to socket server with response
```python
# Send request to socket server and get response at command "list-devices"
# Return a data from socket server
driver.get("list-devices")
```
