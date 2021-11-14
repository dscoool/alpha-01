from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
import db
import pandas as pd
import sqlite3
import datetime
def timestamp_to_datetime_2(timestamp):
  ts_series = timestamp.apply(lambda x: (datetime.datetime.fromtimestamp(x/1000)))
  return ts_series

def historical_candle_db_load():
    # f = (etfcode,modify_date)
    col_historical_candle = ['MTS','DATETIME','OPEN','CLOSE','HIGH','LOW','VOLUME']

    conn = sqlite3.connect("./db/alpha_01.db") 
    cur = conn.cursor() 
    cur.execute("SELECT MTS, DATETIME, OPEN, CLOSE, HIGH, LOW, VOLUME FROM HISTORICAL_CANDLES ORDER BY MTS ASC") 
    rows = cur.fetchall() 
    df_hc=pd.DataFrame(rows, columns=col_historical_candle)
    conn.close()
        
    return df_hc

def vi_db_load(c):
    # f = (etfcode,modify_date)
    col_historical_candle = ['MTS','DATETIME','OPEN','CLOSE','HIGH','LOW','VOLUME','VI_DIFF','VI_POS','VI_NEG']

    conn = sqlite3.connect("./db/alpha_01.db") 
    cur = conn.cursor() 
    cur.execute("SELECT MTS, DATETIME, OPEN, CLOSE, HIGH, LOW, VOLUME, VI_DIFF, VI_POS, VI_NEG FROM VI ORDER BY MTS ASC") 
    rows = cur.fetchall() 
    df=pd.DataFrame(rows, columns=col_historical_candle)
    conn.close() 
        
    return df

def db_connect():
    con = sqlite3.connect("./db/alpha_01.db")
    # type(con)
    sqlite3.Connection
    print("DB connected : alpha_01.db")
    return con


c = db_connect() 
# global df_vi 
# global df_daily
# LOAD DAILY
df_daily = historical_candle_db_load()
df_daily['DT']= timestamp_to_datetime_2(df_daily['MTS'])
df_daily.set_index('DT')
#LOAD VI
df_vi = vi_db_load(c)

c.commit()
c.close()
    
class vi_strategy(Strategy):
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
from backtesting.lib import SignalStrategy, TrailingStrategy


class SmaCross(SignalStrategy,
               TrailingStrategy):
    n1 = 10
    n2 = 25
    
    def init(self):
        # In init() and in next() it is important to call the
        # super method to properly initialize the parent classes
        super().init()
        
        # Precompute the two moving averages
        sma1 = self.I(SMA, self.data.Close, self.n1)
        sma2 = self.I(SMA, self.data.Close, self.n2)
        
        # Where sma1 crosses sma2 upwards. Diff gives us [-1,0, *1*]
        signal = (pd.Series(sma1) > sma2).astype(int).diff().fillna(0)
        signal = signal.replace(-1, 0)  # Upwards/long only
        
        # Use 95% of available liquidity (at the time) on each order.
        # (Leaving a value of 1. would instead buy a single share.)
        entry_size = signal * .95
                
        # Set order entry sizes using the method provided by 
        # `SignalStrategy`. See the docs.
        self.set_signal(entry_size=entry_size)
        
        # Set trailing stop-loss to 2x ATR using
        # the method provided by `TrailingStrategy`
        self.set_trailing_sl(2)
class vi_strategy(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()


bt = Backtest(GOOG, vi_strategy,
              cash=10000, commission=.002,
              exclusive_orders=True)

output = bt.run()
bt.plot()