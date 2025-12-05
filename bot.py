from telegram import Update
from telegram.ext import Application, ContextTypes

async def send_signal(context: ContextTypes.DEFAULT_TYPE, signal):
    text = f"""
🚨 НОВЫЙ СИГНАЛ 🚨

{signal['symbol']}
Направление: {signal['side']}
Точка входа ≈ {signal['entry']}
Плечо: ×{signal['leverage']}

SL: {signal['sl']}
TP1: {signal['tp1']}
TP2: {signal['tp2']} (×4)

RR: {signal['rr']} | Таймфрейм: 15m

@yourchannel (можно поставить свой)
    """.strip()

    await context.bot.send_message(
        chat_id=context.job.data['chat_id'],
        text=text
    )
