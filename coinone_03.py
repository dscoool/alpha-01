import httplib2
import time
import simplejson as json
import base64
import hmac
import hashlib
import requests
import vars
import json
import inspect
import configparser

# 전역변수 설정
COINONE_ACCESS_TOKEN = '0b7b8bef-3dd0-4421-b1ad-7a785ca6800c'
COINONE_SECRET_KEY = 'e600efae-893d-4588-8957-593890071d32'


class CoinOneMachine():
    """
    코인원 거래소와 거래를 위한 클래스입니다.
    BASE_API_URL은 REST API호출의 기본 URL입니다.
    TRADE_CURRENCY_TYPE은 코인원에서 거래가 가능한 화폐의 종류입니다.
    """
    BASE_API_URL = "https://api.coinone.co.kr"
    ASSET = ['krw','btc','btg']
    # CURRENCY_TYPE = ["krw","btc","btg"]
    
    def __init__(self):
        """
        CoinOneMachine 클래스의 최초 호출 메소드입니다.
        config.ini에서 access_token, secret_key 정보를 읽어옵니다.
        """
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.access_token = vars.COINONE_ACCESS_TOKEN
        self.secret_key = vars.COINONE_SECRET_KEY
        
    def get_username(self):
        if self.username is None: 
            return None
        return self.username

    def get_nonce(self):
        """Private API 호출 시 사용할 nonce값을 구하는 메소드입니다.
        
        Returns:
            nonce값을 반환합니다.
        """   
        return int(time.time())

    def get_token(self):
        """인증토큰 정보를 받기 위한 메소드입니다.
        Returns:
            인증토큰(asscee_token)이 있는 경우 반환합니다.
            
        Raises:
            access_token이 없는 경우 Exception을 발생시킵니다.
        
        """
        if self.access_token is not None:
            return self.access_token
        else:
            raise Exception("Need to set_token")

    def set_token(self, grant_type="refresh_token"):
        """인증토큰 정보를 만들기 위한 메소드입니다.
         
        Returns:
            만료시간(expire),인증토큰(access_token),리프레쉬토큰(refresh_token) 을 반환합니다.
        
        Raises:
            grant_type이 password나 refresh_token이 아닌 경우 Exception을 발생시킵니다.
        """   
        token_api_path = "/oauth/refresh_token/"
        url_path = self.BASE_API_URL + token_api_path
        self.expire = 3600

        if grant_type == "refresh_token":
            headers = {"content-type":"application/x-www-form-urlencoded"} 
            data = {"access_token":self.access_token}
            res = requests.post(url_path, headers=headers, data=data)
            result = res.json()
            if result["result"] == "success":
                config = configparser.ConfigParser()
                config.read('conf/config.ini')
                self.access_token = result["accessToken"]
                config["COINONE"]["access_token"] = self.access_token
                with open('conf/config.ini', 'w') as configfile:
                    config.write(configfile)
            else:
                raise Exception("Failed set_token")
        else:
            self.access_token = config['COINONE']['access_token']
        return self.expire, self.access_token, self.access_token

    def get_ticker(self, currency_type=None):
        """마지막 체결정보(Tick)을 얻기 위한 메소드입니다.

        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 ASSET에 정의되어있습니다.
        
        Returns:
            결과를 딕셔너리로 반환합니다. 
            결과의 필드는 timestamp, last, bid, ask, high, low, volume이 있습니다.
            
        Raise:
            currency_type이 없으면 Exception을 발생시킵니다. 
        """
        ticker_api_path = '/ticker/'
        url_path = self.BASE_API_URL + ticker_api_path
        params = {"currency": currency_type}
        res = requests.get(url_path, params=params)
        response_json = res.json() 
        result = {}
        result["timestamp"] = str(response_json["timestamp"])
        result["last"] = response_json["last"]
        result["high"] = response_json["high"]
        result["low"] = response_json["low"]
        result["volume"] = response_json["volume"]
        return result

    def get_filled_orders(self, currency_type=None, per="minute"):
        pass

    def get_signature(self, encoded_payload, secret_key):
        """
        Args: 
            encoded_payload(str): 인코딩된 payload 값입니다.
            secret_key(str): 서명할때 사용할 사용자의 secret_key 입니다.
        Returns:
            사용자의 secret_key로 서명된 데이터를 반환합니다.
        """
        signature = hmac.new(secret_key, encoded_payload, hashlib.sha512);
        return signature.hexdigest()
    
    def get_encoded_payload(self, payload):
        """
        Args:
            payload(str):인코딩할 payload
             
        Returns:
            인코딩된 payload값을 반환합니다 .
        """
        dumped_json = json.dumps(payload)
        return base64.b64encode(dumped_json.encode('utf-8'))  
        
    def get_wallet_status(self):
        """사용자의 지갑정보를 조회하는 메소드입니다.
        
        Returns:
            사용자의 지갑에 화폐별 잔고를 딕셔너리 형태로 반환합니다.
        """
        time.sleep(1)
        wallet_status_api_path = "/v2/account/balance"
        url_path = self.BASE_API_URL + wallet_status_api_path
        payload ={
            "access_token":self.access_token,
            'nonce':self.get_nonce()
        }
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8')) 
        
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature}

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        wallet_status = {currency: result[currency] for currency in self.ASSET }
        return wallet_status

    def get_list_my_orders(self, currency_type=None):
        time.sleep(1)
        list_api_path = "/v2/order/limit_orders/"
        url_path = self.BASE_API_URL + list_api_path
        
        payload ={
            "access_token":self.access_token,
            "currency":currency_type,
            'nonce':self.get_nonce()
        }
        
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8')) 
        
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature}

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result

    def get_my_order_status(self, currency_type=None, order_id=None):
        """사용자의 주문정보 상세정보를 조회하는 메소드입니다. 
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            order_id(str): 거래ID
            
        Returns:
            order_id에 해당하는 주문의 상세정보를 반환합니다.
        """
        list_api_path = "/v2/order/order_info/"
        url_path = self.BASE_API_URL + list_api_path
        
        payload ={
            "access_token":self.access_token,
            "currency":currency_type,
            "order_id":order_id,
            'nonce':self.get_nonce()
        }
        
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8')) 
        
        headers = { 'Content-type': 'application/json',
                    'X-COINONE-PAYLOAD': encoded_payload,
                    'X-COINONE-SIGNATURE': signature }

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result


    def buy_order(self, currency_type=None, price=None, qty=None, order_type="limit"):
        """매수 주문을 실행하는 메소드입니다.. 
        
        Note:
            화폐 종류마다 최소 주문 수량은 다를 수 있습니다.
            이 메소드는 지정가 거래만 지원합니다.      
            
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            price(int): 1개 수량 주문에 해당하는 원화(krw) 값
            qty(float): 주문 수량입니다. 
            
        Returns:
            주문의 상태에 대해 반환합니다.
        """
        if order_type != "limit":
            raise Exception("Coinone order type support only limit.")
        time.sleep(1)
        buy_limit_api_path ="/v2/order/limit_buy/"
        url_path = self.BASE_API_URL + buy_limit_api_path
        
        payload ={
            "access_token" : self.access_token,
            "price" : int(price),
            "qty" : float(qty),
            "currency":currency_type,
            'nonce' : self.get_nonce()
        }

        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8'))
        
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature }

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result

    def sell_order(self, currency_type=None, price=None, qty=None, order_type="limit"):
        """매도 주문을 실행하는 메소드입니다.. 
        
        Note:
            화폐 종류마다 최소 주문 수량은 다를 수 있습니다.
            이 메소드는 지정가 거래만 지원합니다.      
            
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            price(int): 1개 수량 주문에 해당하는 원화(krw) 값
            qty(float): 주문 수량입니다. 
            
        Returns:
            주문의 상태에 대해 반환합니다.
        """
        if order_type != "limit":
            raise Exception("Coinone order type support only limit.")
        time.sleep(1)
        sell_limit_api_path ="/v2/order/limit_sell/"
        url_path = self.BASE_API_URL + sell_limit_api_path
        
        payload ={
            "access_token" : self.access_token,
            "price" : int(price),
            "qty" : float(qty),
            "currency":currency_type,
            'nonce' : self.get_nonce()
        }
        
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8'))
        
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature }

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result

    def cancel_order(self, currency_type=None, order_type=None, order_id=None):
        """매도 주문을 실행하는 메소드입니다.. 
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            order_type(str): 취소하려는 주문의 종류(매수, 매도) 
            order_id(str): 취소 주문하려는 주문의 ID
            
        Returns:
            주문의 상태에 대해 반환합니다.
        """
        if currency_type is None or order_type is None or order_id is None:
            raise Exception("Need to parameter")
        time.sleep(1)
        cancel_api_path ="/v2/order/cancel/"
        url_path = self.BASE_API_URL + cancel_api_path
           
        payload ={
            "access_token" : self.access_token,
            "order_id" : order_id,
            "currency":currency_type,
            "is_ask": 1 if order_type is "sell" else 0,
            'nonce' : self.get_nonce()
        }
        
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8'))
 
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature }

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result

    def __repr__(self):
        return "(CoinOne %s)"%self.username

    def __str__(self):
        return str("CoinOne")


