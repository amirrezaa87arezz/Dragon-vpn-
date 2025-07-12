import json
import logging
import os
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold
import asyncio

# بارگذاری توکن
BOT_TOKEN = os.getenv("7652704164:AAF4conisn2jicpdlHGYyRylb4TZpkMgXbI")

# بارگذاری اطلاعات
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

with open("plans.json", encoding="utf-8") as f:
    plans = json.load(f)

# تنظیمات پایه
ADMINS = config["admins"]
EXTRA_ADMINS = config.get("extra_admins", [])
ALL_ADMINS = ADMINS + EXTRA_ADMINS

CARD_NUMBER = config["card_number"]
CARD_OWNER = config["card_owner"]
TRAINING_URL = config["training_url"]
SUPPORT_USERNAME = config["support_username"]

# راه‌اندازی ربات
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)
logging.basicConfig(level=logging.INFO)


# ثبت کاربران
async def save_user(user_id):
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
    except:
        users = []

    if user_id not in users:
        users.append(user_id)
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f)


# شروع ربات
@router.message(CommandStart())
async def start(message: Message):
    await save_user(message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 خرید اشتراک", callback_data="buy")],
        [InlineKeyboardButton(text="📚 آموزش اتصال", url=TRAINING_URL)],
        [InlineKeyboardButton(text="🎧 پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME.strip('@')}")]
    ])
    await message.answer(
        f"🎉 {hbold('به ربات Dragon VPN خوش آمدید')} 🎉\n\n"
        "از منوی زیر یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=keyboard
    )


# منوی خرید
@router.callback_query(F.data == "buy")
async def show_plans(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    for plan in plans:
        kb.button(
            text=f"{plan['name']} - {plan['price']:,} تومان",
            callback_data=f"plan_{plan['id']}"
        )
    kb.adjust(1)
    await callback.message.edit_text("📦 لطفاً یک پلن را انتخاب کنید:", reply_markup=kb.as_markup())


# نمایش فاکتور
@router.callback_query(F.data.startswith("plan_"))
async def show_invoice(callback: CallbackQuery):
    plan_id = int(callback.data.split("_")[1])
    plan = next((p for p in plans if p["id"] == plan_id), None)
    if not plan:
        return await callback.answer("❌ پلن پیدا نشد")

    text = (
        f"🧾 {hbold('صورتحساب خرید')}:\n\n"
        f"💼 پلن: {plan['name']}\n"
        f"⏳ مدت: {plan['duration']}\n"
        f"👥 تعداد کاربر: {plan['users']}\n"
        f"💾 حجم: نامحدود\n"
        f"💰 قیمت: {plan['price']:,} تومان\n\n"
        f"💳 شماره کارت: {CARD_NUMBER}\n"
        f"👤 به نام: {CARD_OWNER}\n\n"
        f"{hbold('⚠️ لطفاً پس از پرداخت، فیش واریزی را ارسال کنید.')}"
    )
    await callback.message.answer(text)
    await callback.message.answer("برای ارسال فیش، فایل یا تصویر را ارسال کنید.")
    dp.message.register(receive_receipt, F.photo | F.document)


# دریافت فیش
async def receive_receipt(message: Message):
    user_id = message.from_user.id
    for admin_id in ALL_ADMINS:
        await bot.send_message(
            admin_id,
            f"📥 فیش جدید از کاربر {user_id} دریافت شد.\n"
            "جهت بررسی اقدام نمایید."
        )
        if message.photo:
            await bot.send_photo(admin_id, message.photo[-1].file_id)
        elif message.document:
            await bot.send_document(admin_id, message.document.file_id)
    await message.answer("✅ فیش واریزی دریافت شد. منتظر بررسی ادمین باشید (حداکثر ۲ ساعت).")


# پنل مدیریت
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ALL_ADMINS:
        return await message.answer("⛔️ دسترسی ندارید.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 ارسال کانفیگ", callback_data="send_config")],
        [InlineKeyboardButton(text="📢 اطلاع‌رسانی", callback_data="broadcast")],
    ])

    if message.from_user.id in ADMINS:
        kb.inline_keyboard.append([InlineKeyboardButton(text="🛠 ویرایش شماره کارت", callback_data="edit_card")])

    await message.answer("🎛 به پنل مدیریت خوش آمدید:", reply_markup=kb)


# ارسال کانفیگ
@router.callback_query(F.data == "send_config")
async def ask_user_id(callback: CallbackQuery):
    await callback.message.answer("لطفاً آیدی عددی کاربر را ارسال کنید:")
    dp.message.register(ask_config)


async def ask_config(message: Message):
    try:
        target_id = int(message.text)
        await message.answer("حالا فایل کانفیگ (متن یا فایل) را ارسال کنید:")
        dp.message.register(send_config_to_user, F.text | F.document, target_id=target_id)
    except:
        await message.answer("❌ آیدی نامعتبر است. دوباره تلاش کنید.")


async def send_config_to_user(message: Message, target_id: int):
    try:
        if message.document:
            await bot.send_document(target_id, message.document.file_id)
        else:
            await bot.send_message(target_id, message.text)
        await message.answer("✅ کانفیگ ارسال شد.")
    except Exception as e:
        await message.answer(f"❌ ارسال نشد: {e}")


# اطلاع‌رسانی
@router.callback_query(F.data == "broadcast")
async def ask_broadcast(callback: CallbackQuery):
    await callback.message.answer("لطفاً پیام مورد نظر برای ارسال به همه کاربران را بنویسید:")
    dp.message.register(do_broadcast)


async def do_broadcast(message: Message):
    try:
        with open("users.json", encoding="utf-8") as f:
            users = json.load(f)
    except:
        return await message.answer("❌ لیست کاربران پیدا نشد.")
    sent = 0
    for uid in users:
        try:
            await bot.send_message(uid, message.text)
            sent += 1
        except:
            continue
    await message.answer(f"📢 پیام برای {sent} کاربر ارسال شد.")


# ویرایش کارت
@router.callback_query(F.data == "edit_card")
async def edit_card(callback: CallbackQuery):
    await callback.message.answer("لطفاً شماره کارت جدید را ارسال کنید:")
    dp.message.register(save_new_card)


async def save_new_card(message: Message):
    config["card_number"] = message.text
    await message.answer("✅ حالا نام صاحب کارت را وارد کنید:")
    dp.message.register(save_new_owner)


async def save_new_owner(message: Message):
    config["card_owner"] = message.text
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    await message.answer("✅ اطلاعات کارت با موفقیت به‌روزرسانی شد.")


# اجرای ربات
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
