import random
import requests
import json
import os

pool = {}

MAILJET_AUTH = os.environ.get('MAILJET_AUTH')

# defining OTP sending and validation function
def send_otp(user_mobile_number):
    try:
        otp = random.randint(100000, 999999)
        pool[str(user_mobile_number)] = otp

        url = "https://api.mailjet.com/v4/sms-send"
        payload = json.dumps({
            "Text": str(otp) + " is your OTP for ShareFi internet subscription @rupees7/day.",
            "To": "+91" + str(user_mobile_number),
            "From": "ShareFi"
        })
        headers = {
            'Authorization': MAILJET_AUTH,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

        return 'SUCCESS ' + str(otp)
    except Exception as e:
        print(e)
        return 'FAILURE'


def verify_otp(user_mobile_number, otp):
    try:
        if str(user_mobile_number) in pool:
            if pool[str(user_mobile_number)] == int(otp):
                del pool[str(user_mobile_number)]
                return True
        return False
    except Exception as e:
        print(e)
        return False
