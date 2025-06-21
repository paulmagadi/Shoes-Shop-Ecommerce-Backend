import base64
import requests
from django.conf import settings
from datetime import datetime

# Replace these with your Daraja sandbox/live credentials
MPESA_SHORTCODE = "174379"  # test Paybill
MPESA_PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
MPESA_CONSUMER_KEY = "y5uiNFjM7rpaXVsG7BwhsOusxPl40qV6l6TVsoNYbJJVLP9Q"
MPESA_CONSUMER_SECRET = "AYiXGvjOYHp9g5kkHUTANvvENqUohzLaIFLFLcUuuw4pgpAjoAGAs5kSXqWRL0gY"
MPESA_ENVIRONMENT = "sandbox"  # or "production"

BASE_URL = "https://sandbox.safaricom.co.ke" if MPESA_ENVIRONMENT == "sandbox" else "https://api.safaricom.co.ke"


def get_access_token():
    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return response.json().get("access_token")


def generate_password():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = MPESA_SHORTCODE + MPESA_PASSKEY + timestamp
    return base64.b64encode(data_to_encode.encode()).decode(), timestamp
