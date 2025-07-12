import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

logging.basicConfig(level=logging.INFO)

API_TOKEN = "7652704164:AAF4conisn2jicpdlHGYyRylb4TZpkMgXbI"

# بارگذاری کانفیگ و پلن‌ها
def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(data):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_plans():
    with open("plans.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_plans(plans):
    with open("plans.json", "w", encoding="utf-8") as f:
        json.dump(plans, f, ensure_ascii=False, indent=2)

config = load_config()
ADMINS = config.get("admins", [])
SUPPORT_ID = config.get("support_id", "")
OWNER_NAME = config.get("owner_username", "Dragon vpn")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- کیبورد‌های اصلی ---
def main_user_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🛒 خرید اشتراک"), KeyboardButton("📚 آموزش اتصال"), KeyboardButton("💬 پشتیبانی"))
    return markup

def main_admin_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📝 ویرایش"))
    markup.add(KeyboardButton("📤 ارسال کانفیگ"), KeyboardButton("➕ اضافه کردن ادمین"), KeyboardButton("📢 اطلاع رسانی"))
    return markup

def edit_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✏️ تغییر شماره کارت", "✏️ ویرایش پلن")
    markup.add("🔙 بازگشت")
    return markup

def edit_plan_field_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("نام", "مدت", "حجم", "تعداد کاربران", "قیمت")
    markup.add("🔙 بازگشت")
    return markup

# --- حالت FSM ---
class EditCard(StatesGroup):
    number = State()
    name = State()

class EditPlan(StatesGroup):
    choosing_plan = State()
    editing_field = State()
    new_value = State()

class AddAdmin(StatesGroup):
    waiting_for_id = State()

class SendConfig(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_config = State()

class Broadcast(StatesGroup):
    waiting_for_message = State()

class AwaitPayment(StatesGroup):
    waiting_for_receipt = State()

# --- هندلر‌ها ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    text = f"سلام {message.from_user.full_name}!\nبه ربات {OWNER_NAME} خوش آمدید."
    await message.answer(text, reply_markup=main_user_keyboard())

@dp.message_handler(lambda msg: msg.text == "📚 آموزش اتصال")
async def send_tutorial(msg: types.Message):
    await msg.answer("برای آموزش اتصال به این لینک مراجعه کنید:\nhttps://t.me/amuzesh_dragonvpn")

@dp.message_handler(lambda msg: msg.text == "💬 پشتیبانی")
async def send_support(msg: types.Message):
    await msg.answer(f"برای پشتیبانی با آیدی {SUPPORT_ID} تماس بگیرید.")

@dp.message_handler(lambda msg: msg.text == "🛒 خرید اشتراک")
async def show_plans(msg: types.Message):
    plans = load_plans()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for p in plans:
        btn_text = f"{p['id']}. {p['name']} - {p['price'] // 1000} هزار تومان"
        markup.insert(KeyboardButton(btn_text))
    markup.add("🔙 بازگشت")
    await msg.answer("لطفاً یک پلن انتخاب کنید:", reply_markup=markup)

@dp.message_handler(lambda msg: msg.text and msg.text.split(".")[0].isdigit())
async def send_invoice(msg: types.Message):
    plans = load_plans()
    try:
        plan_id = int(msg.text.split(".")[0])
    except:
        await msg.answer("❌ انتخاب نامعتبر است.")
        return
    plan = next((p for p in plans if p["id"] == plan_id), None)
    if not plan:
        await msg.answer("❌ پلن یافت نشد.")
        return
    card_number = config.get("card_number", "")
    card_name = config.get("card_name", "")
    invoice = (f"🧾 مشخصات پلن انتخابی شما:\n\n"
               f"📌 پلن: {plan['name']}\n"
               f"📆 مدت: {plan['duration']}\n"
               f"👥 کاربران: {plan['users']}\n"
               f"💾 حجم: {plan['volume']}\n"
               f"💰 قیمت: {plan['price']} تومان\n\n"
               f"💳 شماره کارت:\n{card_number}\nبه نام {card_name}\n\n"
               f"❗️ لطفاً پس از واریز فیش را ارسال کنید.")
    await msg.answer(invoice)
    await AwaitPayment.waiting_for_receipt.set()

@dp.message_handler(state=AwaitPayment.waiting_for_receipt)
async def receive_receipt(msg: types.Message, state: FSMContext):
    # اینجا میتونیم اعتبارسنجی فیش واریزی بگذاریم (مثلا عکس یا متن)
    if not msg.photo and not msg.document and not msg.text:
        await msg.answer("لطفا فیش واریزی را ارسال کنید (عکس یا متن).")
        return
    await msg.answer("فیش واریزی دریافت شد، لطفاً منتظر بررسی ادمین باشید (حداکثر 2 ساعت).")
    await state.finish()

    # ارسال اطلاعیه به مدیران
    for admin_id in ADMINS:
        await bot.send_message(admin_id, f"کاربر {msg.from_user.id} فیش واریزی ارسال کرد.")

# --- بخش مدیریت ---

@dp.message_handler(lambda msg: msg.from_user.id in ADMINS and msg.text == "📝 ویرایش")
async def edit_menu(msg: types.Message):
    await msg.answer("📋 یکی از گزینه‌های ویرایش را انتخاب کنید:", reply_markup=edit_menu_keyboard())

# ویرایش شماره کارت
@dp.message_handler(lambda msg: msg.text == "✏️ تغییر شماره کارت", user_id=ADMINS)
async def edit_card_start(msg: types.Message):
    await msg.answer("🔢 شماره کارت جدید را وارد کنید:")
    await EditCard.number.set()

@dp.message_handler(state=EditCard.number, user_id=ADMINS)
async def edit_card_number(msg: types.Message, state: FSMContext):
    await state.update_data(number=msg.text)
    await msg.answer("👤 نام دارنده کارت را وارد کنید:")
    await EditCard.name.set()

@dp.message_handler(state=EditCard.name, user_id=ADMINS)
async def edit_card_name(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    config["card_number"] = data["number"]
    config["card_name"] = msg.text
    save_config(config)
    await msg.answer("✅ شماره کارت و نام دارنده کارت با موفقیت به‌روزرسانی شد.")
    await state.finish()

# ویرایش پلن‌ها
@dp.message_handler(lambda msg: msg.text == "✏️ ویرایش پلن", user_id=ADMINS)
async def choose_plan_to_edit(msg: types.Message):
    plans = load_plans()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for plan in plans:
        markup.insert(KeyboardButton(f"{plan['id']}. {plan['name']}"))
    markup.add("🔙 بازگشت")
    await msg.answer("📋 لطفاً پلن مورد نظر برای ویرایش را انتخاب کنید:", reply_markup=markup)
    await Edit
