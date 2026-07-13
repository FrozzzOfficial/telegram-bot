import asyncio
import logging
import random
import os
from datetime import datetime

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder


TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Клавиатура
def main_keyboard():
    kb = ReplyKeyboardBuilder()

    kb.button(text="📖 Помощь")
    kb.button(text="🎲 Случайное число")
    kb.button(text="🕒 Время")
    kb.button(text="👤 Мой профиль")
    kb.button(text="🧠 Узнать свой IQ")
    kb.button(text="🔢 Узнать свой настоящий возраст по таблице эпштейна 🤫")

    kb.adjust(2)

    return kb.as_markup(resize_keyboard=True)


# /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Наш ТГК: https://t.me/FRZTeam\n\n"
        "Выбери действие:",
        reply_markup=main_keyboard()
    )


# Помощь
@dp.message(lambda message: message.text == "📖 Помощь")
async def help_handler(message: Message):
    await message.answer(
        "Я умею:\n"
        "• 🎲 Генерировать случайные числа\n"
        "• 🕒 Показывать время\n"
        "• 👤 Показывать информацию о тебе\n"
        "• 🧠 Сказать твой реальный IQ\n"
        "• 🔢 Сказать твой реальный возраст"
    )


# Случайное число
@dp.message(lambda message: message.text == "🎲 Случайное число")
async def random_number(message: Message):
    number = random.randint(1, 100)
    await message.answer(f"🎲 Твое число: {number}")


# Время
@dp.message(lambda message: message.text == "🕒 Время")
async def time_handler(message: Message):
    now = datetime.now().strftime("%H:%M:%S")
    await message.answer(f"🕒 Сейчас {now}")


# IQ
@dp.message(lambda message: message.text == "🧠 Узнать свой IQ")
async def iq_handler(message: Message):
    number = random.randint(1, 160)

    await message.answer(f"🧠 Твой IQ: {number}")

    if number < 50:
        await message.answer(
            "Ти тупарилий ишак бля че ты тут делаешь те в детский садик завтра"
        )
    elif number < 100:
        await message.answer(
            "Ну лучше чем бля меньше 50 но все равно ты еще ишак"
        )
    elif number < 130:
        await message.answer(
            "Харош (скажи что я умнее пж😭)"
        )
    else:
        await message.answer(
            "Хули ты все еще тут сидишь без нобелевской премии иди в космос бля"
        )


# Возраст
@dp.message(
    lambda message: message.text ==
    "🔢 Узнать свой настоящий возраст по таблице эпштейна 🤫"
)
async def age_handler(message: Message):
    number = random.randint(1, 100)

    await message.answer(
        f"🔢 Твой настоящий возраст: {number}"
    )

    if number == 67:
        await message.answer(
            "Сиксевен сиксевен сиксевен 😭"
        )
    elif number < 10:
        await message.answer(
            "Пиривет мелкий 😂"
        )
    elif number < 20:
        await message.answer(
            "Как там школа? 🤨"
        )
    elif number < 30:
        await message.answer(
            "Работу ищи чудовище бля"
        )
    elif number < 50:
        await message.answer(
            "Все тебе нельзя больше на остров эпштейна 🤫"
        )
    else:
        await message.answer(
            "Иди на пенсию пень ржавый бля"
        )


# Профиль
@dp.message(lambda message: message.text == "👤 Мой профиль")
async def profile(message: Message):
    user = message.from_user

    await message.answer(
        f"👤 Имя: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📛 Username: @{user.username}"
    )


# Неизвестные команды
@dp.message()
async def unknown(message: Message):
    await message.answer(
        "Я пока не знаю такую команду 🤔"
    )


# Webhook
async def webhook(request):
    data = await request.json()

    await dp.feed_raw_update(
        bot,
        data
    )

    return web.Response()


async def main():
    print("TOKEN EXISTS:", TOKEN is not None)
    print("🤖 Бот запускается через webhook!")

    app = web.Application()

    app.router.add_post(
        "/webhook",
        webhook
    )

    webhook_url = os.getenv("WEBHOOK_URL")

    await bot.set_webhook(
        f"{webhook_url}/webhook"
    )

    runner = web.AppRunner(app)

    await runner.setup()

    port = int(
        os.getenv("PORT", 10000)
    )

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(
        f"🌐 Сервер запущен на порту {port}"
    )

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())