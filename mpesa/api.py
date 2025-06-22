import requests
import base64
from django.conf import settings
from datetime import datetime

def get_access_token():
    auth_url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    response.raise_for_status()
    return response.json()['access_token']

def generate_password(timestamp):
    data_to_encode = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    return base64.b64encode(data_to_encode.encode()).decode('utf-8')

def send_stk_push(phone, amount, order_id=None):
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = generate_password(timestamp)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Use fallback reference if order_id is not passed
    account_ref = f"ORDER{order_id}" if order_id else f"TXN{timestamp[-6:]}"
    description = f"Payment for Order #{order_id}" if order_id else "Pending Order Payment"

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": description,
    }

    try:
        response = requests.post(
            f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "ResponseCode": "1",
            "ResponseDescription": "STK Push Request Failed",
            "error": str(e)
        }
