import pandas as pd
import numpy.polynomial.polynomial as poly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import AlphaVantage as av
import time


from_symbol = 'AUD'
to_symbol = 'USD'
interval = '60min'  # 1min, 5min, 15min, 30min, 60min
outputsize = 'compact'  # Optional compact or full
apikey = '2GGORTBXQIFSR2AF'

#  Загружаем данные

data_1h_load = av.get_fx_intraday(
    from_symbol, to_symbol, interval, outputsize, apikey)
data_1d_load = av.get_fx_daily(from_symbol, to_symbol, outputsize, apikey)

data_1h_load.to_csv(f'Data_fx/{from_symbol}{to_symbol}_1h.csv')
data_1d_load.to_csv(f'Data_fx/{from_symbol}{to_symbol}_1d.csv')

# Читаем данные

data_1h = pd.read_csv(f'Data_fx/{from_symbol}{to_symbol}_1h.csv')
data_1d = pd.read_csv(f'Data_fx/{from_symbol}{to_symbol}_1d.csv')
data_1h = data_1h.iloc[::-1]
data_1d = data_1d.iloc[::-1]

data_1h.set_index('timestamp', inplace=True)
data_1d.set_index('timestamp', inplace=True)

# Рассчитываем полином и Osma

data_1h_poly = list()
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
    dt_poly.set_axis(
        price.index[-(len(price)-lenght-1):], axis=0, inplace=True)

    return dt_poly


def get_polinom_f(price, lenght, deg, data_list):

    for i in range(len(price)-lenght, 1, -1):

        y = list(price[(-lenght-i-1):(-i-1)])
        x = list(range(0, len(y)))
        poly_fit = poly.Polynomial.fit(x, y, deg)(lenght)
        data_list.append(poly_fit)

    dt_poly = pd.Series(data_list)
    dt_poly.reset_index(drop=True)
    dt_poly.set_axis(
        price.index[-(len(price)-lenght-1):], axis=0, inplace=True)

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


poly_1h_res = get_polinom(data_1h['close'], 50, 2, data_1h_poly)
poly_1d_res = get_polinom(data_1d['close'], 50, 2, data_1d_poly)

poly_1h_f = get_polinom_f(data_1h['close'], 50, 2, data_1H_poly_f)
poly_1d_f = get_polinom_f(data_1d['close'], 50, 2, data_1d_poly_f)

delta_1h = poly_1h_res - poly_1h_f
delta_1d = poly_1d_res - poly_1d_f

macd_1h = get_macd(poly_1h_res, 26, 12, 9)
macd_1d = get_macd(poly_1d_res, 26, 12, 9)


#  Условие


def signal_short_term():

    # Открыть длинную позицию

    if delta_1h.tail(1)[0] > 0 and delta_1h.tail(2)[0] < 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] > 0:

        return f'{from_symbol}/{to_symbol} краткосрок - открыть длинную позицию по цене {data_1h["close"].tail(1)[0]}'

    elif delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] < macd_1h['Hist'].tail(3)[0] and macd_1h['MACD'].tail(1)[0] > 0:

        return f'{from_symbol}/{to_symbol} краткосрок - открыть длинную позицию по цене {data_1h["close"].tail(1)[0]}'

    elif delta_1h.tail(1)[0] > 0 and delta_1h.tail(2)[0] < 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] < macd_1h['Hist'].tail(3)[0] and macd_1h['MACD'].tail(1)[0] > 0:

        return f'{from_symbol}/{to_symbol} краткосрок - открыть длинную позицию по цене {data_1h["close"].tail(1)[0]}'

    # Открыть короткую позицию

    elif delta_1h.tail(1)[0] < 0 and delta_1h.tail(2)[0] > 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] < 0:

        return f'{from_symbol}/{to_symbol} краткосрок - открыть короткую позицию по цене {data_1h["close"].tail(1)[0]}'

    elif delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] > macd_1h['Hist'].tail(3)[0] and macd_1h['MACD'].tail(1)[0] < 0:

        return f'{from_symbol}/{to_symbol} краткосрок - открыть короткую позицию по цене {data_1h["close"].tail(1)[0]}'

    elif delta_1h.tail(1)[0] < 0 and delta_1h.tail(2)[0] > 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] > macd_1h['Hist'].tail(3)[0] and macd_1h['MACD'].tail(1)[0] < 0:

        return f'{from_symbol}/{to_symbol} краткосрок - открыть короткую позицию по цене {data_1h["close"].tail(1)[0]}'

    # закрыть длинную пощицию

    elif delta_1h.tail(1)[0] < 0 and delta_1h.tail(2)[0] > 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0]:

        return f'{from_symbol}/{to_symbol} краткосрок - закрыть длинную позицию по цене {data_1h["close"].tail(1)[0]}'

    elif delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] > macd_1h['Hist'].tail(3)[0]:

        return f'{from_symbol}/{to_symbol} краткосрок - закрыть длинную позицию по цене {data_1h["close"].tail(1)[0]}'

    elif delta_1h.tail(1)[0] < 0 and delta_1h.tail(2)[0] > 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] > macd_1h['Hist'].tail(3)[0]:

        return f'{from_symbol}/{to_symbol} краткосрок - закрыть длинную позицию по цене {data_1h["close"].tail(1)[0]}'

    # закрыть короткую позицию

    elif delta_1h.tail(1)[0] > 0 and delta_1h.tail(2)[0] < 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0]:

        return f'{from_symbol}/{to_symbol} краткосрок - закрыть короткую позицию по цене {data_1h["close"].tail(1)[0]}'

    elif delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] < macd_1h['Hist'].tail(3)[0]:

        return f'{from_symbol}/{to_symbol} краткосрок - закрыть короткую позицию по цене {data_1h["close"].tail(1)[0]}'

    elif delta_1h.tail(1)[0] > 0 and delta_1h.tail(2)[0] < 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] < macd_1h['Hist'].tail(3)[0]:

        return f'{from_symbol}/{to_symbol} краткосрок - закрыть короткую позицию по цене {data_1h["close"].tail(1)[0]}'

    else:
        return f'{from_symbol}/{to_symbol} краткосрок - нет сигналов'

