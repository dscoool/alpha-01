import httplib2
import time
import simplejson as json
import base64
import hmac
import hashlib
import requests
import vars

# 전역변수 설정
COINONE_ACCESS_TOKEN = '0b7b8bef-3dd0-4421-b1ad-7a785ca6800c'
COINONE_SECRET_KEY = 'e600efae-893d-4588-8957-593890071d32'

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
    'X-COINONE-SIGNATURE': get_signature(encoded_payload, COINONE_SECRET_KEY)
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
    payload = {
        "access_token": COINONE_ACCESS_TOKEN,
        "price": price,
        "qty": qty,
        "currency": currency
    }
    content = post_response(url, payload)
    return content

def coin_limit_sell(price, qty, currency):
    url = 'https://api.coinone.co.kr/v2/order/limit_sell/'
    payload = {
        "access_token": COINONE_ACCESS_TOKEN,
        "price": price,
        "qty": qty,
        "currency": currency
    }
    content = post_response(url, payload)
    return content

import json 

def main():
    t=coin_balance() #잔고조회 ok
    tt = json.loads(t)
    print('krw : ' , tt['krw'])
    print('btc : ' , tt['btc'])
    print('btc : ' , tt['btg'])
    bb=coin_order_book('btg') #매도매수화면
    bbb=json.loads(bb)
    print(bbb['result'])
    print(bbb['timestamp'])
    print(bbb['bid'][0]) #최고가 매수 (빨간색 최상단 파란색 바로 아래)
    print(bbb['ask'][0]) #최저가 매도

    print(bbb['bid'][1]['price']) #1틱 아래
    print(bbb['ask'][2]['price']) #2틱 위
    
    currency = 'BTG'
    sell_price = bbb['ask'][0]['price']
    qty = 0.5
    print('========================================')
    print('SELL ORDER EXECUTION: ')
    print('currency: %s' % currency)
    print('price: %s' % sell_price)
    print('qty: %s' % qty)
    exe = input('would you like to order(SELL) this? (y/N) ')
    print(exe)
    if (exe == 'Y') or (exe =='y'):
        #SELL EXECUTION **
        coin_limit_sell(sell_price,qty,currency) #price, qty, currency 
        print('ordered - %s, price at: %s, qty: %s' % (currency , sell_price , qty) )

    elif (exe == 'N') or (exe == 'n') or (exe==''):
        print('order not executed.')
    else:
        print('error')

    #체결되면 문자 와야함 ㅋㅋ

    #clear_all_order
    # #가격 설정
    # currency = 'BTG'
    # price = bbb['bid'][0]['price']
    # qty = 5
    # print('========================================')
    # print('ORDER EXECUTION: ')
    # print('currency: %s' % currency)
    # print('price: %s' % price)
    # print('qty: %s' % qty)
    # exe = input('would you like to order this? (y/N)')
    # print(exe)
    
    # if (exe == 'Y') or (exe =='y'):
    #     coin_limit_buy(price,qty,currency) #price, qty, currency 
    #     print('ordered - %s, price at: %s, qty: %s' % (currency , price , qty) )

    # elif (exe == 'N') or (exe == 'n') or (exe==''):
    #     print('order not executed.')
    # else:
    #     print('error')
    # # print('order BTG, price at: %, qty: %' % bbb['bid'][1] % 5 )
    # coin_limit_buy(price,price,currency) #price, qty, currency 

# def test_get_wallet_status(self):
#   print(inspect.stack()[0][3])
#   result = self.coinone_machine.get_wallet_status()
#   assert result
#   print(result)
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
 
if __name__ == '__main__':
    main()