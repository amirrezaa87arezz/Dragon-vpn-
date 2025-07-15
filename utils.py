# utils.py
import json
import os
from config import ADMINS, DATA_FOLDER

USERS_FILE = os.path.join(DATA_FOLDER, "users.json")

def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def save_user(user_id, full_name):
    users = load_json(USERS_FILE)
    if user_id not in users:
        users[user_id] = {"name": full_name}
        save_json(USERS_FILE, users)

async def send_to_admins(message):
    from main import bot
    for admin_id in ADMINS:
        try:
            if message.content_type == "photo":
                await bot.send_photo(admin_id, message.photo[-1].file_id, caption=f"فیش واریزی از کاربر {message.from_user.id}")
            elif message.content_type == "document":
                await bot.send_document(admin_id, message.document.file_id, caption=f"فیش واریزی از کاربر {message.from_user.id}")
            else:
                await bot.send_message(admin_id, f"فیش واریزی از کاربر {message.from_user.id} دریافت شد.")
        except Exception as e:
            print(f"خطا هنگام ارسال به ادمین {admin_id}: {e}")

def load_plans():
    return load_json("plans.json")
