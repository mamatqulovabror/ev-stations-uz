import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8586888958:AAF_3RLTuQHYoklx0DW0CUZTrGq4Z7E4rgU")
API_URL = os.getenv("API_URL", "https://ev-stations-uz-production.up.railway.app")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://mamatqulovabror.github.io/ev-stations-uz/")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def open_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="⚡ Xaritani ochish",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]])

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer(
        f"⚡ <b>AvtoTok</b> ga xush kelibsiz!\n\n"
        f"O’zbekistondagi barcha EV zaryadlash stansiyalari\n"
        f"<b>Faqat 1kWh &lt; 2000 so’m</b>\n\n"
        f"Pastdagi tugmani bosing:",
        parse_mode="HTML",
        reply_markup=open_keyboard()
    )

@dp.message(Command("help"))
async def cmd_help(msg: types.Message):
    await msg.answer(
        "ℹ️ <b>AvtoTok bot buyruqlari:</b>\n\n"
        "/start — Bosh menyu\n"
        "/help — Yordam\n\n"
        "⚡ Xaritani ochish tugmasi orqali Mini App ni oching.",
        parse_mode="HTML",
        reply_markup=open_keyboard()
    )

async def main():
    print("AvtoTok bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
