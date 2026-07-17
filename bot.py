import asyncio
import logging
import random
import os
import time
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден")

def get_db():
    return psycopg2.connect(DATABASE_URL)

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

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

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


# ==========================
# НАСТРОЙКИ
# ==========================

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не найден")


logging.basicConfig(
    level=logging.INFO
)


bot = Bot(TOKEN)
dp = Dispatcher()


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


COOLDOWN = 3600


card_lock = asyncio.Lock()

print("Подключение к:", DATABASE_URL.split("@")[1])

def init_db():

    conn = get_db()
    cur = conn.cursor()


    cur.execute("""
    CREATE TABLE IF NOT EXISTS collections(
        user_id TEXT,
        card_id TEXT,
        PRIMARY KEY(user_id, card_id)
    )
    """)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS cooldowns(
        user_id TEXT PRIMARY KEY,
        time BIGINT
    )
    """)


    conn.commit()

    cur.close()
    conn.close()


init_db()

def get_collection(user_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT card_id FROM collections WHERE user_id=%s",
        (user_id,)
    )

    result = [
        row[0]
        for row in cur.fetchall()
    ]

    cur.close()
    conn.close()

    return result



def add_card(user_id, card_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO collections(user_id, card_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (user_id, str(card_id)))

    conn.commit()

    cur.close()
    conn.close()



def get_cooldown(user_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT time FROM cooldowns WHERE user_id=%s",
        (user_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row[0] if row else 0



def set_cooldown(user_id, value):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO cooldowns(user_id,time)
        VALUES(%s,%s)
        ON CONFLICT(user_id)
        DO UPDATE SET time=EXCLUDED.time
        """,
        (user_id,value)
    )

    conn.commit()

    cur.close()
    conn.close()

# ==========================
# СОХРАНЕНИЕ
# ==========================

# ==========================
# КЛАВИАТУРЫ
# ==========================


def main_keyboard():

    kb = ReplyKeyboardBuilder()


    buttons = [
        "🎭 Карты (бета)",
        "📖 Помощь",
        "🎲 Случайное число",
        "🕒 Время",
        "👤 Мой профиль",
        "🧠 Узнать свой IQ",
        "🔢 Узнать свой настоящий возраст по таблице эпштейна 🤫"
    ]


    for b in buttons:
        kb.button(
            text=b
        )


    kb.adjust(2)


    return kb.as_markup(
        resize_keyboard=True
    )



def cards_keyboard():

    return ReplyKeyboardMarkup(
        keyboard=[

            [
                KeyboardButton(
                    text="🎭 Получить карту"
                )
            ],

            [
                KeyboardButton(
                    text="🎒 Моя коллекция"
                )
            ],

            [
                KeyboardButton(
                    text="👁 Посмотреть карту"
                )
            ],

            [
                KeyboardButton(
                    text="📊 Статистика"
                )
            ],

            [
                KeyboardButton(
                    text="📚 Редкости и карты"
                )
            ],

            [
                KeyboardButton(
                    text="⬅️ Назад"
                )
            ]

        ],
        resize_keyboard=True
    )



# ==========================
# СТАРТ
# ==========================


@dp.message(Command("start"))
async def start(
    message: Message,
    state: FSMContext
):

    await state.clear()


    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Наш ТГК: https://t.me/FRZTeam\n\n"
        "Выбери действие:",
        reply_markup=main_keyboard()
    )



@dp.message(
    lambda m: m.text == "⬅️ Назад"
)
async def back(
    message: Message
):

    await message.answer(
        "Главное меню",
        reply_markup=main_keyboard()
    )



@dp.message(
    lambda m: m.text == "🎭 Карты (бета)"
)
async def cards_menu(
    message: Message
):

    await message.answer(
        "🎭 Меню карточек",
        reply_markup=cards_keyboard()
    )



# ==========================
# ПРОСТЫЕ ФУНКЦИИ
# ==========================


@dp.message(
    lambda m: m.text == "📖 Помощь"
)
async def help_handler(
    message: Message
):

    await message.answer(
        "Я умею:\n\n"
        "🎲 Случайные числа\n"
        "🕒 Время\n"
        "👤 Профиль\n"
        "🧠 IQ\n"
        "🔢 Возраст\n"
        "🎭 Карточки (бета)"
    )



@dp.message(
    lambda m: m.text == "🎲 Случайное число"
)
async def random_number(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        f"🎲 Твоё число: {random.randint(1,100)}"
    )



@dp.message(
    lambda m: m.text == "🕒 Время"
)
async def time_handler(
    message: Message,
    state: FSMContext
):

    await state.clear()


    await message.answer(
        "🕒 Сейчас "
        +
        datetime.now(
            ZoneInfo("Europe/Moscow")
        ).strftime(
            "%H:%M:%S"
        )
    )



