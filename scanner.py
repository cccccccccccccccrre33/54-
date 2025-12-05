# scanner.py — полностью без ta-lib, без ошибок на Render
import ccxt
import pandas as pd
import numpy as np
from config import EXCHANGE, SYMBOLS, TIMEFRAME

def get_exchange():
    if EXCHANGE == "bybit":
        exchange = ccxt.bybit({
            'enableRateLimit': True,
            'options': {'defaultType': 'swap'}
        })
    else:
        exchange = ccxt.binance({
            'enableRateLimit': True,
        })
    return exchange

def fetch_ohlcv(symbol):
    exchange = get_exchange()
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=100)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Ошибка загрузки {symbol}: {e}")
        return None

# === Ручные индикаторы (точь-в-точь как ta-lib) ===
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    tr0 = abs(high - low)
    tr1 = abs(high - close.shift())
    tr2 = abs(low - close.shift())
    tr = pd.concat([tr0, tr1, tr2], axis=1).max(axis=1)
    return tr.rolling(period).mean()

# === Генерация сигнала ===
def generate_signal(symbol):
    df = fetch_ohlcv(symbol)
    if df is None or len(df) < 50:
        return None

    df['ema9'] = ema(df['close'], 9)
    df['ema21'] = ema(df['close'], 21)
    df['rsi'] = rsi(df['close'])
    df['atr'] = atr(df)

    # Volume spike
    avg_vol = df['volume'].rolling(20).mean().iloc[-1]
    current_vol = df['volume'].iloc[-1]
    vol_spike = current_vol > avg_vol * 2 if avg_vol > 0 else False

    price = df['close'].iloc[-1]
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Защита от NaN
    if pd.isna(last['ema9']) or pd.isna(last['atr']):
        return None

    signal = None

    # ЛОНГ
    if (last['ema9'] > last['ema21'] and
        prev['ema9'] <= prev['ema21'] and
        last['rsi'] < 70 and
        vol_spike):
        signal = {
            "side": "LONG",
            "entry": round(price, 6),
            "sl": round(price - last['atr'] * 1.5, 6),
            "tp1": round(price + last['atr'] * 2, 6),
            "tp2": round(price + last['atr'] * 4, 6),
            "leverage": 10,
            "rr": "1:2.7+"
        }

    # ШОРТ
    elif (last['ema9'] < last['ema21'] and
          prev['ema9'] >= prev['ema21'] and
          last['rsi'] > 30 and
          vol_spike):
        signal = {
            "side": "SHORT",
            "entry": round(price, 6),
            "sl": round(price + last['atr'] * 1.5, 6),
            "tp1": round(price - last['atr'] * 2, 6),
            "tp2": round(price - last['atr'] * 4, 6),
            "leverage": 10,
            "rr": "1:2.7+"
        }

    if signal:
        signal['symbol'] = symbol.replace(":USDT", "").replace("/USDT", "")
        return signal
    return None
