import requests
import pandas as pd
import csv

def get_fx_intraday(from_symbol, to_symbol, interval, outputsize, apikey):

    url = f'https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={from_symbol}&to_symbol={to_symbol}&interval={interval}&outputsize={outputsize}&datatype=csv&apikey={apikey}'

    r = requests.get(url)
    decoded_content = r.content.decode('utf-8')
    data = csv.reader(decoded_content.splitlines(), delimiter=',')
    dt = pd.DataFrame(data)
    dt.columns = ['timestamp','open', 'high', 'low', 'close']
    dt = dt.iloc[1:]
    dt = dt.set_index('timestamp', inplace=False)

    return dt

def get_fx_daily(from_symbol, to_symbol, outputsize, apikey):

    url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_symbol}&to_symbol={to_symbol}&outputsize={outputsize}&datatype=csv&apikey={apikey}'

    r = requests.get(url)
    decoded_content = r.content.decode('utf-8')
    data = csv.reader(decoded_content.splitlines(), delimiter=',')
    dt = pd.DataFrame(data)
    dt.columns = ['timestamp','open', 'high', 'low', 'close']
    dt = dt.iloc[1:]
    dt = dt.set_index('timestamp', inplace=False)

    return dt

def get_fx_weekly(from_symbol, to_symbol, apikey):

    url = f'https://www.alphavantage.co/query?function=FX_WEEKLY&from_symbol={from_symbol}&to_symbol={to_symbol}&datatype=csv&apikey={apikey}'

    r = requests.get(url)
    decoded_content = r.content.decode('utf-8')
    data = csv.reader(decoded_content.splitlines(), delimiter=',')
    dt = pd.DataFrame(data)
    dt.columns = ['timestamp','open', 'high', 'low', 'close']
    dt = dt.iloc[1:]
    dt = dt.set_index('timestamp', inplace=False)

    return dt

def get_fx_monthly(from_symbol, to_symbol, apikey):

    url = f'https://www.alphavantage.co/query?function=FX_MONTHLY&from_symbol={from_symbol}&to_symbol={to_symbol}&datatype=csv&apikey={apikey}'

    r = requests.get(url)
    decoded_content = r.content.decode('utf-8')
    data = csv.reader(decoded_content.splitlines(), delimiter=',')
    dt = pd.DataFrame(data)
    dt.columns = ['timestamp','open', 'high', 'low', 'close']
    dt = dt.iloc[1:]
    dt = dt.set_index('timestamp', inplace=False)

    return dt