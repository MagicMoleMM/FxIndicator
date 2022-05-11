import requests
import pandas as pd

def get_fx_intraday(from_symbol, to_symbol, interval, outputsize, apikey):

    url = f'https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={from_symbol}&to_symbol={to_symbol}&interval={interval}&outputsize={outputsize}&datatype=json&apikey={apikey}'

    r  = requests.get(url)
    data = r.json()
    dt = pd.DataFrame(data)
    dt.to_csv(f'fx_data_{from_symbol}{to_symbol}_{interval}.csv')
    dt_read = pd.read_csv(f'fx_data_{from_symbol}{to_symbol}_{interval}.csv')

    dt_read = dt_read.iloc[7:]
    new_df = dt_read[f'Time Series FX ({interval})'].str.split(', ',expand=True)
    new_df.columns=['open','high','low', 'close']
    for column in new_df.columns:
        for i in new_df.index:
            new_df[column][i] = new_df[column][i].replace('1. open', '')
            new_df[column][i] = new_df[column][i].replace('2. high', '')
            new_df[column][i] = new_df[column][i].replace('3. low', '')
            new_df[column][i] = new_df[column][i].replace('4. close', '')
            new_df[column][i] = new_df[column][i].replace("'", '')
            new_df[column][i] = new_df[column][i].replace(":", '')
            new_df[column][i] = new_df[column][i].replace("{", '')
            new_df[column][i] = new_df[column][i].replace("}", '')
            new_df[column][i] = float(new_df[column][i])

    final_df = pd.concat([dt_read,new_df],axis=1)
    final_df = final_df.drop(f'Time Series FX ({interval})',axis=1)
    final_df = final_df.drop('Meta Data',axis=1)
    final_df = final_df.rename(columns={'Unnamed: 0': 'Date'})
    final_df = final_df.set_index('Date', inplace=False)

    return final_df

def get_fx_daily(from_symbol, to_symbol, outputsize, apikey):

    url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_symbol}&to_symbol={to_symbol}&outputsize={outputsize}&datatype=json&apikey={apikey}'

    r  = requests.get(url)
    data = r.json()
    dt = pd.DataFrame(data)
    dt.to_csv(f'fx_data_{from_symbol}{to_symbol}_daily.csv')
    dt_read = pd.read_csv(f'fx_data_{from_symbol}{to_symbol}_daily.csv')

    dt_read = dt_read.iloc[6:]
    new_df = dt_read['Time Series FX (Daily)'].str.split(', ',expand=True)
    new_df.columns=['open','high','low', 'close']
    for column in new_df.columns:
        for i in new_df.index:
            new_df[column][i] = new_df[column][i].replace('1. open', '')
            new_df[column][i] = new_df[column][i].replace('2. high', '')
            new_df[column][i] = new_df[column][i].replace('3. low', '')
            new_df[column][i] = new_df[column][i].replace('4. close', '')
            new_df[column][i] = new_df[column][i].replace("'", '')
            new_df[column][i] = new_df[column][i].replace(":", '')
            new_df[column][i] = new_df[column][i].replace("{", '')
            new_df[column][i] = new_df[column][i].replace("}", '')
            new_df[column][i] = float(new_df[column][i])

    final_df = pd.concat([dt_read,new_df],axis=1)
    final_df = final_df.drop('Time Series FX (Daily)',axis=1)
    final_df = final_df.drop('Meta Data',axis=1)
    final_df = final_df.rename(columns={'Unnamed: 0': 'Date'})
    final_df = final_df.set_index('Date', inplace=False)

    return final_df

def get_fx_weekly(from_symbol, to_symbol, apikey):

    url = f'https://www.alphavantage.co/query?function=FX_WEEKLY&from_symbol={from_symbol}&to_symbol={to_symbol}&datatype=json&apikey={apikey}'

    r  = requests.get(url)
    data = r.json()
    dt = pd.DataFrame(data)
    dt.to_csv(f'fx_data_{from_symbol}{to_symbol}_weekly.csv')
    dt_read = pd.read_csv(f'fx_data_{from_symbol}{to_symbol}_weekly.csv')

    dt_read = dt_read.iloc[5:]
    new_df = dt_read['Time Series FX (Weekly)'].str.split(', ',expand=True)
    new_df.columns=['open','high','low', 'close']
    for column in new_df.columns:
        for i in new_df.index:
            new_df[column][i] = new_df[column][i].replace('1. open', '')
            new_df[column][i] = new_df[column][i].replace('2. high', '')
            new_df[column][i] = new_df[column][i].replace('3. low', '')
            new_df[column][i] = new_df[column][i].replace('4. close', '')
            new_df[column][i] = new_df[column][i].replace("'", '')
            new_df[column][i] = new_df[column][i].replace(":", '')
            new_df[column][i] = new_df[column][i].replace("{", '')
            new_df[column][i] = new_df[column][i].replace("}", '')
            new_df[column][i] = float(new_df[column][i])

    final_df = pd.concat([dt_read,new_df],axis=1)
    final_df = final_df.drop('Time Series FX (Weekly)',axis=1)
    final_df = final_df.drop('Meta Data',axis=1)
    final_df = final_df.rename(columns={'Unnamed: 0': 'Date'})
    final_df = final_df.set_index('Date', inplace=False)

    return final_df

def get_fx_monthly(from_symbol, to_symbol, apikey):

    url = f'https://www.alphavantage.co/query?function=FX_MONTHLY&from_symbol={from_symbol}&to_symbol={to_symbol}&datatype=json&apikey={apikey}'

    r  = requests.get(url)
    data = r.json()
    dt = pd.DataFrame(data)
    dt.to_csv(f'fx_data_{from_symbol}{to_symbol}_monthly.csv')
    dt_read = pd.read_csv(f'fx_data_{from_symbol}{to_symbol}_monthly.csv')

    dt_read = dt_read.iloc[5:]
    new_df = dt_read['Time Series FX (Monthly)'].str.split(', ',expand=True)
    new_df.columns=['open','high','low', 'close']
    for column in new_df.columns:
        for i in new_df.index:
            new_df[column][i] = new_df[column][i].replace('1. open', '')
            new_df[column][i] = new_df[column][i].replace('2. high', '')
            new_df[column][i] = new_df[column][i].replace('3. low', '')
            new_df[column][i] = new_df[column][i].replace('4. close', '')
            new_df[column][i] = new_df[column][i].replace("'", '')
            new_df[column][i] = new_df[column][i].replace(":", '')
            new_df[column][i] = new_df[column][i].replace("{", '')
            new_df[column][i] = new_df[column][i].replace("}", '')
            new_df[column][i] = float(new_df[column][i])

    final_df = pd.concat([dt_read,new_df],axis=1)
    final_df = final_df.drop('Time Series FX (Monthly)',axis=1)
    final_df = final_df.drop('Meta Data',axis=1)
    final_df = final_df.rename(columns={'Unnamed: 0': 'Date'})
    final_df = final_df.set_index('Date', inplace=False)

    return final_df
