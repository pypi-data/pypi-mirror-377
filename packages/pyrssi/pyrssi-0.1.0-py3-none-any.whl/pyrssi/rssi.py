import platform
import subprocess
import re
import time

if platform.system() == "Darwin":
    import objc
    from CoreWLAN import CWInterface

def get_rssi_mac():
    """Use CoreWLAN (no sudo)"""
    try:
        interface_names = list(CWInterface.interfaceNames())
        if not interface_names:
            return None
        interface_name = interface_names[0]
        wifi = CWInterface.interfaceWithName_(interface_name)
        rssi = wifi.rssi()
        return rssi
    except Exception:
        return None

def get_rssi_windows():
    """Use netsh wlan show interfaces"""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True,
            text=True
        )
        output = result.stdout
        rssi_match = re.search(r"Rssi\s*:\s*(.*)", output)
        if rssi_match:
            rssi = int(rssi_match.group(1))
        else:
            rssi = None
        return rssi
    except Exception:
        return None

def get_rssi_linux():
    """Use /proc/net/wireless via subprocess"""
    try:
        output = subprocess.check_output(["cat", "/proc/net/wireless"], text=True)
        m = re.search(r'(\w+):\s+\d+\.\s+(\-?\d+)\.\s+(\-?\d+)\.', output)
        if m:
            rssi = int(m.group(3))
            return rssi
        else:
            return None
    except Exception:
        return None

def get_rssi():
    system = platform.system()
    if system == "Darwin":
        return get_rssi_mac()
    elif system == "Windows":
        return get_rssi_windows()
    elif system == "Linux":
        return get_rssi_linux()
    else:
        return None