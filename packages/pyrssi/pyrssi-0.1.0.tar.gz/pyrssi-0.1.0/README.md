# pyrssi

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)]()

**pyrssi** is a lightweight Python package for retrieving the current Wi-Fi signal strength (RSSI) on **macOS, Windows, and Linux**. It automatically detects the operating system and uses the optimal method for each platform.

---

## Features

- Retrieve the current Wi-Fi RSSI (signal strength) in dBm.
- Automatically detects the operating system.
- Supports **macOS**, **Windows**, and **Linux**.

---

## Installation

### Install via PyPI

```bash
pip install pyrssi
Install from source

```bash
git clone https://github.com/yourusername/pyrssi.git
cd pyrssi
pip install .
```

Usage

```python
import pyrssi

rssi = pyrssi.get_rssi()
if rssi is not None:
    print(f"Current Wi-Fi RSSI: {rssi} dBm")
else:
    print("Wi-Fi not detected or interface unavailable.")
```
Returns an integer representing the RSSI in dBm.

Returns None if no Wi-Fi is connected or the interface cannot be accessed.

## Platform Support
### macOS
- Uses CoreWLAN via pyobjc.
- No sudo required.
- Retrieves the RSSI for the first available Wi-Fi interface.

### Windows
- Uses the built-in netsh wlan show interfaces command.
- Parses the output to extract the RSSI.

### Linux
- Reads /proc/net/wireless to extract the signal strength.
- No additional dependencies required.

### Requirements
- Python 3.7+
- macOS: pyobjc (installed automatically if using pip)
- Windows/Linux: No additional packages required.

### License
- MIT License. See LICENSE for details.

### Contributing
Contributions are welcome! Please open issues or pull requests on GitHub.

### Example Output
```python
>>> import pyrssi
>>> print(pyrssi.get_rssi())
-55
```