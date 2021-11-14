import base64
import hashlib
import hmac
import time
import requests
import json

sms_access_key ='sgexVDJCXm4ms8Sa8yIS'
sms_secret_key ='yI0fdXaaE6M6Z0HebEJHFF4OCINyeQvVgfKdymsW'
sms_service_id = 'ncp:sms:kr:270697157096:alpha-01'

def send(message,number='01058409500'):
    url = "https://sens.apigw.ntruss.com"
    uri = "/sms/v2/services/" + sms_service_id + "/messages"
    api_url = url + uri
    timestamp = str(int(time.time() * 1000))
    string_to_sign = "POST " + uri + "\n" + timestamp + "\n" + sms_access_key
    signature = make_signature(string_to_sign)

    # 예약내역 불러와서 변환
    # number = '01058409500'
    # name = '안용미'

    # message = "안녕하세요 안녕하세요 몇자나가나봅시다 주가가오릅니다내립니다내리다맙니다."

    headers = {
        'Content-Type': "application/json; charset=UTF-8",
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': sms_access_key,
        'x-ncp-apigw-signature-v2': signature
    }

    body = {
        "type": "SMS",
        "contentType": "COMM",
        "from": "01058409500",
        "content": message,
        "messages": [{"to": number}]
    }

    body = json.dumps(body)

    response = requests.post(api_url, headers=headers, data=body)
    response.raise_for_status()
    print(response.json())

def make_signature(string):
    secret_key = bytes(sms_secret_key, 'UTF-8')
    string = bytes(string, 'UTF-8')
    string_hmac = hmac.new(secret_key, string, digestmod=hashlib.sha256).digest()
    string_base64 = base64.b64encode(string_hmac).decode('UTF-8')
    return string_base64

send("집에가세요집에가세요집에가세요","01058409500")