def signal_long_term():

    # Открыть длинную позицию

    if delta_1d.tail(1)[0] > 0 and delta_1d.tail(2)[0] < 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] > 0:

        return f'{from_symbol}/{to_symbol} долгосрок - открыть длинную позицию по цене закрытия дня'

    elif delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] < macd_1d['Hist'].tail(3)[0] and macd_1d['MACD'].tail(1)[0] > 0:

        return f'{from_symbol}/{to_symbol} долгосрок - открыть длинную позицию по цене закрытия дня'

    elif delta_1d.tail(1)[0] > 0 and delta_1d.tail(2)[0] < 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] < macd_1d['Hist'].tail(3)[0] and macd_1d['MACD'].tail(1)[0] > 0:

        return f'{from_symbol}/{to_symbol} долгосрок - открыть длинную позицию по цене закрытия дня'

    # Открыть короткую позицию

    elif delta_1d.tail(1)[0] < 0 and delta_1d.tail(2)[0] > 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] < 0:

        return f'{from_symbol}/{to_symbol} долгосрок - открыть короткую позицию по цене по цене закрытия дня'

    elif delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] > macd_1d['Hist'].tail(3)[0] and macd_1d['MACD'].tail(1)[0] < 0:

        return f'{from_symbol}/{to_symbol} долгосрок - открыть короткую позицию по цене закрытия дня'

    elif delta_1d.tail(1)[0] < 0 and delta_1d.tail(2)[0] > 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] > macd_1d['Hist'].tail(3)[0] and macd_1d['MACD'].tail(1)[0] < 0:

        return f'{from_symbol}/{to_symbol} долгосрок - открыть короткую позицию по цене закрытия дня'

    # закрыть длинную пощицию

    elif delta_1d.tail(1)[0] < 0 and delta_1d.tail(2)[0] > 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0]:

        return f'{from_symbol}/{to_symbol} долгосрок - закрыть длинную позицию по цене закрытия дня'

    elif delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] > macd_1d['Hist'].tail(3)[0]:

        return f'{from_symbol}/{to_symbol} долгосрок - закрыть длинную позицию по цене закрытия дня'

    elif delta_1d.tail(1)[0] < 0 and delta_1d.tail(2)[0] > 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] > macd_1d['Hist'].tail(3)[0]:

        return f'{from_symbol}/{to_symbol} долгосрок - закрыть длинную позицию по цене закрытия дня'

    # закрыть короткую позицию

    elif delta_1d.tail(1)[0] > 0 and delta_1d.tail(2)[0] < 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0]:

        return f'{from_symbol}/{to_symbol} долгосрок - закрыть короткую позицию по цене закрытия дня'

    elif delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] < macd_1d['Hist'].tail(3)[0]:

        return f'{from_symbol}/{to_symbol} долгосрок - закрыть короткую позицию по цене закрытия дня'

    elif delta_1d.tail(1)[0] > 0 and delta_1d.tail(2)[0] < 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] < macd_1d['Hist'].tail(3)[0]:

        return f'{from_symbol}/{to_symbol} долгосрок - закрыть короткую позицию по цене закрытия дня'

    else:
        return f'{from_symbol}/{to_symbol} долгосрок - нет сигналов'

def status_short_term():

    if delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] > 0:
        return f'{from_symbol}/{to_symbol}: Держать длинную позицию краткосрочно.'

    elif delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] < 0:
        return f'{from_symbol}/{to_symbol}: Держать короткую позицию краткосрочно.'

    elif delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] > 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Коррекция к северному краткосрочному движению.'

    elif delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] < 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Начало краткосрочного роста (MACD < 0).'

    elif delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] < 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Нет явного направления.'

    elif delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] > 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Нет явного направления.'

    elif delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] > 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Начало краткосрочного снижения (MACD > 0).'

    elif delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['MACD'].tail(1)[0] < 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Коррекция к южному краткосрочному движению.'

    else:
        return f'{from_symbol}/{to_symbol}: Без позиции.'

