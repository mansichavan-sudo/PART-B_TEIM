import paypalrestsdk
from django.conf import settings

# Configure PayPal SDK
PAYPAL_CLIENT_ID = 'AaOe-iPeBSxdlRqmXN_1fFIBC_bf5UO-NsD_2ERJL_Nw278iSCywt6lWsWOY_DxuMo0NsCi1u8rgVAZa'
PAYPAL_CLIENT_SECRET = 'EHAS1bQ_l5ZCBk5r8MrG2dzUFP9ZlJ_eJAwHOCfVngWV--8NtfSiEwMDCzGVILITLU6bjBKce6Fd3UQT'
PAYPAL_MODE = 'sandbox'

paypalrestsdk.configure({
    "mode": PAYPAL_MODE,  # "sandbox" 
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET
})