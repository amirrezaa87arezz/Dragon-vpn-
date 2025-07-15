# handlers.py
import json
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS, CARD_NUMBER, CARD_NAME, SUPPORT_ID, TUTORIAL_LINK
from utils import save_user, send_to_admins, load_plans

# منوی پایین اصلی
async def menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🛒 خرید اشتراک", "📚 آموزش اتصال", "🎧 پشتیبانی")
    return kb

# استارت و خوش آمدگویی
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)
    full_name = message.from_user.full_name or message.from_user.username
    await save_user(user_id, full_name)
    kb = await menu_keyboard()
    await message.answer("به ربات Dragon VPN خوش آمدید 🐉", reply_markup=kb)

# آموزش اتصال
async def tutorial_handler(message: types.Message):
    await message.answer(f"برای آموزش اتصال به لینک زیر مراجعه کنید:\n{TUTORIAL_LINK}")

# پشتیبانی
async def support_handler(message: types.Message):
    await message.answer(f"برای پشتیبانی با آی‌دی زیر تماس بگیرید:\n{SUPPORT_ID}")

# نمایش پلن‌ها در خرید اشتراک
async def buy_handler(message: types.Message):
    plans = load_plans()
    kb = InlineKeyboardMarkup(row_width=1)
    for plan in plans:
        kb.insert(InlineKeyboardButton(
            text=f"{plan['name']} - {plan['price']} تومان",
            callback_data=f"plan_{plan['id']}"
        ))
    await message.answer("لطفاً پلن مورد نظر را انتخاب کنید:", reply_markup=kb)

# انتخاب پلن و ارسال فاکتور
async def plan_callback_handler(callback_query: types.CallbackQuery):
    plan_id = int(callback_query.data.split("_")[1])
    plans = load_plans()
    plan = next((p for p in plans if p["id"] == plan_id), None)
    if not plan:
        await callback_query.answer("پلن پیدا نشد!", show_alert=True)
        return

    text = (
        f"✅ صورت‌حساب شما:\n\n"
        f"📦 پلن: {plan['name']}\n"
        f"⏳ مدت: {plan['duration']}\n"
        f"💾 حجم: نامحدود\n"
        f"👥 تعداد کاربر: {plan['users']}\n"
        f"💰 قیمت: {plan['price']} تومان\n\n"
        f"💳 شماره کارت: {CARD_NUMBER} بنام {CARD_NAME}\n\n"
        f"کاربر گرامی لطفاً بعد از واریز فیش واریزی را ارسال کرده تا ادمین بررسی کند."
    )
    await callback_query.message.edit_text(text)
    await callback_query.answer()

# دریافت فیش پرداختی
async def receipt_handler(message: types.Message):
    if message.content_type in ['photo', 'document']:
        await message.reply("فیش واریزی دریافت شد. منتظر بررسی ادمین باشید (نهایتا 2 ساعت طول می‌کشد).")
        await send_to_admins(message)
    else:
        await message.reply("لطفا فیش واریزی را به صورت عکس یا فایل ارسال کنید.")
