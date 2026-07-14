import asyncio
import logging
import random
import os
from datetime import datetime

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher()

def main_keyboard():
    kb = ReplyKeyboardBuilder()

    kb.button(text="🎭 Карты (бета)")
    kb.button(text="📖 Помощь")
    kb.button(text="🎲 Случайное число")
    kb.button(text="🕒 Время")
    kb.button(text="👤 Мой профиль")
    kb.button(text="🧠 Узнать свой IQ")
    kb.button(text="🔢 Узнать свой настоящий возраст по таблице эпштейна 🤫")

    kb.adjust(2)

    return kb.as_markup(resize_keyboard=True)


def cards_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎭 Получить карту")],
            [KeyboardButton(text="📚 Редкости и карты")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

@dp.message(lambda m: m.text == "🎭 Карты (бета)")
async def cards_menu(message: Message):
    await message.answer(
        "🎭 Меню карточек",
        reply_markup=cards_keyboard()
    )


@dp.message(lambda m: m.text == "⬅️ Назад")
async def back(message: Message):
    await message.answer(
        "Главное меню",
        reply_markup=main_keyboard()
    )

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Наш ТГК: https://t.me/FRZTeam\n\n"
        "Выбери действие:",
        reply_markup=main_keyboard()
    )

@dp.message(lambda m: m.text == "📖 Помощь")
async def help_handler(message: Message):
    await message.answer(
        "Я умею:\n"
        "• 🎲 Генерировать случайные числа\n"
        "• 🕒 Показывать время\n"
        "• 👤 Показывать информацию о тебе\n"
        "• 🧠 Узнавать IQ\n"
        "• 🔢 Узнавать возраст\n"
        "• 🎭 Карточки"
    )

@dp.message(lambda m: m.text == "🎲 Случайное число")
async def random_number(message: Message):
    await message.answer(
        f"🎲 Твое число: {random.randint(1,100)}"
    )

@dp.message(lambda m: m.text == "🕒 Время")
async def time_handler(message: Message):
    await message.answer(
        f"🕒 Сейчас {datetime.now().strftime('%H:%M:%S')}"
    )

@dp.message(lambda m: m.text == "👤 Мой профиль")
async def profile(message: Message):

    user = message.from_user
    username = f"@{user.username}" if user.username else "Нет"

    await message.answer(
        f"👤 Имя: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📛 Username: {username}"
    )

@dp.message(lambda m: m.text == "🧠 Узнать свой IQ")
async def iq_handler(message: Message):

    iq = random.randint(1,160)

    await message.answer(f"🧠 Твой IQ: {iq}")

    if iq < 50:
        await message.answer("Ти тупарилий ишак бля")
    elif iq < 100:
        await message.answer("Ну уже получше 😂")
    elif iq < 130:
        await message.answer("Харош 😎")
    else:
        await message.answer("Иди получай Нобелевскую премию 🚀")

@dp.message(lambda m: m.text == "🔢 Узнать свой настоящий возраст по таблице эпштейна 🤫")
async def age_handler(message: Message):

    age = random.randint(1,100)

    await message.answer(
        f"🔢 Твой настоящий возраст: {age}"
    )

    if age == 67:
        await message.answer("Сиксевен 😭")
    elif age < 10:
        await message.answer("Пиривет мелкий 😂")
    elif age < 20:
        await message.answer("Как школа?")
    elif age < 30:
        await message.answer("Работу ищи 😂")
    elif age < 50:
        await message.answer("На остров уже нельзя 🤫")
    else:
        await message.answer("Иди на пенсию 😂")

RARITY_NAMES = {
    "common": "🟢 Обычная",
    "rare": "🔵 Редкая",
    "epic": "🟣 Эпическая",
    "mythic": "🔴 Мифическая",
    "legend": "🟡 Легендарная",
    "secret": "⚫ Секретная"
}

