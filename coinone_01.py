import httplib2
import time
import simplejson as json
import base64
import hmac
import hashlib
import requests
import vars

# 전역변수 설정
# vars.COINONE_ACCESS_TOKEN
# vars.COINONE_SECRET_KEY

def coin_balance():
    url = 'https://api.coinone.co.kr/v2/account/balance/'
    payload = {
        "access_token": COINONE_ACCESS_TOKEN,
    }
    content = post_response(url, payload)
    return content

def get_signature(self, encoded_payload, secret_key):
    signature = hmac.new(secret_key, encoded_payload, hashlib.sha512);
    return signature.hexdigest()

def get_wallet_status(self):

        time.sleep(1)
        url_path = 'https://api.coinone.co.kr/v2/account/balance/'
        payload ={
            "access_token": COINONE_ACCESS_TOKEN,
            'nonce': self.get_nonce()
        }
        dumped_json = json.dumps(payload)
        encoded_payload = base64.b64encode(dumped_json.encode('utf-8')) 
        encoded_secret_key = base64.b64encode(self.secret_key.upper().encode('utf-8')) 

        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': self.get_signature(encoded_payload, self.secret_key.encode('utf-8'))}

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result

def get_encoded_payload(payload):
  payload[u'nonce'] = int(time.time()*1000)

  dumped_json = json.dumps(payload).encode()
  encoded_json = base64.b64encode(dumped_json)
  return encoded_json

def get_signature(encoded_payload, secret_key):
  signature = hmac.new(secret_key.upper().encode(), encoded_payload, hashlib.sha512);
  return signature.hexdigest()

def get_response(url, payload):
  encoded_payload = get_encoded_payload(payload)
  headers = {
    'Content-type': 'application/json',
    'X-COINONE-PAYLOAD': encoded_payload,
    'X-COINONE-SIGNATURE': get_signature(encoded_payload, COINONE_SECRET_KEY)
  }
  http = httplib2.Http()
  response, content = http.request(url, 'GET', headers=headers, body=encoded_payload)
  return content

def post_response(url, payload):
  encoded_payload = get_encoded_payload(payload)
  headers = {
    'Content-type': 'application/json',
    'X-COINONE-PAYLOAD': encoded_payload,
    'X-COINONE-SIGNATURE': get_signature(encoded_payload, SECRET_KEY)
  }
  http = httplib2.Http()
  response, content = http.request(url, 'POST', headers=headers, body=encoded_payload)
  return content

def coin_order_book(currency):
    url = 'https://api.coinone.co.kr/orderbook/?currency={}&format=json'.format(currency)
    payload = {
        "access_token": COINONE_ACCESS_TOKEN,
    }
    content = get_response(url, payload)
    return content

def coin_limit_buy(price, qty, currency):
    url = 'https://api.coinone.co.kr/v2/order/limit_buy/'
    price = coinone_price(price)#hasworld_debug
    payload = {
        "access_token": ACCESS_TOKEN,
        "price": price,
        "qty": qty,
        "currency": currency
    }
    content = post_response(url, payload)
    return content

def coin_limit_sell(price, qty, currency):
    url = 'https://api.coinone.co.kr/v2/order/limit_sell/'
    price = coinone_price(price)#hasworld_debug
    payload = {
        "access_token": ACCESS_TOKEN,
        "price": price,
        "qty": qty,
        "currency": currency
    }
    content = post_response(url, payload)
    return content

def main():
  test_get_wallet_status()

def test_get_wallet_status(self):
  print(inspect.stack()[0][3])
  result = self.coinone_machine.get_wallet_status()
  assert result
  print(result)
    # print(inspect.stack()[0][3])
    # result = self.coinone_machine.get_wallet_status()
    # assert result
    # print(result)
    # # amount=coin_balance()
    # amt = json.loads(amount)
    # print(amt['result'])
    # print(amt['krw'])
    # print(amt['btc'])
    # t=get_wallet_status()
    # print(t)
    # k=get_signature()
    # print(k)
 
# if __name__ == '__main__':
#     main()