from bfxapi import Client, BfxWebsocket
import sys

sys.path.append('/../')
ws = BfxWebsocket(
             API_KEY=None,
             API_SECRET=None,
             host='wss://api-pub.bitfinex.com/ws/2',
             manageOrderBooks=False,
             dead_man_switch=False,
             ws_capacity=25,
             logLevel='INFO',
             parse_float=float,
             channel_filter=[]
             )


# ws = websockets.WebSocketApp('wss://api-pub.bitfinex.com/ws/2')

ws.on_open = lambda self: self.send('{ "event": "subscribe", "channel": "trades", "symbol": "tBTCUSD"}')

ws.on_message = lambda self, evt:  print (evt)