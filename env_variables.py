from dotenv import load_dotenv
import os

# Load variables from .env into environment
load_dotenv()

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

topdesk_username = os.getenv("TOPDESK_USERNAME")
topdesk_password = os.getenv("TOPDESK_PASSWORD")

topdesk_computer_category_id = os.getenv("TOPDESK_COMPUTER_CATEGORY_ID")
topdesk_mobile_category_id = os.getenv("TOPDESK_MOBILE_CATEGORY_ID")
topdesk_device_category_id = os.getenv("TOPDESK_DEVICE_CATEGORY_ID")