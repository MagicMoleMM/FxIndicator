import pandas as pd
import time
import numpy.polynomial.polynomial as poly
import AlphaVantage as av
import tg_send_message as tg
import schedule

def job():

    fx_list = ['USDZAR',
           'AUDUSD', 
           'NZDUSD', 
           'GBPUSD', 
           'EURUSD', 
           'USDCHF', 
           'USDCAD', 
           'USDJPY',
           'GBPJPY',
           'USDRUB',
           ]

    for fx in fx_list:

        from_symbol = fx[:3]
        to_symbol = fx[3:6]
        interval = '60min' 
        outputsize = 'compact' 
        apikey = '2GGORTBXQIFSR2AF'

        #  Загружаем данные

        data_1h_load = av.get_fx_intraday(from_symbol, to_symbol, interval, outputsize, apikey)
        data_1d_load = av.get_fx_daily(from_symbol, to_symbol, outputsize, apikey)

        data_1h_load.to_csv(f'Data_fx/{from_symbol}{to_symbol}_1h.csv')
        data_1d_load.to_csv(f'Data_fx/{from_symbol}{to_symbol}_1d.csv')

        # # Читаем данные

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

            if (delta_1h.tail(1)[0] > 0 and delta_1h.tail(2)[0] < 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0]) or (delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] < macd_1h['Hist'].tail(3)[0]):

                return f'{from_symbol}/{to_symbol} краткосрок - открыть длинную позицию {time.ctime(time.time())} по цене {data_1h["close"].tail(1)[0]}'
            
            elif (delta_1h.tail(1)[0] < 0 and delta_1h.tail(2)[0] > 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0]) or (delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] > macd_1h['Hist'].tail(3)[0]):

                return f'{from_symbol}/{to_symbol} краткосрок - открыть короткую позицию {time.ctime(time.time())} по цене {data_1h["close"].tail(1)[0]}'
            
            elif (delta_1h.tail(1)[0] < 0 and delta_1h.tail(2)[0] > 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0]) or (delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] > macd_1h['Hist'].tail(3)[0]):

                return f'{from_symbol}/{to_symbol} краткосрок - закрыть длинную позицию {time.ctime(time.time())} по цене {data_1h["close"].tail(1)[0]}'
            
            elif (delta_1h.tail(1)[0] > 0 and delta_1h.tail(2)[0] < 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0]) or (delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1h['Hist'].tail(2)[0] < macd_1h['Hist'].tail(3)[0]):

                return f'{from_symbol}/{to_symbol} краткосрок - закрыть короткую позицию {time.ctime(time.time())} по цене {data_1h["close"].tail(1)[0]}'
            
            else:
                return f'{from_symbol}/{to_symbol} краткосрок - нет сигналов'

        def signal_long_term():

            if (delta_1d.tail(1)[0] > 0 and delta_1d.tail(2)[0] < 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0]) or (delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] < macd_1d['Hist'].tail(3)[0]):

                return f'{from_symbol}/{to_symbol} долгосрок - открыть длинную позицию {time.ctime(time.time())} по цене {data_1d["close"].tail(1)[0]}'
            
            elif (delta_1d.tail(1)[0] < 0 and delta_1d.tail(2)[0] > 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0]) or (delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] > macd_1d['Hist'].tail(3)[0]):

                return f'{from_symbol}/{to_symbol} долгосрок - открыть короткую позицию {time.ctime(time.time())} по цене {data_1d["close"].tail(1)[0]}'
            
            elif (delta_1d.tail(1)[0] < 0 and delta_1d.tail(2)[0] > 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0]) or (delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] > macd_1d['Hist'].tail(3)[0]):

                return f'{from_symbol}/{to_symbol} долгосрок - закрыть длинную позицию {time.ctime(time.time())} по цене {data_1d["close"].tail(1)[0]}'
            
            elif (delta_1d.tail(1)[0] > 0 and delta_1d.tail(2)[0] < 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0]) or (delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and macd_1d['Hist'].tail(2)[0] < macd_1d['Hist'].tail(3)[0]):

                return f'{from_symbol}/{to_symbol} долгосрок - закрыть короткую позицию {time.ctime(time.time())} по цене {data_1d["close"].tail(1)[0]}'
            
            else:
                return f'{from_symbol}/{to_symbol} долгосрок - нет сигналов'

        def status_transaction():

            if delta_1h.tail(1)[0] > 0 and delta_1d.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0] and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0]:
                return f'{from_symbol}/{to_symbol}: Держать длинную позицию (краткосрок / долгосрок)'
            elif delta_1h.tail(1)[0] < 0 and delta_1d.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0] and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0]:
                return f'{from_symbol}/{to_symbol}: Держать короткую позицию (краткосрок / долгосрок)'
            elif delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0] and delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0]:
                return f'{from_symbol}/{to_symbol}: Держать длинную позицию долгосрочно. Краткосрочно  - коррекция, возможно открытие краткосрочной короткой позиции'
            elif delta_1d.tail(1)[0] > 0 and macd_1d['Hist'].tail(1)[0] > macd_1d['Hist'].tail(2)[0]:
                return f'{from_symbol}/{to_symbol}: Держать длинную позицию долгосрочно. Краткосрочно  - коррекция'
            elif delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0] and delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0]:
                return f'{from_symbol}/{to_symbol}: Держать короткую позицию долгосрочно. Краткосрочно  - коррекция, возможно открытие краткосрочной длинной позиции' 
            elif delta_1d.tail(1)[0] < 0 and macd_1d['Hist'].tail(1)[0] < macd_1d['Hist'].tail(2)[0]:
                return f'{from_symbol}/{to_symbol}: Держать короткую позицию долгосрочно. Краткосрочно  - коррекция' 
            elif delta_1h.tail(1)[0] > 0 and macd_1h['Hist'].tail(1)[0] > macd_1h['Hist'].tail(2)[0]:
                return f'{from_symbol}/{to_symbol}: Держать длинную позицию краткосрочно. Долгосрочно  - коррекция'
            elif delta_1h.tail(1)[0] < 0 and macd_1h['Hist'].tail(1)[0] < macd_1h['Hist'].tail(2)[0]:
                return f'{from_symbol}/{to_symbol}: Держать короткую позицию краткосрочно. Долгосрочно  - коррекция'
            else:
                return f'{from_symbol}/{to_symbol}: Без позиции'

        
        print(time.ctime(time.time()))
        tg.telegram_bot_sendtext(time.ctime(time.time()))

        status = status_transaction()
        print(status)
        tg.telegram_bot_sendtext(status)

        signal_short = signal_short_term()
        print(signal_short)
        tg.telegram_bot_sendtext(signal_short)

        signal_long = signal_long_term()
        print(signal_long)
        tg.telegram_bot_sendtext(signal_long)

        time.sleep(60)

job()

schedule.every().hour.at(":00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

