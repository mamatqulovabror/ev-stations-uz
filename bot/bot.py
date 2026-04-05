import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = os.getenv("BOT_TOKEN", "8586888958:AAF_3RLTuQHYoklx0DW0CUZTrGq4Z7E4rgU")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://mamatqulovabror.github.io/ev-stations-uz/")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    # Avval eski keyboardni tozalaymiz
    await msg.answer("...", reply_markup=ReplyKeyboardRemove())
    # Keyin inline button bilan asosiy xabar
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⚡ Xaritani ochish", web_app=WebAppInfo(url=WEBAPP_URL))
    ]])
    await msg.answer(
        f"⚡ <b>AvtoTok</b> ga xush kelibsiz!\n\n"
        f"O’zbekistondagi barcha EV zaryadlash stansiyalari\n"
        f"<b>Faqat 1kWh &lt; 2000 so’m</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

async def main():
    print("AvtoTok bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
