import ccxt
import pandas as pd
import ta
import numpy as np
from config import EXCHANGE, TESTNET, SYMBOLS, TIMEFRAME

def get_exchange():
    if EXCHANGE == "bybit":
        return ccxt.bybit({
            'enableRateLimit': True,
            'options': {'defaultType': 'swap'}
        })
    else:
        return ccxt.binance({'enableRateLimit': True})

def fetch_ohlcv(symbol):
    exchange = get_exchange()
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        return None

def generate_signal(symbol):
    df = fetch_ohlcv(symbol)
    if df is None or len(df) < 50:
        return None

    df['ema9'] = ta.trend.EMAIndicator(df['close'], window=9).ema_indicator()
    df['ema21'] = ta.trend.EMAIndicator(df['close'], window=21).ema_indicator()
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
    
    # Volume spike
    avg_vol = df['volume'].rolling(20).mean().iloc[-1]
    vol_spike = df['volume'].iloc[-1] > avg_vol * 2

    price = df['close'].iloc[-1]
    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal = None

    # Лонг
    if (last['ema9'] > last['ema21'] and 
        prev['ema9'] <= prev['ema21'] and 
        last['rsi'] < 70 and 
        vol_spike):
        signal = {
            "side": "LONG 🟢",
            "entry": round(price, 6),
            "sl": round(price - last['atr'] * 1.5, 6),
            "tp1": round(price + last['atr'] * 2, 6),
            "tp2": round(price + last['atr'] * 4, 6),
            "leverage": 10,
            "rr": "1:2.7+"
        }

    # Шорт
    elif (last['ema9'] < last['ema21'] and 
          prev['ema9'] >= prev['ema21'] and 
          last['rsi'] > 30 and 
          vol_spike):
        signal = {
            "side": "SHORT 🔴",
            "entry": round(price, 6),
            "sl": round(price + last['atr'] * 1.5, 6),
            "tp1": round(price - last['atr'] * 2, 6),
            "tp2": round(price - last['atr'] * 4, 6),
            "leverage": 10,
            "rr": "1:2.7+"
        }

    if signal:
        signal['symbol'] = symbol.replace(":USDT", "")
        return signal
    return None
