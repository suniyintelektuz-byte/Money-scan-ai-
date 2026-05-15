import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"Salom! 👋\n\n💵 Dollar kupyurasini tekshirish uchun rasm yuboring!\n\n📋 /history — tarix"
    )

@router.message(F.photo)
async def handle_photo(message: Message):
    await message.answer("⏳ Tahlil qilinmoqda...")
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            image_bytes = await resp.read()
        form = aiohttp.FormData()
        form.add_field("file", image_bytes, filename="photo.jpg", content_type="image/jpeg")
        form.add_field("source", "telegram")
        try:
            async with session.post(f"{API_BASE_URL}/api/scan/", data=form) as api_resp:
                if api_resp.status == 200:
                    r = await api_resp.json()
                    status = "✅ HAQIQIY" if r["is_genuine"] else "❌ SOXTA"
                    denom = f"${r['denomination']}" if r["denomination"] else "?"
                    serial = r["serial_number"] or "O'qilmadi"
                    year = r["year"] or "?"
                    await message.answer(
                        f"💵 Natija:\n\n🔍 {status}\n📊 Ishonch: {int(r['confidence']*100)}%\n"
                        f"💰 Qiymat: {denom}\n🔢 Seriya: {serial}\n📅 Yil: {year}"
                    )
                else:
                    await message.answer("❌ Xatolik yuz berdi.")
        except Exception as e:
            await message.answer(f"❌ Server xatosi: {str(e)}")

@router.message(Command("history"))
async def cmd_history(message: Message):
    await message.answer("📋 Tarix funksiyasi tez orada!")

async def main():
    dp.include_router(router)
    print("Bot ishga tushdi ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
