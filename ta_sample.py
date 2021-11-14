import pandas as pd
from ta.utils import dropna
from ta.trend import VortexIndicator
from time import strftime
from datetime import datetime
# Load datas
df = pd.read_csv('btcusd_2021-10-01.csv', sep=',')

# Clean NaN values
df = dropna(df)

# Initialize Bollinger Bands Indicator
vortex_indicator = VortexIndicator(high=df["HIGH"], low=df["LOW"], close=df["CLOSE"],
    window=14, fillna=False)




# Add Bollinger Bands features
df['DT']=df['MTS'].apply(lambda x: datetime.fromtimestamp(x/1000))
# df['DT_TEXT']= df['MTS'].dt.strftime('%Y-%m-%d-%H:%M:%S')
df['VI_POS'] = vortex_indicator.vortex_indicator_pos() # time_period= 14
df['VI_NEG'] = vortex_indicator.vortex_indicator_neg()
df['VI_DIFF']=vortex_indicator.vortex_indicator_diff()

print(df['DT'])