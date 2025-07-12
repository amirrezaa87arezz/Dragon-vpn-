import logging
from aiogram import Bot, Dispatcher, executor, types

# توکن رباتت رو اینجا بذار
API_TOKEN = "توکن_واقعی_ربات"

# آیدی عددی مدیران
ADMINS = [5993860770]
MANAGERS = [7935344235, 5993860770]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

# شماره کارت و نام اولیه
card_info = {
    "number": "6277-6013-6877-6066",
    "name": "رضوانی"
}

# پلن‌ها
PLANS = {
    "plan_1": {"title": "تک کاربره - 1 ماهه", "price": "85,000"},
    "plan_2": {"title": "دو کاربره - 1 ماهه", "price": "115,000"},
    "plan_3": {"title": "سه کاربره - 1 ماهه", "price": "169,000"},
    "plan_4": {"title": "تک کاربره - 2 ماهه", "price": "140,000"},
    "plan_5": {"title": "دو کاربره - 2 ماهه", "price": "165,000"},
    "plan_6": {"title": "سه کاربره - 2 ماهه", "price": "185,000"},
    "plan_7": {"title": "تک کاربره - 3 ماهه", "price": "174,000"},
    "plan_8": {"title": "دو کاربره - 3 ماهه", "price": "234,000"},
    "plan_9": {"title": "سه کاربره - 3 ماهه", "price": "335,000"},
}


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🛒 خرید اشتراک", "📚 آموزش اتصال", "💬 پشتیبانی")
    await msg.answer("🎉 به ربات Dragon VPN خوش آمدید!\nاز منوی زیر استفاده کنید.", reply_markup=kb)


@dp.message_handler(lambda m: m.text == "📚 آموزش اتصال")
async def help(msg: types.Message):
    await msg.answer("📎 آموزش اتصال:\nhttps://t.me/amuzesh_dragonvpn")


@dp.message_handler(lambda m: m.text == "💬 پشتیبانی")
async def support(msg: types.Message):
    await msg.answer("برای پشتیبانی به آیدی زیر پیام دهید:\n@Psycho_remix1")


@dp.message_handler(lambda m: m.text == "🛒 خرید اشتراک")
async def buy(msg: types.Message):
    ikb = types.InlineKeyboardMarkup()
    for i, key in enumerate(PLANS, 1):
        ikb.add(types.InlineKeyboardButton(f"پلن {i}", callback_data=key))
    await msg.answer("لطفاً یکی از پلن‌ها را انتخاب کنید:", reply_markup=ikb)


@dp.callback_query_handler(lambda c: c.data in PLANS)
async def plan_selected(call: types.CallbackQuery):
    p = PLANS[call.data]
    text = f"""✅ پلن انتخابی:
📦 {p['title']}
💳 قیمت: {p['price']} تومان
📡 حجم: نامحدود

💳 واریز به:
شماره کارت: {card_info['number']}
بنام: {card_info['name']}

📤 لطفاً پس از پرداخت، فیش را همین‌جا ارسال نمایید.
"""
    await call.message.answer(text)


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_receipt(msg: types.Message):
    user_id = msg.from_user.id
    for admin in MANAGERS:
        await bot.send_message(admin, f"📥 فیش جدید از کاربر {user_id}")
        await bot.forward_message(admin, from_chat_id=msg.chat.id, message_id=msg.message_id)
    await msg.reply("✅ فیش شما دریافت شد و در حال بررسی است. پاسخ تا ۲ ساعت آینده.")


@dp.message_handler(commands=['admin'])
async def admin_panel(msg: types.Message):
    if msg.from_user.id in MANAGERS:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("📤 ارسال کانفیگ", "📢 اطلاع‌رسانی", "➕ افزودن ادمین")
        await msg.answer("🔐 پنل مدیریت:", reply_markup=kb)
    elif msg.from_user.id in ADMINS:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("🛠 ویرایش")
        await msg.answer("🛠 پنل ادمین:", reply_markup=kb)


