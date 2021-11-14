
import asyncio
import timeconvert
from httplib2 import debuglevel
import coinone
import time
import sms

async def get_live_order(co):
    order_id=[]
    orders=co.get_list_my_orders(currency='btg')
    # print(orders)
    for i, ord in enumerate(orders['limitOrders']):
        # print("order No. %s" %i)
        # print(ord)
        # print(ord['orderId'])
        order_id.append(ord['orderId'])
    return order_id

async def main():
    co=coinone.CoinOneMachine()
    order_id=await get_live_order(co)
    # order_id
    for ord_id in order_id:
        status=co.get_my_order_status(currency='btg',order_id=ord_id)
        print(status['status'])
        print(status['info'])

            # update db -- check if status changed
            # sms send
        elif status['status']=='filled': #매매체결순간 이거 안남아있음.
            if status['info']['type']=='bid': #buy    
                sms.sms_send(message="매수체결\n종목: %s\n가격: %s\n수량: %s\n시각: %s\n" % (status['info']['currency'],status['info']['price'],status['info']['qty'],timeconvert.timestamp_to_datetime(status['info']['timestamp'])))
            elif status['info']['type']=='ask': #sell
                sms.sms_send(message="매도체결\n종목: %s\n가격: %s\n수량: %s\n시각: %s\n" % (status['info']['currency'],status['info']['price'],status['info']['qty'],timeconvert.timestamp_to_datetime(status['info']['timestamp'])))
            print("sms sent : \n")
 
        elif status['status']=='partially_filled':
            pass
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())