# Oliver Weinmeier, Date: 15.4.2020
# This code searches for all discoverable devices closeby and prints them.
# Bluetooth Discovery can take quite a long time (up to 15 seconds)
# It is important to check if the nearby devices are actually discovery
# (they are not by default, only during the pairing process and the like)
import bluetooth


nearbyDevices = bluetooth.discover_devices(lookup_names=True)
print(f"The scan has discovered {len(nearbyDevices)} devices")

for addr, name in nearbyDevices:
    print(f"{addr}:{name}")
