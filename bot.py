import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================== SOZLAMALAR ==================
BOT_TOKEN = os.getenv("8473286959:AAHmhC7S0260_FySK2oWfpS78PB9_-7rmDs")

ADMIN_ID = 7723504118  # <-- BU YERGA ADMIN TELEGRAM ID
CHANNELS = [
    "https://t.me/+q_cduzR_ApBlZjhi",  # majburiy kanal 1
    "https://t.me/+k2CoVZkEsb0xNjZi",  # majburiy kanal 2
    "@gift_konkurs_game",  # majburiy kanal 3
    "@gold_stars_tolov"   # majburiy kanal 4
]

REF_BONUS = 2
MIN_WITHDRAW = 25

# ================== START ==================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

users = {}
withdraw_requests = []

# ================== TEKSHIRUV ==================
async def check_sub(user_id):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("⭐ Stars ishlash", callback_data="earn"),
        InlineKeyboardButton("👤 Profil", callback_data="profile"),
        InlineKeyboardButton("💰 Gift (25⭐)", callback_data="withdraw"),
        InlineKeyboardButton("🆘 Qo‘llab-quvvatlash", url="https://t.me/your_support")
    )
    return kb

# ================== /START ==================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    uid = message.from_user.id

    if uid not in users:
        users[uid] = {"stars": 0}

        if message.get_args().isdigit():
            ref = int(message.get_args())
            if ref in users and ref != uid:
                users[ref]["stars"] += REF_BONUS
                await bot.send_message(ref, f"🎉 +{REF_BONUS}⭐ referal bonus!")

    if not await check_sub(uid):
        text = "❗ Botdan foydalanish uchun kanallarga obuna bo‘ling:\n\n"
        kb = InlineKeyboardMarkup()
        for ch in CHANNELS:
            kb.add(InlineKeyboardButton(ch, url=f"https://t.me/{ch.replace('@','')}"))
        kb.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check"))
        await message.answer(text, reply_markup=kb)
        return

    await message.answer(
        "🔥 Stars botga xush kelibsiz!\n\n"
        "Quyidan bo‘limni tanlang:",
        reply_markup=main_menu()
    )

# ================== OBUNANI TEKSHIRISH ==================
@dp.callback_query_handler(lambda c: c.data == "check")
async def check(callback: types.CallbackQuery):
    if await check_sub(callback.from_user.id):
        await callback.message.edit_text(
            "✅ Obuna tasdiqlandi!\n\nMenyu:",
            reply_markup=main_menu()
        )
    else:
        await callback.answer("❌ Hali hamma kanalga obuna emassiz", show_alert=True)

# ================== MENYU ==================
@dp.callback_query_handler(lambda c: c.data == "earn")
async def earn(callback: types.CallbackQuery):
    uid = callback.from_user.id
    link = f"https://t.me/{(await bot.me).username}?start={uid}"

    await callback.message.edit_text(
        f"⭐ Stars ishlash\n\n"
        f"👥 Referal orqali:\n"
        f"➕ Har referal = {REF_BONUS}⭐\n\n"
        f"🔗 Sizning havola:\n{link}",
        reply_markup=main_menu()
    )

@dp.callback_query_handler(lambda c: c.data == "profile")
async def profile(callback: types.CallbackQuery):
    uid = callback.from_user.id
    stars = users.get(uid, {}).get("stars", 0)

    await callback.message.edit_text(
        f"👤 Profil\n\n"
        f"🆔 ID: {uid}\n"
        f"⭐ Stars: {stars}",
        reply_markup=main_menu()
    )

@dp.callback_query_handler(lambda c: c.data == "withdraw")
async def withdraw(callback: types.CallbackQuery):
    uid = callback.from_user.id
    stars = users.get(uid, {}).get("stars", 0)

    if stars < MIN_WITHDRAW:
        await callback.answer("❌ Yetarli stars yo‘q", show_alert=True)
        return

    users[uid]["stars"] -= MIN_WITHDRAW
    withdraw_requests.append(uid)
  text = (
        "🎁 YANGI GIFT ARIZA\n\n"
        f"👤 @{callback.from_user.username}\n"
        f"🆔 ID: {uid}\n"
        f"⭐ Miqdor: {MIN_WITHDRAW}"
    )

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{uid}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"no_{uid}")
    )

    await bot.send_message(ADMIN_ID, text, reply_markup=kb)
    await callback.answer("✅ Ariza yuborildi")

# ================== ADMIN ==================
@dp.callback_query_handler(lambda c: c.data.startswith("ok_"))
async def approve(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    uid = int(callback.data.split("_")[1])
    await bot.send_message(uid, "🎉 Gift tasdiqlandi!")
    await callback.message.edit_text("✅ Tasdiqlandi")

@dp.callback_query_handler(lambda c: c.data.startswith("no_"))
async def reject(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    uid = int(callback.data.split("_")[1])
    users[uid]["stars"] += MIN_WITHDRAW
    await bot.send_message(uid, "❌ Ariza rad etildi, stars qaytarildi")
    await callback.message.edit_text("❌ Rad etildi")

# ================== ISHGA TUSHISH ==================
if name == "main":
    executor.start_polling(dp, skip_updates=True)