def get_my_order_status(self, coin_type=None, order_id=None):
        """
        get list my transaction history
        """
        list_api_path = "/v2/order/order_info/"
        url_path = self.host + list_api_path
        payload ={
            "access_token":self.access_token,
            "currency":coin_type,
            "order_id":order_id,
            'nonce':self.get_nonce()
        }
        dumped_json = json.dumps(payload)
        encoded_payload = base64.b64encode(dumped_json.encode('utf-8')) 

        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': self.get_signature(encoded_payload, self.secret_key.encode('utf-8'))}

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result



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
        """
        Get wallet_status
        """
        time.sleep(1)
        wallet_status_api_path ="/v1/user/balances"
        url_path = self.host + wallet_status_api_path
        headers = {"Authorization":"Bearer " + self.access_token}
        res = requests.get(url_path, headers=headers)
        result = res.json()
        print("balance:"+result["krw"]["available"])
        return result["krw"]["available"]

def get_encoded_payload(payload):
  payload[u'nonce'] = int(time.time()*1000)

  dumped_json = json.dumps(payload).encode()
  encoded_json = base64.b64encode(dumped_json)
  return encoded_json

def get_signature(encoded_payload, secret_key):
  signature = hmac.new(secret_key.upper().encode(), encoded_payload, hashlib.sha512)
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

    print(inspect.stack()[0][3])
    c=CoinOneMachine()

    #잔고 불러오기

    # result = c.get_wallet_status() 
    # assert result
    # print(result)
    # print(result['btg'])

    


    # currency = 'BTG'
    # sell_price = bbb['ask'][0]['price']
    # qty = 0.5
    # print('========================================')
    # print('SELL ORDER EXECUTION: ')
    # print('currency: %s' % currency)
    # print('price: %s' % sell_price)
    # print('qty: %s' % qty)
    # exe = input('would you like to order(SELL) this? (y/N) ')
    # print(exe)
    # if (exe == 'Y') or (exe =='y'):
    #     #SELL EXECUTION **
    #     coin_limit_sell(sell_price,qty,currency) #price, qty, currency 
    #     print('ordered - %s, price at: %s, qty: %s' % (currency , sell_price , qty) )

    # elif (exe == 'N') or (exe == 'n') or (exe==''):
    #     print('order not executed.')
    # else:
    #     print('error')

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