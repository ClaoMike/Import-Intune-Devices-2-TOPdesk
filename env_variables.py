from dotenv import load_dotenv
import os

# Load variables from .env into environment
load_dotenv()

tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

topdesk_username = os.getenv("TOPDESK_USERNAME")
topdesk_password = os.getenv("topdesk_password")
topdesk_devices_category_id = os.getenv("topdesk_devices_category_id")
