# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyflowercare']

package_data = \
{'': ['*']}

install_requires = \
['bleak>=0.21.0,<0.22.0', 'pydantic>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'pyflowercare',
    'version': '0.2.3',
    'description': 'Python library for communicating with FlowerCare (Xiaomi MiFlora) Bluetooth plant sensors',
    'long_description': '# PyFlowerCare\n\nA Python library for communicating with FlowerCare (Xiaomi MiFlora) Bluetooth plant sensors.\n\n## Features\n\n- **Device Discovery**: Scan and discover FlowerCare devices via Bluetooth Low Energy\n- **Real-time Sensor Data**: Read temperature, brightness, soil moisture, and conductivity\n- **Historical Data**: Access stored historical measurements from the device\n- **Device Management**: Connect, disconnect, and manage multiple devices\n- **Async Support**: Full asyncio support for non-blocking operations\n- **Error Handling**: Comprehensive exception handling with meaningful error messages\n\n## Installation\n\n```bash\npip install pyflowercare\n```\n\n## Requirements\n\n- Python 3.9+\n- Bluetooth Low Energy support\n- Linux/macOS/Windows with Bluetooth adapter\n\n## Quick Start\n\n### Basic Usage\n\n```python\nimport asyncio\nfrom pyflowercare import FlowerCareScanner\n\nasync def main():\n    scanner = FlowerCareScanner()\n    \n    # Scan for devices\n    devices = await scanner.scan_for_devices(timeout=10.0)\n    \n    if devices:\n        device = devices[0]\n        \n        # Connect and read data\n        async with device:\n            sensor_data = await device.read_sensor_data()\n            print(f"Temperature: {sensor_data.temperature}°C")\n            print(f"Brightness: {sensor_data.brightness} lux")\n            print(f"Moisture: {sensor_data.moisture}%")\n            print(f"Conductivity: {sensor_data.conductivity} µS/cm")\n\nasyncio.run(main())\n```\n\n### Device Information\n\n```python\nasync with device:\n    info = await device.get_device_info()\n    print(f"Device: {info.name}")\n    print(f"MAC: {info.mac_address}")\n    print(f"Battery: {info.battery_level}%")\n    print(f"Firmware: {info.firmware_version}")\n```\n\n### Historical Data\n\n```python\nasync with device:\n    history = await device.get_historical_data()\n    \n    for entry in history[-5:]:  # Last 5 entries\n        print(f"{entry.timestamp}: {entry.sensor_data}")\n```\n\n### Continuous Monitoring\n\n```python\nimport asyncio\nfrom datetime import datetime\nfrom pyflowercare import FlowerCareScanner\n\nasync def monitor_device(device):\n    while True:\n        try:\n            async with device:\n                while True:\n                    data = await device.read_sensor_data()\n                    timestamp = datetime.now().strftime("%H:%M:%S")\n                    print(f"[{timestamp}] {data}")\n                    await asyncio.sleep(60)  # Read every minute\n        except Exception as e:\n            print(f"Error: {e}")\n            await asyncio.sleep(5)  # Retry after 5 seconds\n\nasync def main():\n    scanner = FlowerCareScanner()\n    devices = await scanner.scan_for_devices()\n    \n    # Monitor all found devices\n    tasks = [monitor_device(device) for device in devices]\n    await asyncio.gather(*tasks)\n\nasyncio.run(main())\n```\n\n## API Reference\n\n### FlowerCareScanner\n\n- `scan_for_devices(timeout=10.0)`: Scan for FlowerCare devices\n- `find_device_by_address(mac_address, timeout=10.0)`: Find specific device by MAC address\n- `scan_continuously(callback, timeout=None)`: Continuous scanning with callback\n- `scan_stream(timeout=None)`: Async generator for device discovery\n\n### FlowerCareDevice\n\n- `connect(timeout=10.0)`: Connect to device\n- `disconnect()`: Disconnect from device\n- `read_sensor_data()`: Read current sensor measurements\n- `get_device_info()`: Get device information (name, MAC, battery, firmware)\n- `get_historical_data()`: Get stored historical measurements\n- `blink_led()`: Make device LED blink\n\n### Data Models\n\n#### SensorData\n- `temperature`: Temperature in Celsius\n- `brightness`: Light intensity in lux\n- `moisture`: Soil moisture percentage\n- `conductivity`: Soil conductivity in µS/cm\n- `timestamp`: Measurement timestamp\n\n#### DeviceInfo\n- `name`: Device name\n- `mac_address`: MAC address\n- `firmware_version`: Firmware version\n- `battery_level`: Battery level percentage\n\n## Error Handling\n\nThe library provides specific exception types:\n\n```python\nfrom pyflowercare.exceptions import (\n    FlowerCareError,      # Base exception\n    ConnectionError,      # Connection failures\n    DeviceError,         # Device operation errors\n    DataParsingError,    # Data parsing errors\n    TimeoutError         # Operation timeouts\n)\n\ntry:\n    async with device:\n        data = await device.read_sensor_data()\nexcept ConnectionError as e:\n    print(f"Failed to connect: {e}")\nexcept DeviceError as e:\n    print(f"Device error: {e}")\n```\n\n## Logging\n\nEnable logging to see detailed operation information:\n\n```python\nfrom pyflowercare import setup_logging\n\nsetup_logging("DEBUG")  # Enable debug logging\n```\n\n## Examples\n\nSee the `examples/` directory for more comprehensive examples:\n\n- `basic_usage.py`: Simple device connection and data reading\n- `continuous_monitoring.py`: Continuous monitoring of multiple devices\n- `historical_data.py`: Historical data retrieval and CSV export\n\n## Troubleshooting\n\n### Permission Issues (Linux)\n```bash\nsudo setcap cap_net_raw+eip $(eval readlink -f `which python`)\n```\n\n### Bluetooth Not Available\nEnsure your system has Bluetooth Low Energy support and the adapter is enabled.\n\n### Device Not Found\n- Ensure the FlowerCare device is nearby and not connected to another app\n- Try increasing the scan timeout\n- Check that the device battery is not depleted\n\n## License\n\nThis project is licensed under the MIT License.\n\n## Contributing\n\nContributions are welcome! Please feel free to submit issues and enhancement requests.',
    'author': 'Ilya Redkolis',
    'author_email': 'illyaredkolis@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/eljhr9/pyflowercare',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.13',
}


setup(**setup_kwargs)
