from __future__ import (absolute_import, division, print_function, unicode_literals)
import datetime
import asyncio
import os
import argparse
import get_public_data
import coinone_01
import vars
import pandas as pd
import time
import db
import vortex
import backtrader as bt
import argparse

#데이터 제대로 feed 되었는가?
#signal 제대로 만들어 졌는가?
#모델링 제대로 되었는가?

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

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        # print(type(sma1))
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONGSHORT, crossover)
#STOCHRSI

class StochrsiCross(bt.SignalStrategy):
    def __init__(self):
        srsi_k,srsi_d = bt.talib.STOCHRSI(self.data)
        self.crossdown = bt.ind.CrossDown(srsi_k, srsi_d)
#strategy 00
class vi_strategy(bt.Strategy):
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
        vi_plus = bt.ind.Vortex(self.data).vi_plus
        vi_minus = bt.ind.Vortex(self.data).vi_minus
        crossover = bt.ind.CrossOver(vi_plus, vi_minus)
        self.crossup = bt.ind.CrossUp(vi_plus, vi_minus)
        self.crossdown = bt.ind.CrossDown(vi_plus,vi_minus)
        # exit = 0
        # self.signal_add(bt.SIGNAL_LONGSHORT, crossover)
        self.signal_add(bt.SIGNAL_LONG, self.crossup)
        self.signal_add(bt.SIGNAL_LONGEXIT, self.crossdown)
        # self.signal_add(bt.SIGNAL_SHORT, crossdown)
        # # self.signal_add(bt.SIGNAL_LONGEXIT, exit)

# kwargs = dict(
#         timeframe=bt.TimeFrame.Minutes,
#         compression=30,
#         sessionstart=datetime(2021,1,1),
#         sessionend=datetime(2021, 10,2),
#     )

def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='')

    parser.add_argument('--data', required=False, default='tBTCUSD',
                        help='tBTCUSD ticker')

    parser.add_argument('--fromdate', required=False, default='2013-04-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', required=False, default='2020-10-01',
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--cash', required=False, action='store', type=float,
                        default=10000, help=('Starting cash'))

    parser.add_argument('--stake', required=False, action='store', type=int,
                        default=0.001, help=('Stake to apply'))

    parser.add_argument('--strat', required=False, action='store', default='',
                        help=('Arguments for the strategy'))
    parser.add_argument('--broker', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--sizer', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')
    parser.add_argument('--plot', '-p', nargs='?', required=False,
                        metavar='kwargs', const='{}',
                        help=('Plot the read data applying any kwargs passed\n'
                              '\n'
                              'For example:\n'
                              '\n'
                              '  --plot style="candle" (to plot candles)\n'))

    return parser.parse_args(pargs)

# class VortexExitSignal(bt.Indicator): #buy했으나 긴급상황시 포지션 정리 (sell)
#     def __init__(self):
#         #손실률 넣기 1%이상 손실시 포지션 정리
#         vi_plus = bt.ind.Vortex(self.data).vi_plus
#         vi_minus = bt.ind.Vortex(self.data).vi_minus
#         crossdown = bt.ind.CrossDown(vi_plus, vi_minus)
#         # self.signal_add(bt.SIGNAL_SHORT crossdown)
#         # sma1 = bt.indicators.SMA(period=self.p.p1)
#         # sma2 = bt.indicators.SMA(period=self.p.p2)
#         # self.lines.signal = sma1 - sma2

#buy, sell 제대로 됐는지 체크할 것 **

# 참조: https://github.com/mementum/backtrader/blob/master/samples/sigsmacross/sigsmacross.py

async def main(pargs=None):
    c = await db.db_connect() 
    global df_vi 
    global df_daily
    # LOAD DAILY
    df_hc = await db.historical_candle_db_load()
    df_hc['D1']= timestamp_to_datetime_2(df_hc['MTS']).apply(lambda x: datetime.datetime.strftime(x,format = "%Y-%m-%d"))
    df_hc['T1']= timestamp_to_datetime_2(df_hc['MTS']).apply(lambda x: datetime.datetime.strftime(x,format = "%H:%M:%S"))
    print(df_hc)

    filename_csv = datetime.datetime.today().strftime(format = "%Y%m%d%H")
    # print(filename_csv)
    df_hc.to_csv(os.path.join('./csv/',str(filename_csv+'.csv')))
    df_hc.set_index('MTS')
    # print(df_hc)
    #LOAD VI

    df_vi = await db.vi_db_load(c)
    df_vi.to_csv(os.path.join('./csv/',str(filename_csv+'_10'+'.csv')))

    c.commit()
    c.close()
    # BACKTESTING
    args = parse_args(pargs)
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(1200000.0) #1.2M
    cerebro.broker.setcommission(commission=0.002)

    df_daily_test=df_hc #1,000 recent records backtesting!!
    # print(df_daily_test)
    #start cerebro
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro = bt.Cerebro() 
    cerebro.broker.setcash(1200000.0) #1.2M
    cerebro.broker.setcommission(commission=0.002)
    df_0 = bt.feeds.GenericCSVData(
        nullvalue= float('NaN'),
        dataname=os.path.join('./csv/',str(filename_csv+'.csv')),
        datetime='DATETIME',
        time = 'T1',
        high='HIGH',
        low='LOW',
        close='CLOSE',
        open='OPEN',
        volume = 'VOLUME',
        openinterest=-1,
        timeframe = bt.TimeFrame.Minutes,
        dtformat=('%Y-%m-%d %H:%M:%S'),
        tmformat=('%H:%M:%S'),
        # sessionstart=datetime.datetime(2021,1,1,0,0,0),
        # sessionend=datetime.datetime(2021,10,2,23,59,00),
        compression=30
        )
    cerebro.adddata(df_0)
    # cerebro.resampledata(df_0,timeframe=bt.TimeFrame.Minutes,compression=30)
    # Broker
    # cerebro.broker = bt.brokers.BackBroker(**eval('dict(' + args.broker + ')'))
    # Sizer
    # cerebro.addsizer(bt.sizers.FixedSize, **eval('dict(' + args.sizer + ')'))

    #strategy
    cerebro.addstrategy(vi_strategy)
    # cerebro.addstrategy(vi_strategy, **(eval('dict(' + args.strat + ')')))

    # cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Months)
    # cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years)
    # cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)

    # if args.exitsignal is not None:
    #     cerebro.add_signal(EXITSIGNALS[args.exitsignal],
    #                        SMAExitSignal,
    #                        p1=args.exitperiod,
    #                        p2=args.smaperiod)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()  # and plot it with a single command


  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())