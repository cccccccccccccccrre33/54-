import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # твой личный чат айди

EXCHANGE = "bybit"  # или "binance"
TESTNET = True      # пока True — без риска

# Пары, которые сканируем (можно добавить сколько угодно)
SYMBOLS = [
    "BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT", "XRP/USDT:USDT",
    "DOGE/USDT:USDT", "ADA/USDT:USDT", "AVAX/USDT:USDT", "LINK/USDT:USDT",
    "BNB/USDT:USDT", "DOT/USDT:USDT", "MATIC/USDT:USDT", "LTC/USDT:USDT",
    "1000PEPE/USDT:USDT", "WIF/USDT:USDT", "FARTCOIN/USDT:USDT", "POPCAT/USDT:USDT",
    # добавляй любые, какие хочешь
]

TIMEFRAME = "15m"
LEVERAGE_RECOMMEND = 10   # рекомендуемое плечо
SCAN_INTERVAL_MINUTES = 5  # как часто сканировать
