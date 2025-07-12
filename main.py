
import logging
import os
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = os.getenv("BOT_TOKEN")

# Admin and manager IDs
ADMINS = [5993860770]
MANAGERS = [7935344235, 5993860770]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Users memory
user_data = {}

# Start
@dp.message_handler(commands=['start'])
async def welcome(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🛒 خرید اشتراک", "📚 آموزش اتصال", "💬 پشتیبانی")
    await msg.answer("🎉 به ربات Dragon VPN خوش آمدید!
از منوی زیر استفاده کنید.", reply_markup=kb)

# Support
@dp.message_handler(lambda m: m.text == "💬 پشتیبانی")
async def support(msg: types.Message):
    await msg.answer("برای پشتیبانی به آیدی زیر پیام دهید:
@Psycho_remix1")

# Guide
@dp.message_handler(lambda m: m.text == "📚 آموزش اتصال")
async def guide(msg: types.Message):
    await msg.answer("📎 آموزش اتصال:
https://t.me/amuzesh_dragonvpn")

# Plans
PLANS = {
    "plan_1": ("تک کاربره", "1 ماه", "85,000"),
    "plan_2": ("دو کاربره", "1 ماه", "115,000"),
    "plan_3": ("سه کاربره", "1 ماه", "169,000"),
    "plan_4": ("تک کاربره", "2 ماه", "140,000"),
    "plan_5": ("دو کاربره", "2 ماه", "165,000"),
    "plan_6": ("سه کاربره", "2 ماه", "185,000"),
    "plan_7": ("تک کاربره", "3 ماه", "174,000"),
    "plan_8": ("دو کاربره", "3 ماه", "234,000"),
    "plan_9": ("سه کاربره", "3 ماه", "335,000"),
}

@dp.message_handler(lambda m: m.text == "🛒 خرید اشتراک")
async def plans(msg: types.Message):
    ikb = types.InlineKeyboardMarkup()
    for i, key in enumerate(PLANS, start=1):
        ikb.add(types.InlineKeyboardButton(f"پلن {i}", callback_data=key))
    await msg.answer("لطفا پلن مورد نظر را انتخاب کنید:", reply_markup=ikb)

@dp.callback_query_handler(lambda c: c.data in PLANS)
async def invoice(call: types.CallbackQuery):
    code = call.data
    p = PLANS[code]
    text = f"""✅ پلن انتخابی شما:
👥 {p[0]}
🕒 مدت: {p[1]}
💾 حجم: نامحدود
💳 قیمت: {p[2]} تومان

💳 شماره کارت: 6277-6013-6877-6066
به نام رضوانی

📤 لطفاً پس از واریز، فیش را همین‌جا ارسال نمایید."""
    await bot.send_message(call.from_user.id, text)

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def receipt(msg: types.Message):
    user_id = msg.from_user.id
    for admin in MANAGERS:
        await bot.send_message(admin, f"📥 فیش جدید از کاربر {user_id}")
        await bot.forward_message(admin, admin_chat_id=admin, from_chat_id=msg.chat.id, message_id=msg.message_id)
    await msg.reply("✅ فیش شما دریافت شد و در حال بررسی است. تا ۲ ساعت آینده پاسخ داده می‌شود.")

# Admin Panel
@dp.message_handler(commands=['admin'])
async def admin_panel(msg: types.Message):
    if msg.from_user.id in MANAGERS:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("📤 ارسال کانفیگ", "📢 اطلاع‌رسانی", "➕ افزودن ادمین")
        await msg.answer("🔐 پنل مدیریت:", reply_markup=kb)
    elif msg.from_user.id in ADMINS:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("📤 ارسال کانفیگ", "📢 اطلاع‌رسانی")
        await msg.answer("🔐 پنل ادمین:", reply_markup=kb)

@dp.message_handler(lambda m: m.text == "📤 ارسال کانفیگ")
async def ask_id(msg: types.Message):
    await msg.answer("لطفاً آیدی عددی کاربر را وارد کنید:")
    user_data[msg.from_user.id] = {"step": "get_user_id"}

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "get_user_id")
async def get_config_text(msg: types.Message):
    user_data[msg.from_user.id]["target_id"] = int(msg.text)
    user_data[msg.from_user.id]["step"] = "get_config"
    await msg.answer("متن یا کانفیگ را وارد کنید:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "get_config")
async def send_config(msg: types.Message):
    uid = user_data[msg.from_user.id]["target_id"]
    await bot.send_message(uid, f"📥 کانفیگ شما:
{msg.text}")
    await msg.answer("✅ کانفیگ ارسال شد.")
    user_data.pop(msg.from_user.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
