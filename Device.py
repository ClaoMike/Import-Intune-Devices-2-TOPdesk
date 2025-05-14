from typing import Optional, List, Dict

class Device:
    def __init__(self):
        # extract relevant data
        self.user_id: Optional[str] = None
        self.topdesk_asset_name: Optional[str] = None