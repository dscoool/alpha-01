import datetime
import matplotlib.pyplot as plt
import asyncio
import get_public_data
import coinone_01
import vars
import datetime
import pandas as pd
import time
import db
from zipline.api import order, symbol

def initialize(context):
    pass


def handle_data(context, data):
    order(symbol('tBTCUSD'), 1)

async def main():
  #db connection
  c = await db.db_connect() #db connect
  df_daily=await db.historical_candle__daily_db_load()
#   plt.plot(df_daily['MTS'], df_daily['CLOSE'])
#   plt.show()
  df_close = pd.DataFrame(df_daily['DATETIME'],df_daily['CLOSE'])
  df_close.head()
  c.commit()
  c.close() 
    
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