@dp.message(
    lambda m: m.text == "👤 Мой профиль"
)
async def profile(
    message: Message,
    state: FSMContext
):

    await state.clear()


    user = message.from_user


    username = (
        f"@{user.username}"
        if user.username
        else "Нет"
    )


    await message.answer(
        f"👤 Имя: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📛 Username: {username}"
    )



@dp.message(
    lambda m: m.text == "🧠 Узнать свой IQ"
)
async def iq(
    message: Message,
    state: FSMContext
):

    await state.clear()


    value = random.randint(
        1,
        160
    )


    await message.answer(
        f"🧠 Твой IQ: {value}"
    )



    if value < 50:
        await message.answer(
            "Ну тут надо потренироваться 😂"
        )

    elif value < 100:
        await message.answer(
            "Нормально 👍"
        )

    elif value < 130:
        await message.answer(
            "Хороший результат 😎"
        )

    else:
        await message.answer(
            "Гений 🚀"
        )



@dp.message(
    lambda m: m.text == "🔢 Узнать свой настоящий возраст по таблице эпштейна 🤫"
)
async def age(
    message: Message,
    state: FSMContext
):

    await state.clear()


    value = random.randint(
        1,
        100
    )


    await message.answer(
        f"🔢 Твой настоящий возраст: {value}"
    )

# ==========================
# КАРТОЧКИ
# ==========================


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
            "text": "Долбаеб долбаеб ты долбаеб"
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
            "name": "Модерация риблокса",
            "file": "cards/card13.jpg",
            "animation": False,
            "text": "Вы были забанены за авто дыхание"
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



RARITY_WEIGHTS = {

    "common": 52,
    "rare": 25,
    "epic": 10,
    "mythic": 8,
    "legend": 4,
    "secret": 1

}



# проверка файлов

for rarity in CARDS.values():

    for card in rarity:

        path = os.path.join(
            BASE_DIR,
            card["file"]
        )

        if not os.path.exists(path):

            logging.warning(
                f"Нет файла: {path}"
            )




# ==========================
# СОСТОЯНИЕ ПРОСМОТРА
# ==========================


class ViewCard(StatesGroup):

    waiting_id = State()




# ==========================
# ПОЛУЧИТЬ КАРТУ
# ==========================


@dp.message(
    lambda m: m.text == "🎭 Получить карту"
)
async def get_card(
    message: Message
):


    user_id = str(
        message.from_user.id
    )


    now = int(
        time.time()
    )



    last = get_cooldown(user_id)



    if now - last < COOLDOWN:


        left = COOLDOWN - (
            now - last
        )


        hours = left // 3600
        minutes = (left % 3600) // 60
        seconds = left % 60

        time_text = ""

        if hours:
            time_text += f"{hours} ч. "

        if minutes:
            time_text += f"{minutes} мин. "

        time_text += f"{seconds} сек."

        await message.answer(
            f"⏳ Следующая карта через {time_text}"
        )

        return



    async with card_lock:

        rarity = random.choices(

            list(
                RARITY_WEIGHTS.keys()
            ),

            weights=list(
                RARITY_WEIGHTS.values()
            ),

            k=1

        )[0]



        card = random.choice(
            CARDS[rarity]
        )



        user_cards = get_collection(user_id)

        duplicate = (
            str(card["id"])
            in user_cards
    )



    path = os.path.join(
        BASE_DIR,
        card["file"]
    )



    if not os.path.exists(path):

        await message.answer(
            "❌ Файл карты не найден"
        )

        return



    file = FSInputFile(
        path
    )



    caption = (

        f"🎭 <b>Карта #{card['id']}</b>\n\n"

        f"📛 {escape(card['name'])}\n"

        f"⭐ {RARITY_NAMES[rarity]}\n\n"

        f"💬 {escape(card['text'])}"

    )



    try:


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



    except Exception as e:


        logging.error(e)


        await message.answer(
            "❌ Ошибка отправки карты"
        )

        return



    if not duplicate:


        add_card(
            user_id,
            card["id"]
        )



        await message.answer(
            "🎉 Новая карта добавлена в твою коллекцию!"
        )


    else:


        await message.answer(
            "♻️ Повторка! Такая карта уже есть"
        )



    set_cooldown(
        user_id,
        now
    )

@dp.message(lambda m: m.text == "🎒 Моя коллекция")
async def my_collection(message: Message):

    user_id = str(message.from_user.id)

    cards = get_collection(user_id)

    if not cards:
        await message.answer("📭 У тебя пока нет карточек.")
        return

    text = "🎒 <b>Твоя коллекция</b>\n\n"

    owned = {}

    for card_id in cards:
        owned[card_id] = owned.get(card_id, 0) + 1

    for rarity in CARDS:
        for card in CARDS[rarity]:

            if str(card["id"]) in owned:

                count = owned[str(card["id"])]

                text += (
                    f"🎴 #{card['id']} — {card['name']}"
                )

                if count > 1:
                    text += f" x{count}"

                text += "\n"

    text += f"\n📦 Всего карт: {len(cards)}"

    await message.answer(
        text,
        parse_mode="HTML"
    )