CARDS = {
    "common": [
        {
            "id": 1,
            "name": "Silly",
            "file": "cards/card1.jpg",
            "animation": False,
            "text": "Это такая залупа не завидую те бро😭"
        }
    ],

    "rare": [
        {
            "id": 4,
            "name": "N*ggbear",
            "file": "cards/card4.jpg",
            "animation": False,
            "text": "ето ТОТАЛЬНО не я бро"
        },
        {
            "id": 6,
            "name": "VERITY💔",
            "file": "cards/card6.jpg",
            "animation": False,
            "text": "Секретная концовка..."
        }
    ],

    "epic": [
        {
            "id": 3,
            "name": "Лемончик",
            "file": "cards/card3.jpg",
            "animation": False,
            "text": "Месси месси⚽"
        }
    ],

    "mythic": [
        {
            "id": 2,
            "name": "Абоба",
            "file": "cards/card2.jpg",
            "animation": False,
            "text": "(он сосет силли🤫)"
        }
    ],

    "legend": [
        {
            "id": 5,
            "name": "Frozzz",
            "file": "cards/card5.jpg",
            "animation": False,
            "text": "Все же он знал секрет..."
        },
        {
            "id": 7,
            "name": "Онлайн мошенник",
            "file": "cards/card7.jpg",
            "animation": False,
            "text": "Заплати 5 робуксов😡"
        }
    ],

    "secret": [
        {
            "id": 8,
            "name": "Файлы эпштейна DLC",
            "file": "cards/card8.jpg",
            "animation": False,
            "text": "Это не должно было быть тут..."
        },
        {
            "id": 9,
            "name": "P1mple",
            "file": "cards/card9.gif",
            "animation": True,
            "text": "Прафiсiонал из Адопт мi"
        }
    ]
}

@dp.message(lambda m: m.text == "🎭 Получить карту")
async def card(message: Message):

    rarity = random.choices(
        population=[
            "common",
            "rare",
            "epic",
            "mythic",
            "legend",
            "secret"
        ],
        weights=[60, 25, 10, 8, 4, 1],
        k=1
    )[0]

    card = random.choice(CARDS[rarity])

    if not os.path.exists(card["file"]):
        await message.answer(f"Файл {card['file']} не найден.")
        return

    file = FSInputFile(card["file"])

    caption = (
        f"🎭 <b>Карта #{card['id']}</b>\n\n"
        f"📛 {card['name']}\n"
        f"⭐ Редкость: {RARITY_NAMES[rarity]}\n\n"
        f"💬 {card['text']}"
    )

    if card["animation"]:
        await message.answer_animation(
            animation=file,
            caption=caption,
            parse_mode="HTML"
        )
    else:
        await message.answer_photo(
            photo=file,
            caption=caption,
            parse_mode="HTML"
        )

@dp.message(lambda m: m.text == "📚 Редкости и карты")
async def cards_info(message: Message):
    await message.answer(
        "🎭 <b>Редкости карт</b>\n\n"
        "🟢 Обычная — 60%\n"
        "🔵 Редкая — 25%\n"
        "🟣 Эпическая — 10%\n"
        "🔴 Мифическая — 8%\n"
        "🟡 Легендарная — 4%\n"
        "⚫ Секретная — 1%\n\n"
        "<b>📖 Список карт</b>\n"
        "1️⃣ Silly 🟢\n"
        "2️⃣ Абоба 🔴\n"
        "3️⃣ Лемончик 🟣\n"
        "4️⃣ N*ggbear 🔵\n"
        "5️⃣ Frozzz 🟡\n"
        "6️⃣ VERITY💔 🔵\n"
        "7️⃣ Онлайн мошенник 🟡\n"
        "8️⃣ Файлы эпштейна DLC ⚫\n"
        "9️⃣ P1mple ⚫",
        parse_mode="HTML"
    )

# Неизвестные команды
@dp.message()
async def unknown(message: Message):
    await message.answer("Я пока не знаю такую команду 🤔")


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

    port = int(os.getenv("PORT", 10000))

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(f"🌐 Сервер запущен на порту {port}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())

webhook_url = os.getenv("WEBHOOK_URL")

if not webhook_url:
    raise ValueError("WEBHOOK_URL не найден!")
