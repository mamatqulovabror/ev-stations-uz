import asyncio
import os
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8586888958:AAF_3RLTuQHYoklx0DW0CUZTrGq4Z7E4rgU")
API_URL = os.getenv("API_URL", "https://ev-stations-uz-production.up.railway.app")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://mamatqulovabror.github.io/ev-stations-uz/")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def open_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="â¡ Xaritani ochish",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]])

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="â¡ Xaritani ochish", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text="ð Barcha stansiyalar"), KeyboardButton(text="ð° Eng arzon")],
            [KeyboardButton(text="ð Tok Bor"), KeyboardButton(text="ð Beon"), KeyboardButton(text="ð EcoTok")],
            [KeyboardButton(text="ð Statistika")],
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer(
        f"â¡ <b>AvtoTok</b> ga xush kelibsiz!\n\n"
        f"O'zbekistondagi barcha EV zaryadlash stansiyalari\n"
        f"<b>Faqat 1kWh &lt; 2000 so'm</b>\n\n"
        f"Pastdagi tugmani bosing:",
        parse_mode="HTML",
        reply_markup=open_keyboard()
    )


@dp.message(F.text == "ð Barcha stansiyalar")
async def all_stations(msg: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/api/stations", timeout=10)
            stations = res.json()
        except Exception:
            await msg.answer("â API ga ulanib bo\'lmadi.")
            return

    if not stations:
        await msg.answer("Stansiya topilmadi.")
        return

    text = f"â¡ <b>Barcha stansiyalar ({len(stations)} ta):</b>\n\n"
    for s in stations[:10]:
        text += (
            f"ð <b>{s['name']}</b>\n"
            f"   ð° {s['price_per_kwh']} so'm/kWh\n"
            f"   ð {s.get('network','?')} | â¡{s.get('power_kw','?')}kW\n"
            f"   ð {s.get('working_hours','24/7')}\n\n"
        )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@dp.message(F.text == "ð° Eng arzon")
async def cheapest(msg: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/api/stations", timeout=10)
            stations = res.json()
        except Exception:
            await msg.answer("â Xatolik yuz berdi.")
            return

    stations.sort(key=lambda x: x.get('price_per_kwh', 9999))
    top5 = stations[:5]
    text = "ð° <b>Eng arzon 5 ta stansiya:</b>\n\n"
    for i, s in enumerate(top5, 1):
        text += (
            f"{i}. <b>{s['name']}</b>\n"
            f"   ð° <b>{s['price_per_kwh']} so'm/kWh</b>\n"
            f"   ð {s.get('network','?')} | ð {s.get('address','?')}\n\n"
        )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@dp.message(F.text.in_(["ð Tok Bor", "ð Beon", "ð EcoTok"]))
async def by_network(msg: types.Message):
    network_map = {"ð Tok Bor": "Tok Bor", "ð Beon": "Beon", "ð EcoTok": "EcoTok"}
    network = network_map[msg.text]
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/api/stations?network={network}", timeout=10)
            stations = res.json()
        except Exception:
            await msg.answer("â Xatolik yuz berdi.")
            return

    if not stations:
        await msg.answer(f"{network} tarmog'ida stansiya topilmadi.")
        return

    text = f"ð <b>{network} stansiyalari ({len(stations)} ta):</b>\n\n"
    for s in stations:
        text += (
            f"ð <b>{s['name']}</b>\n"
            f"   ð° {s['price_per_kwh']} so'm/kWh | â¡{s.get('power_kw','?')}kW\n"
            f"   ð {s.get('address','?')}\n\n"
        )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@dp.message(F.text == "ð Statistika")
async def stats(msg: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/api/stats", timeout=10)
            s = res.json()
        except Exception:
            await msg.answer("â Xatolik yuz berdi.")
            return

    text = (
        f"ð <b>AvtoTok statistikasi:</b>\n\n"
        f"â¡ Jami stansiyalar: <b>{s['total_stations']} ta</b>\n"
        f"ð° O'rtacha narx: <b>{s['avg_price_per_kwh']} so'm/kWh</b>\n"
        f"ð Filtr: 1kWh &lt; 2000 so'm"
    )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@dp.message(Command("help"))
async def cmd_help(msg: types.Message):
    await msg.answer(
        "â¹ï¸ <b>AvtoTok bot buyruqlari:</b>\n\n"
        "/start â Bosh menyu\n"
        "/help â Yordam\n\n"
        "Tugmalar orqali:\n"
        "â¡ Xaritani ochish â Mini App\n"
        "ð Barcha stansiyalar â ro'yxat\n"
        "ð° Eng arzon â narx bo'yicha\n"
        "ð Tarmoq bo'yicha â Tok Bor, Beon, EcoTok",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

async def main():
    print("AvtoTok bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
