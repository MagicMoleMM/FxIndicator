import pandas as pd
import numpy.polynomial.polynomial as poly
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots


tickers = 'EURUSD=X'

#  Загружаем данные

# data_1H_load = yf.download(tickers =tickers, period ='1mo', interval = '1h')
# data_1d_load = yf.download(tickers =tickers, period ='1y', interval = '1d')

# data_1H_read = pd.DataFrame(data_1H_load)
# data_1d_read = pd.DataFrame(data_1d_load)

# data_1H_read.to_csv(f'{tickers}_1H.csv')
# data_1d_read.to_csv(f'{tickers}_1d.csv')

# Читаем данные

data_1H = pd.read_csv(f'{tickers}_1H.csv')
data_1d = pd.read_csv(f'{tickers}_1d.csv')

data_1H.set_index('Unnamed: 0', inplace=True)
data_1d.set_index('Date', inplace=True)

# Рассчитываем полином и Osma

data_1H_poly = list()
data_1d_poly = list()

data_1H_poly_f = list()
data_1d_poly_f = list()

i = 0

def get_polinom(price, lenght, deg, data_list):

    for i in range(len(price)-lenght, 1, -1):

        y = list(price[(-lenght-i):(-i)])
        x = list(range(0, len(y)))
        poly_fit = poly.Polynomial.fit(x, y, deg)(lenght)
        data_list.append(poly_fit)
        
    dt_poly = pd.Series(data_list)
    dt_poly.reset_index(drop=True)
    dt_poly.set_axis(price.index[-(len(price)-lenght-1):], axis=0, inplace=True)

    return dt_poly

def get_polinom_f(price, lenght, deg, data_list):

    for i in range(len(price)-lenght, 1, -1):

        y = list(price[(-lenght-i-1):(-i-1)])
        x = list(range(0, len(y)))
        poly_fit = poly.Polynomial.fit(x, y, deg)(lenght)
        data_list.append(poly_fit)
        
    dt_poly = pd.Series(data_list)
    dt_poly.reset_index(drop=True)
    dt_poly.set_axis(price.index[-(len(price)-lenght-1):], axis=0, inplace=True)

    return dt_poly

def get_macd(price, slow, fast, smooth):

    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=smooth, adjust=False).mean()
    hist = macd - signal
    frames = [macd, signal, hist]
    df = pd.DataFrame(frames).T
    df = df.set_axis(['MACD', 'Signal', 'Hist'], axis='columns', inplace=False)
    return df

# Получаем значения индикаторов (полином и Osma)

poly_1H_res = get_polinom(data_1H['Close'], 50, 2, data_1H_poly)
poly_1d_res = get_polinom(data_1d['Close'], 50, 2, data_1d_poly)

poly_1H_f = get_polinom_f(data_1H['Close'], 50, 2, data_1H_poly_f)
poly_1d_f = get_polinom_f(data_1d['Close'], 50, 2, data_1d_poly_f)

delta_1H = poly_1H_res - poly_1H_f
delta_1d = poly_1d_res - poly_1d_f

macd_1H = get_macd(poly_1H_res, 26, 12, 9)
macd_1d = get_macd(poly_1d_res, 26, 12, 9)


# Строим график

fig = make_subplots(rows=3, cols=2, row_heights=[0.3, 0.1, 0.6], column_widths=[0.5, 0.5])

fig.append_trace(go.Candlestick(x=data_1H.index,
                open=data_1H['Open'],
                high=data_1H['High'],
                low=data_1H['Low'],
                close=data_1H['Close'], name = 'market data_1H'), row=3, col=1)

fig.append_trace(go.Scatter(x=poly_1H_res.index, y=poly_1H_res, mode='lines', name='Polynom_1H'),row=3, col=1)
fig.append_trace(go.Scatter(x=poly_1H_f.index, y=poly_1H_f, mode='lines', name='Polynom_f_1H'), row=3, col=1)

fig.append_trace(go.Bar(x=macd_1H['Hist'].index, 
                        y=macd_1H['Hist'], 
                        marker=dict(color =macd_1H['Hist'], colorscale='RdYlGn'),
                        name='Osma_1H'), 
                        row=1, col=1)

fig.append_trace(go.Scatter(x=delta_1H.index, 
                            y=delta_1H, 
                            line=dict(color ='#5aba47'),
                            mode='lines', 
                            # marker=dict(size=8, color=delta_1H, colorscale='RdYlGn'),
                            name='Delta_1H'), 
                            row=1, col=1)


fig.append_trace(go.Candlestick(x=data_1d.index,
                open=data_1d['Open'],
                high=data_1d['High'],
                low=data_1d['Low'],
                close=data_1d['Close'], name = 'market data_1D'), row=3, col=2)

fig.append_trace(go.Scatter(x=poly_1d_res.index, y=poly_1d_res, mode='lines', name='Polynom_1d'),row=3, col=2)
fig.append_trace(go.Scatter(x=poly_1d_f.index, y=poly_1d_f, mode='lines', name='Polynom_f_1d'), row=3, col=2)

fig.append_trace(go.Bar(x=macd_1d['Hist'].index, 
                        y=macd_1d['Hist'], 
                        marker=dict(color =macd_1d['Hist'], colorscale='RdYlGn'), 
                        name='Osma_1d'), 
                        row=1, col=2)

fig.append_trace(go.Scatter(x=delta_1d.index, 
                            y=delta_1d,
                            line=dict(color ='#5788c9'), 
                            mode='lines', 
                            name='Delta_1d'), 
                            row=1, col=2)


fig.update_layout(title=f'{tickers}',
                  margin=dict(l=100, r=100, t=50, b=50),
                  hovermode="x",
                  legend_orientation="v",
                )


fig.update_xaxes(
        rangeslider_visible=True,
        rangebreaks=[dict(bounds=["sat", "mon"])],
        # zeroline=True, zerolinewidth=2, zerolinecolor='#000000',
    )
# fig.update_xaxes(
#         rangeslider_visible=True,
#         rangebreaks=[dict(bounds=["sat", "mon"])],
#         row=5
#     )

fig.show()
