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
            text="⚡ Xaritani ochish",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]])

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚡ Xaritani ochish", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text="📋 Barcha stansiyalar"), KeyboardButton(text="💰 Eng arzon")],
            [KeyboardButton(text="🔌 Tok Bor"), KeyboardButton(text="🔌 Beon"), KeyboardButton(text="🔌 EcoTok")],
            [KeyboardButton(text="📊 Statistika")],
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    await msg.answer(
        f"⚡ <b>AvtoTok</b> ga xush kelibsiz!\n\n"
        f"O'zbekistondagi barcha EV zaryadlash stansiyalari\n"
        f"<b>Faqat 1kWh &lt; 2000 so'm</b>\n\n"
        f"Pastdagi tugmani bosing:",
        parse_mode="HTML",
        reply_markup=open_keyboard()
    )
    await msg.answer(
        "Qo'shimcha buyruqlar:",
        reply_markup=main_keyboard()
    )

@dp.message(F.text == "📋 Barcha stansiyalar")
async def all_stations(msg: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/api/stations", timeout=10)
            stations = res.json()
        except Exception:
            await msg.answer("❌ API ga ulanib bo\'lmadi.")
            return

    if not stations:
        await msg.answer("Stansiya topilmadi.")
        return

    text = f"⚡ <b>Barcha stansiyalar ({len(stations)} ta):</b>\n\n"
    for s in stations[:10]:
        text += (
            f"📍 <b>{s['name']}</b>\n"
            f"   💰 {s['price_per_kwh']} so'm/kWh\n"
            f"   🔌 {s.get('network','?')} | ⚡{s.get('power_kw','?')}kW\n"
            f"   🕐 {s.get('working_hours','24/7')}\n\n"
        )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@dp.message(F.text == "💰 Eng arzon")
async def cheapest(msg: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/api/stations", timeout=10)
            stations = res.json()
        except Exception:
            await msg.answer("❌ Xatolik yuz berdi.")
            return

    stations.sort(key=lambda x: x.get('price_per_kwh', 9999))
    top5 = stations[:5]
    text = "💰 <b>Eng arzon 5 ta stansiya:</b>\n\n"
    for i, s in enumerate(top5, 1):
        text += (
            f"{i}. <b>{s['name']}</b>\n"
            f"   💰 <b>{s['price_per_kwh']} so'm/kWh</b>\n"
            f"   🔌 {s.get('network','?')} | 📍 {s.get('address','?')}\n\n"
        )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@dp.message(F.text.in_(["🔌 Tok Bor", "🔌 Beon", "🔌 EcoTok"]))
async def by_network(msg: types.Message):
    network_map = {"🔌 Tok Bor": "Tok Bor", "🔌 Beon": "Beon", "🔌 EcoTok": "EcoTok"}
    network = network_map[msg.text]
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/api/stations?network={network}", timeout=10)
            stations = res.json()
        except Exception:
            await msg.answer("❌ Xatolik yuz berdi.")
            return

    if not stations:
        await msg.answer(f"{network} tarmog'ida stansiya topilmadi.")
        return

    text = f"🔌 <b>{network} stansiyalari ({len(stations)} ta):</b>\n\n"
    for s in stations:
        text += (
            f"📍 <b>{s['name']}</b>\n"
            f"   💰 {s['price_per_kwh']} so'm/kWh | ⚡{s.get('power_kw','?')}kW\n"
            f"   📍 {s.get('address','?')}\n\n"
        )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@dp.message(F.text == "📊 Statistika")
async def stats(msg: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/api/stats", timeout=10)
            s = res.json()
        except Exception:
            await msg.answer("❌ Xatolik yuz berdi.")
            return

    text = (
        f"📊 <b>AvtoTok statistikasi:</b>\n\n"
        f"⚡ Jami stansiyalar: <b>{s['total_stations']} ta</b>\n"
        f"💰 O'rtacha narx: <b>{s['avg_price_per_kwh']} so'm/kWh</b>\n"
        f"📌 Filtr: 1kWh &lt; 2000 so'm"
    )
    await msg.answer(text, parse_mode="HTML", reply_markup=main_keyboard())

@dp.message(Command("help"))
async def cmd_help(msg: types.Message):
    await msg.answer(
        "ℹ️ <b>AvtoTok bot buyruqlari:</b>\n\n"
        "/start — Bosh menyu\n"
        "/help — Yordam\n\n"
        "Tugmalar orqali:\n"
        "⚡ Xaritani ochish — Mini App\n"
        "📋 Barcha stansiyalar — ro'yxat\n"
        "💰 Eng arzon — narx bo'yicha\n"
        "🔌 Tarmoq bo'yicha — Tok Bor, Beon, EcoTok",
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

async def main():
    print("AvtoTok bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
