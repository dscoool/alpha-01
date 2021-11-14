import backtrader as bt
from numpy import diff 
from backtrader.indicators import EMA, AwesomeOscillator, Indicator, And, If, MovAv, ATR
from pandas import DataFrame
import pandas
class St(bt.Strategy): #stop trail - stoploss / not percent, stop trail by amount
    params = dict(
        ma=bt.ind.SMA,
        p1=10,
        p2=30,
        stoptype=bt.Order.StopTrail,
        trailamount=200,
        trailpercent=1.0,
        limitoffset=0.0,
    )

    def __init__(self):
        ma1, ma2 = self.p.ma(period=self.p.p1), self.p.ma(period=self.p.p2)
        self.crup = bt.ind.CrossUp(ma1, ma2)
        self.order = None

    def next(self):
        if not self.position:
            if self.crup:
                o = self.buy()
                self.order = None
                print('*' * 50)

        elif self.order is None:
            if self.p.stoptype == bt.Order.StopTrailLimit:
                price = self.data.close[0]
                plimit = self.data.close[0] + self.p.limitoffset
            else:
                price = None
                plimit = None

            self.order = self.sell(exectype=self.p.stoptype,
                                   price=price,
                                   plimit=plimit,
                                   trailamount=self.p.trailamount,
                                   trailpercent=self.p.trailpercent)

            if self.p.trailamount:
                tcheck = self.data.close - self.p.trailamount
            else:
                tcheck = self.data.close * (1.0 - self.p.trailpercent)
            print(','.join(
                map(str, [self.datetime.date(), self.data.close[0],
                          self.order.created.price, tcheck])
                )
            )
            print('-' * 10)
        else:
            if self.p.trailamount:
                tcheck = self.data.close - self.p.trailamount
            else:
                tcheck = self.data.close * (1.0 - self.p.trailpercent)
            print(','.join(
                map(str, [self.datetime.date(), self.data.close[0],
                          self.order.created.price, tcheck])
                )
            )

class sell_AO(bt.SignalStrategy):
    lines = ('line',)
    params = (('period', 14),)

    # lines = ('macd', 'signal', 'histo',)
    # params = (('period_me1', 12), ('p(eriod_me2', 26), ('period_signal', 9),)
    def __init__(self):
        self.line = bt.ind.AwesomeOscillator().ao
        # self.lines.signal = bt.ind.CrossUp(vi_plus, vi_minus)
        # self.lines.signal=ao.ao    
        print(self.line._method)
        print(self.line.alpha)
        print(self.line.width)
        self.sell=bt.ind.DownMove(self.line)
        # self.lines.signal=ao.width
        self.signal_add(bt.SIGNAL_LONGEXIT, self.sell)
    def next(self):
        if (self.line > 0 & self.sell > 0):
            self.close()
        
class SmaCross(bt.SignalStrategy):
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
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        # print(type(sma1))
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONGSHORT, crossover)

#STOCHRSI
class StochrsiCross(bt.SignalStrategy):
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
        srsi_k = bt.talib.STOCHRSI(self.data, timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=0).fastk
        srsi_d = bt.talib.STOCHRSI(self.data, timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=0).fastd
        self.crossdown = bt.ind.CrossDown(srsi_k, srsi_d) # k crosses down d -> longexit
        self.signal_add(bt.SIGNAL_SHORT, self.crossdown)
#전략 문제임.

class AwesomeOSC_Downward(bt.SignalStrategy):
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
        lines = ('ao',)
        self.ao = bt.ind.AwesomeOscillator(self.data)
        self.d1=D2(self.ao).downmove

        # self.signal_add(bt.SIGNAL_LONGEXIT, self.lines)
    def next(self):
        if self.ao >0 and self.d1>0:
            self.close()
        # pass

class VICross(bt.SignalStrategy):
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
    lines = ('signal',)
    params = (('period', 14),)

    def __init__(self):
        lines = ('vi_crossup', 'vi_crossdown','oscillator',)
        self.vi_plus  = bt.ind.Vortex(self.data).vi_plus
        self.vi_minus = bt.ind.Vortex(self.data).vi_minus
        self.vi_crossup = bt.ind.CrossUp(self.vi_plus, self.vi_minus)
        self.vi_crossdown = bt.ind.CrossDown(self.vi_plus,self.vi_minus)
        # self.signal_add(bt.SIGNAL_LONG, self.vi_crossup)

        self.oscillator= bt.ind.AwesomeOscillator(self.data)
        self.osc_red=bt.ind.DownMove(self.oscillator.ao)
        self.osc_green=bt.ind.UpMove(self.oscillator.ao)
    def next(self):
        #vi_crossup > 0 and three consecutive AO is green
        if (self.vi_crossup > 0) and (self.osc_green[-3] >0) and (self.osc_green[-2] >0) and (self.osc_green[-1] > 0):
            print(self.osc_green[-1], self.osc_red[-1])
            self.buy()      
        if self.vi_crossdown > 0:
            self.close()
        # if ((self.oscillator.ao[-2] - self.oscillator.ao[-1] > 0) and (self.oscillator.ao[-3]-self.oscillator.ao[-2] > 0) and (self.oscillator.ao[-1] > 0) and (self.vi_plus[-1]-self.vi_minus[-1]>0)):
        #     self.close()



class VI2(bt.SignalStrategy):
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
    lines = ('signal',)
    params = (('period', 14),)

    def __init__(self):
        lines = ('vi_crossup', 'vi_crossdown','oscillator',)
        self.vi_plus  = bt.ind.Vortex(self.data).vi_plus
        self.vi_minus = bt.ind.Vortex(self.data).vi_minus
        self.vi_crossup = bt.ind.CrossUp(self.vi_plus, self.vi_minus)
        self.vi_crossdown = bt.ind.CrossDown(self.vi_plus,self.vi_minus)
        # self.signal_add(bt.SIGNAL_LONG, self.vi_crossup)

        self.oscillator= bt.ind.AwesomeOscillator(self.data)
        # self.ad = 
    def next(self):
        #vi_crossup > 0 and three consecutive AO is green
        if (self.vi_crossdown > 0) and (abs(self.oscillator) < 300):
            self.buy()      
        # if (self.ad > 2.0):
        #     self.close()

