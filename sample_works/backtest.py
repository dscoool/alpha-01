from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
# from datetime import datetime
import asyncio
import get_public_data
import coinone_01
import vars
import pandas as pd
import time
import db
import vortex
import backtrader as bt
from ta import add_all_ta_features
from ta.utils import dropna
from ta import trend
import argparse

async def datetime_to_timestamp(y,m,d,hh=0,mm=0,ss=0,mmmmmm=0): #UTC기준
  timestamp=round(datetime.datetime(y, m, d, hh, mm, ss, mmmmmm).timestamp()*1000)
  return timestamp

async def timestamp_to_datetime(timestamp):
  ts_series=timestamp.apply(lambda x: datetime.fromtimestamp(x/1000))
  return ts_series
    # Create a subclass of Strategy to define the indicators and logic
def timestamp_to_datetime_2(timestamp):
  ts_series = timestamp.apply(lambda x: datetime.datetime.fromtimestamp(x/1000))
#   print(ts_series)
#   ts_series = datetime.date(ts_series)
  return ts_series
    # Create a subclass of Strategy to define the indicators and logic

class vi_strategy(bt.SignalStrategy):

    def notify_order(self, order):
        if not order.alive():
            print('{} {} {}@{}'.format(
                bt.num2date(order.executed.dt),
                'buy' if order.isbuy() else 'sell',
                order.executed.size,
                order.executed.price)
            )

    def notify_trade(self, trade):
        if trade.isclosed:
            print('profit {}'.format(trade.pnlcomm))

    def __init__(self):
        vi_diff=df_vi.loc[:,'VI_DIFF']
        vi_pos=df_vi.loc[:,'VI_POS']
        vi_neg=df_vi.loc[:,'VI_NEG']
        self.crossover = bt.ind.CrossOver(vi_pos, vi_neg)
        self.signal_add(bt.SIGNAL_LONG, self.crossover)

#buy, sell 제대로 됐는지 체크할 것 **

# 참조: https://github.com/mementum/backtrader/blob/master/samples/sigsmacross/sigsmacross.py

def runstrat(pargs=None):
    args = parse_args(pargs)

    cerebro = bt.Cerebro()
    # cerebro.broker.set_cash(args.cash)
    cerebro.broker.set_cash(1200000)

    df_0 = df_daily
    df_0['DT']= timestamp_to_datetime_2(df_0['MTS'])

    data0 = bt.feeds.PandasData(dataname=df_0, datetime='DT',high='HIGH',low='LOW',close='CLOSE',open='OPEN')

    # data0 = bt.feeds.YahooFinanceData(
    #     dataname=args.data,
    #     fromdate=datetime.datetime.strptime(args.fromdate, '%Y-%m-%d'),
    #     todate=datetime.datetime.strptime(args.todate, '%Y-%m-%d'))
    cerebro.adddata(data0)

    cerebro.addstrategy(vi_strategy, **(eval('dict(' + args.strat + ')')))
    cerebro.addsizer(bt.sizers.FixedSize, stake=args.stake)

    cerebro.run()
    if args.plot:
        cerebro.plot(**(eval('dict(' + args.plot + ')')))

def parse_args(pargs=None):

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='sigvicross')

    parser.add_argument('--data', required=False, default='tBTCUSD',
                        help='tBTCUSD ticker')

    parser.add_argument('--fromdate', required=False, default='2013-04-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', required=False, default='2021-10-01',
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--cash', required=False, action='store', type=float,
                        default=10000, help=('Starting cash'))

    parser.add_argument('--stake', required=False, action='store', type=int,
                        default=1, help=('Stake to apply'))

    parser.add_argument('--strat', required=False, action='store', default='',
                        help=('Arguments for the strategy'))

    parser.add_argument('--plot', '-p', nargs='?', required=False,
                        metavar='kwargs', const='{}',
                        help=('Plot the read data applying any kwargs passed\n'
                              '\n'
                              'For example:\n'
                              '\n'
                              '  --plot style="candle" (to plot candles)\n'))

    return parser.parse_args(pargs)

async def main():
    c = await db.db_connect() 
    global df_vi 
    global df_daily
    df_daily = await db.historical_candle_db_load()
    df_daily['DT']= timestamp_to_datetime_2(df_daily['MTS'])
    df_vi = await db.vi_db_load(c)
    c.commit()
    c.close()
    df_daily.set_index('DT')

    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

    df_2 = bt.feeds.PandasData(dataname=df_daily, datetime='DT',high='HIGH',low='LOW',close='CLOSE',open='OPEN')
    cerebro.adddata(df_2)  # Add the data feed
    cerebro.addstrategy(vi_strategy)  # Add the trading strategy
    cerebro.run()  # run it all
    cerebro.plot()  # and plot it with a single command

    
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())