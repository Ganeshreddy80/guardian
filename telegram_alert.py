import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def send_guardian_alert(decision: dict):
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    emoji = "🚨" if decision["urgency"] == "HIGH" else "⚠️"

    msg = f"""{emoji} GUARDIAN Alert

Action: {decision['action']}
Save: ₹{decision['projected_saving']}
Urgency: {decision['urgency']}

{decision['message']}"""

    await bot.send_message(chat_id=chat_id, text=msg)

def send_alert(decision):
    try:
        asyncio.run(send_guardian_alert(decision))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_guardian_alert(decision))

if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
    raise ValueError("Telegram env variables missing")