@dp.message_handler(lambda m: m.text == "🛠 ویرایش")
async def edit_menu(msg: types.Message):
    ikb = types.InlineKeyboardMarkup()
    ikb.add(
        types.InlineKeyboardButton("✏️ تغییر کارت", callback_data="edit_card"),
        types.InlineKeyboardButton("💰 قیمت پلن", callback_data="edit_price"),
        types.InlineKeyboardButton("📝 نام پلن", callback_data="edit_title")
    )
    await msg.answer("کدام مورد را می‌خواهید ویرایش کنید؟", reply_markup=ikb)


@dp.callback_query_handler(lambda c: c.data == "edit_card")
async def edit_card(call: types.CallbackQuery):
    user_data[call.from_user.id] = {"step": "edit_card"}
    await call.message.answer("شماره کارت و نام صاحب کارت را وارد کنید (مثال:\n6277-xxxx-xxxx-xxxx بنام رضوانی)")


@dp.callback_query_handler(lambda c: c.data == "edit_price")
async def edit_price(call: types.CallbackQuery):
    user_data[call.from_user.id] = {"step": "edit_price"}
    txt = "کدام پلن؟ عدد 1 تا 9 بنویس:\nمثال:\n`2 120,000` (یعنی پلن 2، قیمت جدید 120 هزار)"
    await call.message.answer(txt, parse_mode="Markdown")


@dp.callback_query_handler(lambda c: c.data == "edit_title")
async def edit_title(call: types.CallbackQuery):
    user_data[call.from_user.id] = {"step": "edit_title"}
    txt = "کدام پلن؟ عدد 1 تا 9 بنویس:\nمثال:\n`3 پلن سه کاربره یک ماهه ویژه`"
    await call.message.answer(txt, parse_mode="Markdown")


@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") in ["edit_card", "edit_price", "edit_title"])
async def process_edit(msg: types.Message):
    step = user_data[msg.from_user.id]["step"]

    if step == "edit_card":
        parts = msg.text.split("بنام")
        if len(parts) == 2:
            card_info["number"] = parts[0].strip()
            card_info["name"] = parts[1].strip()
            await msg.reply("✅ اطلاعات کارت بروزرسانی شد.")
        else:
            await msg.reply("❌ فرمت اشتباه است.")

    elif step == "edit_price":
        try:
            num, price = msg.text.strip().split()
            key = f"plan_{num}"
            if key in PLANS:
                PLANS[key]["price"] = price
                await msg.reply(f"✅ قیمت پلن {num} به {price} تغییر کرد.")
            else:
                await msg.reply("❌ شماره پلن نامعتبر است.")
        except:
            await msg.reply("❌ فرمت اشتباه است.")

    elif step == "edit_title":
        try:
            num, title = msg.text.strip().split(' ', 1)
            key = f"plan_{num}"
            if key in PLANS:
                PLANS[key]["title"] = title
                await msg.reply(f"✅ نام پلن {num} به '{title}' تغییر کرد.")
            else:
                await msg.reply("❌ شماره پلن نامعتبر است.")
        except:
            await msg.reply("❌ فرمت اشتباه است.")

    user_data.pop(msg.from_user.id)


@dp.message_handler(lambda m: m.text == "📤 ارسال کانفیگ")
async def send_config_start(msg: types.Message):
    user_data[msg.from_user.id] = {"step": "get_user_id"}
    await msg.reply("لطفاً آیدی عددی کاربر را وارد کنید:")


@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "get_user_id")
async def send_config_text(msg: types.Message):
    user_data[msg.from_user.id]["target"] = int(msg.text)
    user_data[msg.from_user.id]["step"] = "get_config"
    await msg.reply("کانفیگ را وارد کنید:")


@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get("step") == "get_config")
async def send_config(msg: types.Message):
    uid = user_data[msg.from_user.id]["target"]
    await bot.send_message(uid, f"📥 کانفیگ شما:\n{msg.text}")
    await msg.reply("✅ کانفیگ ارسال شد.")
    user_data.pop(msg.from_user.id)


if __name__ == '__main__':
    print("🟢 ربات Dragon VPN اجرا شد...")
    executor.start_polling(dp, skip_updates=True)
