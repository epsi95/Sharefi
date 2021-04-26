import datetime
import json
import os

import requests
from flask import Flask, render_template, request, redirect, make_response, url_for
import razorpay

from utils.encryption_utils import *
from utils.otp_util import *
from utils.phone_number_util import *
from utils.mongo_util import MongoDB
from utils.email_util import *
from utils.tplink_python import TPLinkClient

# getting environment variables and setting up constants
API_KEY = os.environ.get('API_KEY')
COOKIE_ENCRYPTION_KEY = os.environ.get('COOKIE_ENCRYPTION_KEY')
MONGO_CONNECTION_STRING = os.environ.get('MONGO_CONNECTION_STRING')
RAZORPAY_ID = os.environ.get('RAZORPAY_ID')
RAZORPAY_SECRET = os.environ.get('RAZORPAY_SECRET')
TPLINK_ID = os.environ.get('TPLINK_ID')
TPLINK_PASSWORD = os.environ.get('TPLINK_PASSWORD')
PORT_NUMBER = 8080

if not COOKIE_ENCRYPTION_KEY:
    print("no encryption key available as os.environ.get('COOKIE_ENCRYPTION_KEY')")
    key = Fernet.generate_key()
    COOKIE_ENCRYPTION_KEY = os.environ['COOKIE_ENCRYPTION_KEY'] = key.decode()


app = Flask(__name__)

mongo_db = MongoDB(MONGO_CONNECTION_STRING)
razorpay_client = razorpay.Client(auth=(RAZORPAY_ID, RAZORPAY_SECRET))
tp_client = TPLinkClient(TPLINK_ID, TPLINK_PASSWORD)


def url_end_point(request_obj):
    if "ngrok" in request_obj.host_url:
        return request_obj.host_url.replace('http', 'https')[:-1]
    else:
        return request_obj.host_url[:-1]


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/checkNumber', methods=['POST', 'GET'])
def check_number():
    if request.method == 'POST':
        user_mobile_number = request.form.get("mobileNumber")
        if not is_valid_number(user_mobile_number)[0]:
            print('Route: ' + '/checkNumber' + '>>>' + 'mobile number not valid type ' + user_mobile_number)
            return redirect(url_end_point(request))
        result = mongo_db.get_user_info(user_mobile_number)
        if result:
            # print(result)
            user_mobile_number = result.get("mobile")
            user_name = result.get("name")
            user_name = result.get("name")
            user_name = result.get("name")
            user_name = result.get("name")
            user_mac = result.get("mac")
            current_status = result.get("session_state")
            if user_mobile_number and user_name and user_mac and current_status:
                cookie_string = json.dumps({
                    "user_mobile_number": user_mobile_number,
                    "user_name": user_name,
                    "user_mac": user_mac
                })
                if current_status == "SUSPENDED":
                    response = make_response(render_template("checkout.html", user_mobile_number=user_mobile_number,
                                                             user_name=user_name,
                                                             user_mac=user_mac))
                    response.set_cookie("jwt_like_session", encrypt_data(cookie_string, COOKIE_ENCRYPTION_KEY))
                    return response
                elif current_status == "ACTIVE":
                    return redirect(url_end_point(request) + '/success?sessionEndDate=' + result[
                        'session_end_dt'].strftime("%d-%b-%Y %H:%M:%S"))
            else:
                return redirect(url_end_point(request))
        else:
            return redirect(
                url_end_point(request) + '/userRegistration?mobileNumber=' + str(user_mobile_number))
    else:
        return redirect(url_end_point(request))


@app.route('/userRegistration', methods=['POST', 'GET'])
def user_registration():
    if request.method == 'POST':
        user_mobile_number = request.form.get("mobileNumber")
        user_name = request.form.get("userName")
        user_mac = request.form.get("userMac")
        if not is_valid_number(user_mobile_number)[0]:
            return redirect(url_end_point(request) + '/userRegistration')
        if user_mobile_number and user_name and user_mac:
            response = make_response(render_template('otp.html', on_otp_submit_url='/createUser', display_state="none"))
            otp_send_status = send_otp(user_mobile_number)
            print('OTP send status ' + otp_send_status)
            cookie_string = json.dumps({
                "user_mobile_number": user_mobile_number,
                "user_name": user_name,
                "user_mac": user_mac
            })
            response.set_cookie("jwt_like_session", encrypt_data(cookie_string, COOKIE_ENCRYPTION_KEY))
            return response

        else:
            return redirect(
                url_end_point(request) + '/userRegistration?mobileNumber=' + str(user_mobile_number))
    else:
        mobile_number = request.args.get('mobileNumber')
        return render_template('registration.html', mobile_number=mobile_number)


