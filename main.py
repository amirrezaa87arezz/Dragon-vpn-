from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
import asyncio

from config import BOT_TOKEN
from handlers import start, buy, payment, admin

async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(start.router, buy.router, payment.router, admin.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())