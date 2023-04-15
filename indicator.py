import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import argrelextrema
import io
import requests


# for greater simplicity install our package
# https://github.com/twelvedata/twelvedata-python

def getcandle_csv(symbol = "XAU/USD",timeframe = "1h",num = 400):
    token = '3ac243c6f2db45bd98cd7f3538557043'
    response = requests.get(f"https://api.twelvedata.com/time_series?apikey={token}&interval={timeframe}&symbol={symbol}&outputsize={num}&format=CSV")
    data_file = io.StringIO(response.text)
    df = pd.read_csv(data_file, sep=';')
    #write to file
    df.to_csv('data.csv', index=False)
    return df
    
def KeyLevel(dataframe, timeframe = "1h", beetwen = 5):
    candle = pd.DataFrame(dataframe)
    lst_idmax_base = []
    lst_idmin_base = []

    minloc = candle.iloc[argrelextrema(candle["close"].values, np.less_equal, order=beetwen)[0]]
    maxloc = candle.iloc[argrelextrema(candle["close"].values, np.greater_equal, order=beetwen)[0]]
  
    plt.plot(minloc["close"], 'r.', label="H1")
    plt.plot(maxloc["close"], 'g.', label="H1")
    plt.plot(candle["close"])
    plt.show()

    frame_merge = pd.concat([minloc, maxloc])
    return frame_merge

#main
if __name__ == "__main__":
    #getcandle_csv()
    df = pd.read_csv('data.csv')
    df_key = KeyLevel(df)
    print(df_key)