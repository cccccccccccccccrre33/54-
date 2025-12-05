import asyncio
import logging
from scanner import generate_signal
from bot import send_signal
from config import *
from telegram.ext import Application
from telegram import BotCommand

logging.basicConfig(level=logging.INFO)

async def scan_and_notify(app):
    signals = []
    for symbol in SYMBOLS:
        signal = generate_signal(symbol)
        if signal:
            signals.append(signal)

    for sig in signals:
        await send_signal(app, sig)

async def main_job(context):
    await scan_and_notify(context.application)

async def start_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем команду /status
    async def status(update, context):
        await update.message.reply_text("Бот живой, сканирую рынок каждые 5 мин ⏱️")
    app.add_handler(CommandHandler("status", status))

    # Запускаем сканирование каждые N минут
    job_queue = app.job_queue
    job_queue.run_repeating(
        main_job,
        interval=SCAN_INTERVAL_MINUTES * 60,
        first=10,
        data={'chat_id': TELEGRAM_CHAT_ID}
    )

    print("Бот запущен...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Держим живым
    await asyncio.Event().wait()

if __name__ == "__main__":
    from telegram.ext import CommandHandler
    asyncio.run(start_bot())