@app.route('/createUser', methods=['POST'])
def create_user():
    cookie_string = request.cookies.get("jwt_like_session")
    if not cookie_string:
        return redirect(url_end_point(request))
    try:
        data = json.loads(decrypt_data(cookie_string, COOKIE_ENCRYPTION_KEY))
        user_mobile_number = data.get("user_mobile_number")
        user_name = data.get("user_name")
        user_mac = data.get("user_mac")

        user_provided_otp = request.form.get("otp")
        if user_mobile_number and user_name and user_mac and user_provided_otp:
            if verify_otp(user_mobile_number, user_provided_otp):
                result = mongo_db.create_user(user_mobile_number, user_name, user_mac)
                if result == -1:
                    return redirect(url_end_point(request))
                else:
                    print('Route: ' + '/createUser' + '>>>' + 'user creation success ' + str(result))
                    send_email(f"""
                    New User created
                    at: {datetime.datetime.now()}
                    name: {user_name}
                    mobile number: {user_mobile_number}
                    mac: {user_mac}
                    """)
                    return render_template("checkout.html", user_mobile_number=user_mobile_number,
                                           user_name=user_name,
                                           user_mac=user_mac
                                           )
            else:
                return render_template('otp.html', on_otp_submit_url='/createUser', display_state="block")
        else:
            return redirect(url_end_point(request))

    except Exception as e:
        print(e)
        return redirect(url_end_point(request))


@app.route('/checkOut', methods=['POST'])
def checkout():
    if request.method == 'POST':
        cookie_string = request.cookies.get("jwt_like_session")
        if not cookie_string:
            return redirect(url_end_point(request))
        try:
            print(cookie_string)
            data = json.loads(decrypt_data(cookie_string, COOKIE_ENCRYPTION_KEY))
            print(data)
            user_mobile_number = data.get("user_mobile_number")
            user_name = data.get("user_name")
            user_mac = data.get("user_mac")
            if not (user_mobile_number and user_name and user_mac):
                return redirect(url_end_point(request))
            order_receipt = str(user_mobile_number) + '_' + str(
                int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000))
            print(order_receipt)
            order = razorpay_client.order.create({
                "amount": 700,
                "currency": "INR",
                "receipt": order_receipt
            })
            print(order)
            mongo_db.insert_order(order)
            return render_template("razorpay_checkout.html", user_mobile_number=user_mobile_number,
                                   user_name=user_name,
                                   user_mac=user_mac,
                                   RAZORPAY_ID=RAZORPAY_ID,
                                   amount=700,
                                   order_id=order['id'],
                                   logo=url_end_point(request) + "/static/ShareFi.svg",
                                   callback_url=url_end_point(request))
        except Exception as e:
            return redirect(url_end_point(request))
    else:
        return redirect(url_end_point(request))


@app.route('/charge', methods=['POST'])
def app_charge():
    # print(request.form)
    amount = 700
    payment_id = request.form['razorpay_payment_id']
    print(payment_id)
    # razorpay_client.payment.capture(payment_id, amount)
    captured_payment_details = razorpay_client.payment.fetch(payment_id)
    mongo_db.insert_captured_payment(captured_payment_details)
    order_id = captured_payment_details['order_id']
    order_details = mongo_db.get_order_details(order_id)
    mobile_number = order_details['receipt'].split('_')[0]
    result = mongo_db.get_user_info(mobile_number)
    user_mac = result.get("mac")
    sessionEndDate = mongo_db.update_user_subscription(mobile_number).strftime("%d-%b-%Y %H:%M:%S")
    mac_whitelist_result = tp_client.whitelist_mac(user_mac, str(mobile_number))
    if "[error]0" not in mac_whitelist_result:
        print("whitelisting not successful", mac_whitelist_result)
        return redirect(url_end_point(request))
    else:
        print("whitelisting successful")
        return redirect(url_end_point(request) + '/success?sessionEndDate=' + sessionEndDate)


@app.route('/success')
def success_page():
    session_end_dt = request.args.get('sessionEndDate')
    return render_template("success.html", wifi_password="123456987fff", subscription_end_date=session_end_dt)


@app.route('/resendOtp')
def resend_otp():
    cookie_string = request.cookies.get("jwt_like_session")
    if not cookie_string:
        return "ERROR", 404
    try:
        data = json.loads(decrypt_data(cookie_string, COOKIE_ENCRYPTION_KEY))
        user_mobile_number = data.get("user_mobile_number")
        user_name = data.get("user_name")
        user_mac = data.get("user_mac")
        otp_send_status = send_otp(user_mobile_number)
        print('OTP re-send status ' + otp_send_status)
        return "INITIATED", 200
    except Exception as e:
        print(e)
        return "ERROR", 404


@app.route('/macInfo')
def get_mac_info():
    return "mac details"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=PORT_NUMBER)
