#!/usr/bin/env python3
from microsoft_methods import *

devices = fetch_devices()

for device in devices:
    print(device.user_id)