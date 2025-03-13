import requests
import pandas as pd
import os

API_KEY = os.getenv('FMP_API_KEY')
BASE_URL = 'https://financialmodelingprep.com/api/v3'

# Файл с тикерами
tickers_file = 'tickers.txt'

# Параметры RSI и MA для разных таймфреймов
timeframes = {
    'daily': {'ma_length': 50, 'rsi_length': 20, 'interval': '1day'},
    'hourly': {'ma_length': 150, 'rsi_length': 200, 'interval': '1hour'},
    '15min': {'ma_length': 70, 'rsi_length': 200, 'interval': '15min'},
    '5min': {'ma_length': 100, 'rsi_length': 200, 'interval': '5min'}
}

def load_tickers(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def get_rsi(symbol, interval, rsi_length):
    url = f"{BASE_URL}/technical_indicator/{interval}/{symbol}?period={rsi_length}&type=rsi&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['rsi']
    return None

def get_rsi_ma(symbol, interval, ma_length, rsi_length):
    url = f"{BASE_URL}/technical_indicator/{interval}/{symbol}?period={rsi_length}&type=rsi&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) >= ma_length:
            rsi_values = [item['rsi'] for item in data[:ma_length]]
            return sum(rsi_values) / len(rsi_values)
    return None

def analyze_tickers(tickers, timeframes):
    results = []

    for ticker in tickers:
        ticker_result = {'Ticker': ticker}

        for tf_name, params in timeframes.items():
            rsi = get_rsi(ticker, params['interval'], params['rsi_length'])
            rsi_ma = get_rsi_ma(ticker, params['interval'], params['ma_length'], params['rsi_length'])

            if rsi is not None and rsi_ma is not None:
                sign = '+' if rsi > rsi_ma else '-'
            else:
                sign = 'N/A'

            ticker_result[tf_name] = sign

        results.append(ticker_result)

    return pd.DataFrame(results)

if __name__ == "__main__":
    tickers = load_tickers(tickers_file)
    df_results = analyze_tickers(tickers, timeframes)
    print(df_results)
    df_results.to_csv('rsi_analysis_results.csv', index=False)
