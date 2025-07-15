import json import logging from aiogram import Bot, Dispatcher, types from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton from aiogram.utils import executor from aiogram.dispatcher.filters import CommandStart from aiogram.dispatcher import filters import os

API_TOKEN = os.getenv("7652704164:AAF4conisn2jicpdlHGYyRylb4TZpkMgXbI")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN) dp = Dispatcher(bot)

Load Plans

def load_plans(): with open("data/plans.json", encoding="utf-8") as f: return json.load(f)

def load_config(): with open("data/config.json", encoding="utf-8") as f: return json.load(f)

def is_admin(user_id): with open("data/admins.json") as f: admins = json.load(f) return str(user_id) in admins or str(user_id) in ["7935344235", "5993860770"]

def is_super_admin(user_id): return str(user_id) in ["7935344235", "5993860770"]

@dp.message_handler(CommandStart()) async def send_welcome(message: types.Message): keyboard = InlineKeyboardMarkup(row_width=2) keyboard.add( InlineKeyboardButton("🛒 خرید اشتراک", callback_data="buy_subscription"), InlineKeyboardButton("📚 آموزش اتصال", url="https://t.me/amuzesh_dragonvpn"), InlineKeyboardButton("💬 پشتیبانی", url="https://t.me/Psycho_remix1") ) await message.answer("به ربات Dragon VPN خوش آمدید", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'buy_subscription') async def handle_buy(call: types.CallbackQuery): plans = load_plans() markup = InlineKeyboardMarkup(row_width=1) for plan in plans: markup.add(InlineKeyboardButton(plan["name"], callback_data=f"plan_{plan['id']}")) await call.message.edit_text("📋 لطفا یک پلن را انتخاب کنید:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('plan_')) async def handle_plan_selection(call: types.CallbackQuery): plan_id = int(call.data.split('_')[1]) plans = load_plans() plan = next((p for p in plans if p["id"] == plan_id), None) if not plan: await call.message.edit_text("❌ پلن مورد نظر یافت نشد.") return

config = load_config()

msg = (
    f"✅ {plan['name']}\n"
    f"مدت: {plan['duration']}\n"
    f"حجم: نامحدود\n"
    f"تعداد کاربر: {plan['users']}\n"
    f"قیمت: {plan['price']} تومان\n\n"
    f"💳 شماره کارت: {config['card_number']} بنام {config['card_name']}\n"
    "لطفاً بعد از واریز، فیش واریزی را ارسال کنید تا بررسی شود."
)
await call.message.edit_text(msg)

@dp.message_handler(content_types=types.ContentType.PHOTO) async def handle_payment_receipt(message: types.Message): await message.reply("✅ فیش واریزی دریافت شد. منتظر بررسی ادمین باشید (نهایتا 2 ساعت طول می‌کشد)") # ارسال برای ادمین‌ها with open("data/admins.json") as f: admins = json.load(f) for admin_id in admins: try: await bot.send_message(int(admin_id), f"📥 فیش جدید از کاربر {message.from_user.id}") await bot.send_photo(int(admin_id), photo=message.photo[-1].file_id, caption="فیش ارسالی") except: pass

@dp.message_handler(commands=["admin"]) async def admin_panel(message: types.Message): if not is_admin(message.from_user.id): return await message.reply("⛔ دسترسی ندارید")

kb = InlineKeyboardMarkup(row_width=2)
if is_super_admin(message.from_user.id):
    kb.add(InlineKeyboardButton("1️⃣ ویرایش اطلاعات", callback_data="edit_info"))
    kb.add(InlineKeyboardButton("3️⃣ افزودن ادمین", callback_data="add_admin"))
kb.add(InlineKeyboardButton("2️⃣ ارسال کانفیگ", callback_data="send_config"))
kb.add(InlineKeyboardButton("4️⃣ اطلاع‌رسانی", callback_data="broadcast"))
await message.reply("🛠 پنل مدیریت", reply_markup=kb)

ادامه کدهای مدیریت در فایل بعدی یا ادامه همین فایل اضافه می‌گردد

