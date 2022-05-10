# from sklearn.preprocessing import PolynomialFeatures
from turtle import color
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly
import yfinance as yf
import plotly.graph_objs as go


tickers = 'EURUSD=X'
data = yf.download(tickers =tickers, period ='1wk', interval = '1h')
data_read = pd.DataFrame(data)
data_read.to_csv(f'{tickers}_1H.csv')
# print(data)

# declare figure
fig = go.Figure()

#Candlestick
fig.add_trace(go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'], name = 'market data'))

# Add titles
fig.update_layout(
    title='EUR/USD')

# Show
fig.show()

y_0 = list(data['Close'])
x_0 = list(range(0,len(y_0)))


y = list(data['Close'][-50:])
x = list(range(0,len(y)))

y_f = list(data['Close'][-51:][:-1])
x_f = list(range(0,len(y_f)))

polynom_1h = poly.Polynomial.fit(x, y, 2)
polynom_1h_f = poly.Polynomial.fit(x_f, y_f, 2)




def get_macd(price, slow, fast, smooth):
    
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span = smooth, adjust = False).mean()
    hist = macd - signal
    frames =  [macd, signal, hist]
    df = pd.DataFrame(frames).T
    df2 = df.set_axis(['MACD', 'Signal', 'Hist'], axis=1, inplace=True)
    return df

def plot_macd(prices, macd, hist):
    ax1 = plt.subplot2grid((8,1), (0,0), rowspan = 5, colspan = 1)
    ax2 = plt.subplot2grid((8,1), (5,0), rowspan = 3, colspan = 1)

    ax1.plot(prices)
    ax2.plot(macd, color = 'blue', linewidth = 1.5, label = 'MACD')
    ax2.plot(hist, color = 'red', linewidth = 1.5, label = 'HIST')
    plt.axhline(0, color='grey')
    plt.legend(loc = 'lower left')


dt = get_macd(data['Close'], 26, 12, 9)
print(dt)
plot_macd(data['Close'], dt['MACD'], dt['Hist'])

plt.show()


# use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        # period = "ytd",

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        # interval = "1m",
