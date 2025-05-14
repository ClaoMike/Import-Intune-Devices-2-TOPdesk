#!/usr/bin/env python3
import authentication
import auth_state
import requests
import time

from microsoft_methods import *

azure_devices, azure_user_map, intune_devices = fetch_devices()