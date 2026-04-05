import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

BOT_TOKEN = os.getenv("BOT_TOKEN", "8586888958:AAF_3RLTuQHYoklx0DW0CUZTrGq4Z7E4rgU")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer(
        f"⚡ <b>AvtoTok</b> ga xush kelibsiz!\n\n"
        f"O’zbekistondagi barcha EV zaryadlash stansiyalari\n"
        f"<b>Faqat 1kWh &lt; 2000 so’m</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

async def main():
    print("AvtoTok bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