@dp.message(lambda m: m.text == "👁 Посмотреть карту")
async def ask_card(
    message: Message,
    state: FSMContext
):

    await message.answer(
        "Введите ID карты:"
    )

    await state.set_state(
        ViewCard.waiting_id
    )


@dp.message(ViewCard.waiting_id)
async def show_card(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "❌ Нужно написать число."
        )
        return


    card_id = int(message.text)

    found = None
    rarity = None


    for r, cards in CARDS.items():

        for card in cards:

            if card["id"] == card_id:

                found = card
                rarity = r
                break

        if found:
            break


    if not found:

        await message.answer(
            "❌ Такой карты нет."
        )

        await state.clear()
        return


    user_id = str(message.from_user.id)


    if str(card_id) not in get_collection(user_id):

        await message.answer(
            "❌ У тебя нет этой карты."
        )

        await state.clear()
        return



    path = os.path.join(
        BASE_DIR,
        found["file"]
    )


    if not os.path.exists(path):

        await message.answer(
            "❌ Файл карты отсутствует."
        )

        await state.clear()
        return


    file = FSInputFile(path)


    caption = (
        f"🎭 <b>Карта #{found['id']}</b>\n\n"
        f"📛 {escape(found['name'])}\n"
        f"⭐ {RARITY_NAMES[rarity]}\n\n"
        f"💬 {escape(found['text'])}"
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


    if not get_collection(user_id):

        await message.answer(
            "📭 Коллекция пустая."
        )

        return



    owned = set(
        get_collection(user_id)
    )


    rarity_count = {}

    for rarity in CARDS:

        rarity_count[rarity] = 0


    for rarity, cards in CARDS.items():

        for card in cards:

            if str(card["id"]) in owned:

                rarity_count[rarity] += 1



    total = sum(
        len(cards)
        for cards in CARDS.values()
    )


    have = len(owned)


    percent = (
        have / total * 100
        if total
        else 0
    )


    text = (

        "📊 <b>Статистика</b>\n\n"

        f"🎴 Собрано: "
        f"<b>{have}/{total}</b>\n"

        f"📈 Прогресс: "
        f"<b>{percent:.1f}%</b>\n\n"

        f"🟢 {rarity_count['common']}/{len(CARDS['common'])}\n"
        f"🔵 {rarity_count['rare']}/{len(CARDS['rare'])}\n"
        f"🟣 {rarity_count['epic']}/{len(CARDS['epic'])}\n"
        f"🔴 {rarity_count['mythic']}/{len(CARDS['mythic'])}\n"
        f"🟡 {rarity_count['legend']}/{len(CARDS['legend'])}\n"
        f"⚫ {rarity_count['secret']}/{len(CARDS['secret'])}"

    )


    await message.answer(
        text,
        parse_mode="HTML"
    )



@dp.message(lambda m: m.text == "📚 Редкости и карты")
async def cards_info(message: Message):

    text = (
        "🎭 <b>Редкости:</b>\n\n"
        "🟢 Обычная — 52%\n"
        "🔵 Редкая — 25%\n"
        "🟣 Эпическая — 10%\n"
        "🔴 Мифическая — 8%\n"
        "🟡 Легендарная — 4%\n"
        "⚫ Секретная — 1%\n\n"
        "📚 <b>Карты:</b>\n\n"
    )


    for rarity, cards in CARDS.items():

        text += (
            f"{RARITY_NAMES[rarity]}\n"
        )

        for card in cards:

            text += (
                f"🎴 #{card['id']} "
                f"{card['name']}\n"
            )

        text += "\n"


    await message.answer(
        text,
        parse_mode="HTML"
    )



@dp.message()
async def unknown(message: Message):

    await message.answer(
        "🤔 Неизвестная команда."
    )



async def webhook(request):

    try:

        data = await request.json()

        await dp.feed_raw_update(
            bot,
            data
        )

        return web.Response()


    except Exception as e:

        logging.exception(e)

        return web.Response(
            status=500
        )



async def main():

    logging.info(
        "🤖 Бот запускается..."
    )


    app = web.Application()


    app.router.add_post(
        "/webhook",
        webhook
    )


    await bot.delete_webhook(
        drop_pending_updates=True
    )


    await bot.set_webhook(
        f"{WEBHOOK_URL}/webhook"
    )


    runner = web.AppRunner(app)

    await runner.setup()


    port = int(
        os.getenv(
            "PORT",
            10000
        )
    )


    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )


    await site.start()


    logging.info(
        f"🌐 Сервер запущен {port}"
    )


    await asyncio.Event().wait()



if __name__ == "__main__":

    asyncio.run(main())