def status_long_term():

    if delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] > 0:
        return f'{from_symbol}/{to_symbol}: Держать длинную позицию долгосрочно.'

    elif delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] < 0:
        return f'{from_symbol}/{to_symbol}: Держать короткую позицию долгосрочно.'

    elif delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] > 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Коррекция к северному долгосрочному движению.'

    elif delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] < 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Начало долгосрочного роста (MACD < 0).'

    elif delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] < 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Нет явного направления.'

    elif delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] > 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Нет явного направления.'

    elif delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] > 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Начало долгосрочного снижения (MACD > 0).'

    elif delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['MACD'].tail(1)[0] < 0:
        return f'{from_symbol}/{to_symbol}: Без позиции. Коррекция к южному долгосрочному движению.'

    else:
        return f'{from_symbol}/{to_symbol}: Без позиции.'


status_long = status_long_term()
signal_long = signal_long_term()
status_short = status_short_term()
signal_short = signal_short_term()

status =((f'{time.ctime(time.time())}\n\n{from_symbol}/{to_symbol} Долгосрочный статус -\n{status_long}\n{signal_long}\n\n{from_symbol}/{to_symbol} Краткосрочный статус -\n{status_short}\n{signal_short}'))
print(status)


# Строим график

fig = make_subplots(rows=2, cols=2, row_heights=[
                    0.4, 0.6], column_widths=[0.5, 0.5])

fig.append_trace(go.Candlestick(x=data_1h.index,
                                open=data_1h['open'],
    high=data_1h['high'],
    low=data_1h['low'],
    close=data_1h['close'], name = 'market data_1H'), row=2, col=1)

fig.append_trace(go.Scatter(x=poly_1h_res.index, y=poly_1h_res, mode='lines', name='Polynom_1H'), row=2, col=1)
fig.append_trace(go.Scatter(x=poly_1h_f.index, y=poly_1h_f,
                 mode='lines', name='Polynom_f_1H'), row=2, col=1)

fig.append_trace(go.Bar(x=macd_1h['Hist'].index,
                        y=macd_1h['Hist'],
                        marker=dict(color=macd_1h['Hist'], colorscale='RdYlGn'),
                        name='Osma_1H'),
                 row=1, col=1)

fig.append_trace(go.Bar(x=macd_1h['MACD'].index,
                        y=macd_1h['MACD'],
                        marker=dict(color=macd_1h['MACD'], colorscale='speed'),
                        name='MACD_1H'),
                        row=1, col=1)

fig.append_trace(go.Scatter(x=delta_1h.index,
                            y=delta_1h,
                            line=dict(color='#5aba47'),
                            mode='lines',
                            name='Delta_1H'),
                 row=1, col=1)

fig.append_trace(go.Candlestick(x=data_1d.index,
                                open=data_1d['open'],
    high=data_1d['high'],
    low=data_1d['low'],
    close=data_1d['close'], name = 'market data_1D'), row=2, col=2)

fig.append_trace(go.Scatter(x=poly_1d_res.index, y=poly_1d_res, mode='lines', name='Polynom_1d'), row=2, col=2)
fig.append_trace(go.Scatter(x=poly_1d_f.index, y=poly_1d_f,
                 mode='lines', name='Polynom_f_1d'), row=2, col=2)

fig.append_trace(go.Bar(x=macd_1d['Hist'].index,
                        y=macd_1d['Hist'],
                        marker=dict(color =macd_1d['Hist'], colorscale='RdYlGn'),
                        name='Osma_1d'),
                 row=1, col=2)

fig.append_trace(go.Bar(x=macd_1d['MACD'].index,
                        y=macd_1d['MACD'],
                        marker=dict(color =macd_1d['MACD'], colorscale='speed'),
                        name='MACD_1d'),
                        row=1, col=2)

fig.append_trace(go.Scatter(x=delta_1d.index,
                            y=delta_1d,
                            line=dict(color ='#5788c9'),
                            mode='lines',
                            name='Delta_1d'),
                 row=1, col=2)

fig.update_layout(
                  title=dict(pad=dict(r=100, t=50, b=50), text=f'{from_symbol}/{to_symbol}. Рекомендация - {status}', font=dict(size=10)),
                  margin=dict(l=100, r=100, t=100, b=100),
                  hovermode="x",
                  legend_orientation="v",
                  )

fig.update_xaxes(
    rangeslider_visible=False,
    rangebreaks=[dict(bounds=["sat", "mon"])],
    rangeselector = dict(
            buttons = list([
            dict(count= 1, label = '1H', step = 'hour', stepmode = 'backward'),
            dict(count= 1, label = '1D', step = 'day', stepmode = 'backward'),
            dict(count= 1, label = '1M', step = 'month', stepmode = 'todate'),
            dict(count= 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(step= 'all')])))


fig.show()
