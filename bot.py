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
import json
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from zoneinfo import ZoneInfo
import time
from html import escape
card_lock = asyncio.Lock()

COOLDOWN = 3600  # секунд

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден!")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не найден!")

logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLLECTION_FILE = os.path.join(
    BASE_DIR,
    "data",
    "collection.json"
)

COOLDOWN_FILE = os.path.join(
    BASE_DIR,
    "data",
    "cooldowns.json"
)


def load_collection():
    if not os.path.exists(COLLECTION_FILE):
        return {}

    try:
        with open(COLLECTION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_collection(data):
    os.makedirs(
        os.path.dirname(COLLECTION_FILE),
        exist_ok=True
    )

    with open(COLLECTION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_cooldowns(data):
    os.makedirs(
        os.path.dirname(COOLDOWN_FILE),
        exist_ok=True
    )

    with open(COOLDOWN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_cooldowns():
    if not os.path.exists(COOLDOWN_FILE):
        return {}

    try:
        with open(COOLDOWN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


collection = load_collection()
cooldowns = load_cooldowns()

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
            [KeyboardButton(text="🎒 Моя коллекция")],
            [KeyboardButton(text="👁 Посмотреть карту")],
            [KeyboardButton(text="📊 Статистика")],
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
async def start(message: Message, state: FSMContext):
    await state.clear()
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
async def random_number(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        f"🎲 Твое число: {random.randint(1,100)}"
    )

@dp.message(lambda m: m.text == "🕒 Время")
async def time_handler(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        f"🕒 Сейчас {datetime.now(ZoneInfo('Europe/Moscow')).strftime('%H:%M:%S')}"
    )

@dp.message(lambda m: m.text == "👤 Мой профиль")
async def profile(message: Message, state: FSMContext):

    await state.clear()

    user = message.from_user
    username = f"@{user.username}" if user.username else "Нет"

    await message.answer(
        f"👤 Имя: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📛 Username: {username}"
    )

@dp.message(lambda m: m.text == "🧠 Узнать свой IQ")
async def iq_handler(message: Message, state: FSMContext):

    await state.clear()

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
async def age_handler(message: Message, state: FSMContext):

    await state.clear()

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
        },
        {
            "id": 10,
            "name": "Долбаеб",
            "file": "cards/card10.jpg",
            "animation": False,
            "text": "Долбаеб долбаеб ты долбаеб долбаеб"
        },
        {
            "id": 12,
            "name": "0_0",
            "file": "cards/card12.jpg",
            "animation": False,
            "text": "ватафак"
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
        },
        {
            "id": 11,
            "name": "Эпштейн сквад",
            "file": "cards/card11.jpg",
            "animation": False,
            "text": "🏝️"
        }
    ],

    "mythic": [
        {
            "id": 2,
            "name": "Абоба",
            "file": "cards/card2.jpg",
            "animation": False,
            "text": "(он сосет силли🤫)"
        },
        {
            "id": 13,
            "name": "Модiрацiя рiблокса",
            "file": "cards/card13.jpg",
            "animation": False,
            "text": "Вы были забанены за авто дыхание (Использование читов)"
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
        },
        {
            "id": 14,
            "name": "КТО ето?",
            "file": "cards/card14.jpg",
            "animation": False,
            "text": "ТОТАЛЬНО кто ето???"
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
class ViewCard(StatesGroup):
    waiting_id = State()

CARD_POOL = [

    # 🟢 Common (60%)
    ("common", CARDS["common"][0], 20),
    ("common", CARDS["common"][1], 20),
    ("common", CARDS["common"][2], 20),

    # 🔵 Rare (25%)
    ("rare", CARDS["rare"][0], 12.5),
    ("rare", CARDS["rare"][1], 12.5),

    # 🟣 Epic (10%)
    ("epic", CARDS["epic"][0], 5),
    ("epic", CARDS["epic"][1], 5),

    # 🔴 Mythic (8%)
    ("mythic", CARDS["mythic"][0], 4),
    ("mythic", CARDS["mythic"][1], 4),

    # 🟡 Legend (4%)
    ("legend", CARDS["legend"][0], 1.34),
    ("legend", CARDS["legend"][1], 1.33),
    ("legend", CARDS["legend"][2], 1.33),

    # ⚫ Secret (1%)
    ("secret", CARDS["secret"][0], 0.5),
    ("secret", CARDS["secret"][1], 0.5),
]
# Проверяем, что все файлы карт существуют
for rarity in CARDS.values():
    for card in rarity:
        path = os.path.join(BASE_DIR, card["file"])
        if not os.path.exists(path):
            logging.warning(f"Нет карты {path}")

@dp.message(lambda m: m.text == "🎭 Получить карту")
async def card(message: Message):

    async with card_lock:

        user_id = str(message.from_user.id)

        now = int(time.time())

        last = cooldowns.get(user_id, 0)

        if now - last < COOLDOWN:
            left = COOLDOWN - (now - last)

            hours = left // 3600
            minutes = (left % 3600) // 60
            seconds = left % 60

            await message.answer(
                f"⏳ Получить новую карту можно через "
                f"{hours} ч. {minutes} мин. {seconds} сек."
            )
            return

        if user_id not in collection:
            collection[user_id] = []

        rarity, card, _ = random.choices(
            CARD_POOL,
            weights=[c[2] for c in CARD_POOL],
            k=1
        )[0]

        ...

    duplicate = str(card["id"]) in collection[user_id]

    path = os.path.join(BASE_DIR, card["file"])

    # Если карты ещё нет — сохраняем
    if not duplicate:
        collection[user_id].append(str(card["id"]))
        save_collection(collection)

    if not os.path.exists(path):
        await message.answer("❌ Файл карты не найден.")
        return

    file = FSInputFile(path)

    caption = (
        f"🎭 <b>Карта #{['id']}</b>\n\n"
        f"📛 {escape(['name'])}\n"
        f"⭐ {RARITY_NAMES[rarity]}\n\n"
        f"💬 {escape(['text'])}"
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

    if duplicate:
        await message.answer(
            "♻️ Повторка!\n"
            "Эта карта уже есть в твоей коллекции."
        )
    else:
        await message.answer(
            "🎉 Новая карта!\n"
            "Она добавлена в твою коллекцию."
        )

    logging.info(
        f"{message.from_user.id} получил карту #{card['id']}"
    )
    cooldowns[user_id] = now
    save_cooldowns(cooldowns)

@dp.message(lambda m: m.text == "📚 Редкости и карты")
async def cards_info(message: Message):

    text = (
        "🎭 <b>Редкости карт</b>\n\n"
        "🟢 Обычная — 60%\n"
        "🔵 Редкая — 25%\n"
        "🟣 Эпическая — 10%\n"
        "🔴 Мифическая — 8%\n"
        "🟡 Легендарная — 4%\n"
        "⚫ Секретная — 1%\n\n"
        "<b>📖 Все карты</b>\n\n"
    )

    rarities = [
        ("common", "🟢"),
        ("rare", "🔵"),
        ("epic", "🟣"),
        ("mythic", "🔴"),
        ("legend", "🟡"),
        ("secret", "⚫"),
    ]

    for rarity, emoji in rarities:
        text += f"{emoji} <b>{RARITY_NAMES[rarity]}</b>\n"

        for card in CARDS[rarity]:
            text += f"🎴 #{card['id']} — {card['name']}\n"

        text += "\n"

    await message.answer(text, parse_mode="HTML")

@dp.message(lambda m: m.text == "🎒 Моя коллекция")
async def my_collection(message: Message):

    user_id = str(message.from_user.id)

    if user_id not in collection or not collection[user_id]:
        await message.answer("📭 У тебя пока нет карточек.")
        return

    text = "🎒 <b>Твоя коллекция</b>\n\n"

    counts = {}

    for card_id in collection[user_id]:
        counts[card_id] = counts.get(card_id, 0) + 1

    for rarity in ["common", "rare", "epic", "mythic", "legend", "secret"]:
        cards = CARDS[rarity]
        for card in cards:
            if str(card["id"]) in counts:
                text += (
                    f"🎴 #{card['id']} — {card['name']}\n"
                    )

    text += (
        f"\n📦 Всего карт: {len(collection[user_id])}"
    )

    await message.answer(text, parse_mode="HTML")

@dp.message(lambda m: m.text == "👁 Посмотреть карту")
async def ask_card(message: Message, state: FSMContext):
        await message.answer("Напиши ID карты.")
        await state.set_state(ViewCard.waiting_id)

@dp.message(ViewCard.waiting_id)
async def show_card(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("Введите число.")
        return

    card_id = int(message.text)

    found = None
    rarity = None

    for r, cards in CARDS.items():
        for c in cards:
            if c["id"] == card_id:
                found = c
                rarity = r
                break
        if found:
            break

    if found is None:
        await message.answer("Такой карты нет.")
        await state.clear()
        return

    user_id = str(message.from_user.id)

    if user_id not in collection or str(card_id) not in collection[user_id]:
        await message.answer("❌ У тебя нет этой карты.")
        await state.clear()
        return

    path = os.path.join(BASE_DIR, found["file"])

    file = FSInputFile(path)

    caption = (
        f"🎭 <b>Карта #{found['id']}</b>\n\n"
        f"📛 {found['name']}\n"
        f"⭐ {RARITY_NAMES[rarity]}\n\n"
        f"💬 {found['text']}"
    )

    if found["animation"]:
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

    await state.clear()

@dp.message(lambda m: m.text == "📊 Статистика")
async def stats(message: Message):

    user_id = str(message.from_user.id)

    if user_id not in collection:
        await message.answer("Коллекция пустая.")
        return

    owned = set(collection[user_id])

    rarity_count = {
        "common": 0,
        "rare": 0,
        "epic": 0,
        "mythic": 0,
        "legend": 0,
        "secret": 0,
    }

    for rarity, cards in CARDS.items():
        for card in cards:
            if str(card["id"]) in owned:
                rarity_count[rarity] += 1

    total_cards = sum(len(cards) for cards in CARDS.values())
    have = len(owned)

    percent = have / total_cards * 100

    text = (
    "📊 <b>Статистика коллекции</b>\n\n"
    f"🎴 Собрано: <b>{have}/{total_cards}</b>\n"
    f"📈 Прогресс: <b>{percent:.1f}%</b>\n\n"
    f"🟢 {rarity_count['common']}/{len(CARDS['common'])}\n"
    f"🔵 {rarity_count['rare']}/{len(CARDS['rare'])}\n"
    f"🟣 {rarity_count['epic']}/{len(CARDS['epic'])}\n"
    f"🔴 {rarity_count['mythic']}/{len(CARDS['mythic'])}\n"
    f"🟡 {rarity_count['legend']}/{len(CARDS['legend'])}\n"
    f"⚫ {rarity_count['secret']}/{len(CARDS['secret'])}"
)

    await message.answer(text, parse_mode="HTML")

# Неизвестные команды
@dp.message()
async def unknown(message: Message):
    await message.answer("Я пока не знаю такую команду 🤔")


# Webhook
async def webhook(request):
    data = await request.json()
    await dp.feed_raw_update(bot, data)
    return web.Response()


async def main():
    print("TOKEN EXISTS:", TOKEN is not None)
    print("🤖 Бот запускается через webhook!")

    app = web.Application()

    app.router.add_post(
        "/webhook",
        webhook
    )
    
    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_webhook(
        f"{WEBHOOK_URL}/webhook"
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

    
