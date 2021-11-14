import sqlite3

import pandas as pd
from ta import add_all_ta_features
from ta.utils import dropna
from ta import trend

async def calc_VI(df):
    df = dropna(df)
    # df = add_all_ta_features(
        # df, open="OPEN", high="HIGH", low="LOW", close="CLOSE", volume="VOLUME")
    vi= trend.VortexIndicator(high=df["HIGH"], low=df["LOW"], close=df["CLOSE"],
            window=14, fillna=True)
    df['VI_DIFF'] = vi.vortex_indicator_diff()
    df['VI_POS'] = vi.vortex_indicator_pos()
    df['VI_NEG'] = vi.vortex_indicator_neg()
    return df

async def VI_signal(df):
    df = dropna(df)
    # df = add_all_ta_features(
        # df, open="OPEN", high="HIGH", low="LOW", close="CLOSE", volume="VOLUME")
    vi= trend.VortexIndicator(high=df["HIGH"], low=df["LOW"], close=df["CLOSE"],
            window=14, fillna=True)
    df['VI_DIFF'] = vi.vortex_indicator_diff()
    df['VI_POS'] = vi.vortex_indicator_pos()
    df['VI_NEG'] = vi.vortex_indicator_neg()
    return df

async def sort_ascending(df):
    return df 

async def calc_vortex(df):
    return

async def write_vortex(c,df):
    return

