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
        trailamount=1000,
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
    # params = (('period_me1', 12), ('period_me2', 26), ('period_signal', 9),)
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

def sma(price, period):
    sma = price.rolling(period).mean()
    return sma

def aweosc(price, period1, period2):
    # print(type(price))
    median = price.MovingAverageSimple(period=2).median() #2일간 주가평균
    short = sma(median, period1)
    long = sma(median, period2)
    ao = short - long
    ao_df = DataFrame(ao).rename(columns = {'Close':'ao'})
    return ao_df


class Awesome_Indicator(bt.Indicator):
    alias = ('AO','AwesomeOsc')
    lines = ('ao',)

    params = (('period1', 5),('period2',34))
    plotlines = dict(ao=dict(_method='bar', alpha=0.50, width=1.0))

    def __init__(self):
        self.lines.ao = aweosc(self.data.close, self.params.period1, self.params.period2)
        super(Awesome_Indicator, self).__init__()



class AwesomeOSC_Sell(bt.SignalStrategy):
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
        self.lines = bt.ind.AwesomeOscillator(self.data).ao
        print(self.lines(-1))
        # self.d1=DownMove2(self.lines).downmove
        # self.d2=DownMove2(self.lines).downmove2
        # print(self.d1, self.d2)
        # self.two_downmove= self.d1 <0 

        # self.signal_add(bt.SIGNAL_LONGEXIT, self.two_downmove)
    def next(self):
        if DownMove2(self.lines).downmove > 0:
            self.close()

class VICrossUp(bt.SignalStrategy):
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
        vi_plus  = bt.ind.Vortex(self.data).vi_plus
        vi_minus = bt.ind.Vortex(self.data).vi_minus
        self.vi_crossup = bt.ind.CrossUp(vi_plus, vi_minus)
        self.vi_crossdown = bt.ind.CrossDown(vi_plus,vi_minus)
        self.signal_add(bt.SIGNAL_LONG, self.vi_crossup)
    def next(self):
        if self.vi_crossup > 0:
            self.buy()
        if self.vi_crossdown > 0:
            self.close()

#strategy 00
class vi_strategy2(bt.SignalStrategy):
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
        vi_plus  = bt.ind.Vortex(self.data).vi_plus
        vi_minus = bt.ind.Vortex(self.data).vi_minus
        self.vi_crossup = bt.ind.CrossUp(vi_plus, vi_minus)
        # self.vi_crossdown = bt.ind.CrossDown(vi_plus,vi_minus)
        self.signal_add(bt.SIGNAL_LONG, self.vi_crossup)
        # self.signal_add(bt.SIGNAL_LONGEXIT, self.vi_crossdown)
        self.vi_diff = vi_plus - vi_minus
        # self.sell_sig = bt.ind.DownMove(vi_diff)
        self.roc=bt.ind.ROC100(self.data)

        srsi_k = bt.talib.STOCHRSI(self.data, timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=0).fastk
        srsi_d = bt.talib.STOCHRSI(self.data, timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=0).fastd
        self.srsi_crossdown = bt.ind.CrossDown(srsi_k,srsi_d) # k crosses down d -> longexit
        self.signal_add(bt.SIGNAL_LONGEXIT, self.srsi_crossdown)
        # self.signal_add(bt.SIGNAL_LONGEXIT, self.vi_diff)
    def next(self):
        if self.vi_crossup > 0:
            self.buy()
        elif self.srsi_crossdown > 0:
            self.close()
        elif self.roc < -0.001:
            self.close()
        elif self.vi_diff < 0:
            self.close()
        #sell 전략을 마련하자
        # AWESOME OSCILLATOR 파랑에서 빨강으로 갈 때 팔 것
        #vortex 미분값 (+)에서 (-)로 갈 때로 바꿀 것.

            


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
        #vi strategy
        vi_plus  = bt.ind.Vortex(self.data).vi_plus
        vi_minus = bt.ind.Vortex(self.data).vi_minus
        self.vi_crossup = bt.ind.CrossUp(vi_plus, vi_minus)
        self.signal_add(bt.SIGNAL_LONG, self.vi_crossup)

        # self.signal_add(bt.SIGNAL_LONGEXIT, srsi_crossdown)     
    def next(self):
        if self.vi_crossup > 0:
            self.buy()
        pass
        # elif self.sma < self.data.close:
        #     # Do something else
        #     pass
# kwargs = dict(
#         timeframe=bt.TimeFrame.Minutes,
#         compression=30,
#         sessionstart=datetime(2021,1,1),
#         sessionend=datetime(2021, 10,2),
#     )

