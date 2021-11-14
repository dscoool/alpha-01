import sqlite3 
import pandas as pd
conn = sqlite3.connect("./db/alpha_01.db") 
cur = conn.cursor() 
cur.execute("SELECT * FROM HISTORICAL_CANDLES") 
rows = cur.fetchall() 
df=pd.DataFrame(rows)
print(df) 
conn.close()