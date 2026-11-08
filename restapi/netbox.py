#!/usr/bin/env python3

import json
import os
from pynetbox import api
from requests.exceptions import RequestException

# Configuration from environment variables
NETBOX_URL = os.getenv("NETBOX_URL", "https://your-netbox-instance.com")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN")

if not NETBOX_TOKEN:
    print("Error: NETBOX_TOKEN environment variable not set")
    exit(1)

try:
    nb = api(url=NETBOX_URL, token=NETBOX_TOKEN)


    # Query all devices
    #devices = nb.dcim.devices.all()
    # Query with filter
    devices = nb.dcim.devices.filter(name__ic="QH2-rcc100")

    for device in devices:
        serial = device.serial if device.serial else "N/A"
        print(f"{device.name}: {serial}")
        print(device)
        print(json.dumps(device.serialize(), indent=2))



except RequestException as e:
    print(f"Error connecting to NetBox: {e}")
    exit(1)
