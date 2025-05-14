from topdesk_methods import *
from Device import *

def get_device_template(device):
    operating_system = device.get('operatingSystem')
    type = Device.get_device_type(operating_system)

    if type is Device.Type.DEVICE:  # Skip these
        return topdesk_device_category_id
    elif type is Device.Type.COMPUTER:
        return topdesk_computer_category_id
    elif type is Device.Type.MOBILE:
        return topdesk_mobile_category_id
    else:
        print("New OS detected - please take action")
        return None