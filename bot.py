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
from aiogram.types import FSInputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

CARD_WEIGHTS = [60, 4, 10, 25, 4, 25, 4, 1]
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Клавиатура
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

@dp.message(lambda message: message.text == "🎭 Карты (бета)")
async def cards_menu(message: Message):
    await message.answer(
        "🎭 Меню карточек\n\nВыберите действие:",
        reply_markup=cards_keyboard()
    )

@dp.message(lambda message: message.text == "⬅️ Назад")
async def back(message: Message):
    await message.answer(
        "Главное меню",
        reply_markup=main_keyboard()
    )

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
        "• 🔢 Сказать твой реальный возраст\n"
        "• 🎭 Система карточек (бета)"
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

 # Карты
@dp.message(lambda message: message.text == "🎭 Получить карту")
async def card(message: Message):
    number = random.choices(
    range(1, 9),
    weights=CARD_WEIGHTS,
    k=1
)[0]

    if number == 1:
        photo = FSInputFile("cards/card1.jpg")
        text = (
            "🎭 <b>Карта #1</b>\n\n"
            "📛 Silly\n"
            "⭐ Редкость: Обычная🟢\n\n"
            "💬 Это такая залупа не завидую те бро😭"
        )

    elif number == 2:
        photo = FSInputFile("cards/card2.jpg")
        text = (
            "🎭 <b>Карта #2</b>\n\n"
            "📛 Абоба\n"
            "⭐ Редкость: Мифическая🔴\n\n"
            "💬 (он сосет силли🤫)"
        )

    elif number == 3:
        photo = FSInputFile("cards/card3.jpg")
        text = (
            "🎭 <b>Карта #3</b>\n\n"
            "📛 Лемончик\n"
            "⭐ Редкость: Эпическая🟣\n\n"
            "💬 Месси месси месси месси месси месси и анкара месси анкара месси анкара месси анкара месси гол гол гол гол гол гол гол⚽"
        )

    elif number == 4:
        photo = FSInputFile("cards/card4.jpg")
        text = (
            "🎭 <b>Карта #4</b>\n\n"
            "📛 N*ggbear\n"
            "⭐ Редкость: Редкая🔵\n\n"
            "💬 ето ТОТАЛЬНО не я бро"
        )

    elif number == 5:
        photo = FSInputFile("cards/card5.jpg")
        text = (
            "🎭 <b>Карта #5</b>\n\n"
            "📛 Frozzz\n"
            "⭐ Редкость: Легендарная🟡\n\n"
            "💬 Все же он знал секрет тун тун тун сахура..."
        )

    elif number == 6:
        photo = FSInputFile("cards/card6.jpg")
        text = (
            "🎭 <b>Карта #6</b>\n\n"
            "📛 VERITY💔\n"
            "⭐ Редкость: Редкая🔵\n\n"
            "💬 Секретная концовка 5 обстрелов на #@%$^ 3.."
        )

    elif number == 7:
        photo = FSInputFile("cards/card7.jpg")
        text = (
            "🎭 <b>Карта #7</b>\n\n"
            "📛 Онлайн мошеннiк\n"
            "⭐ Редкость: Легендарная🟡\n\n"
            "💬 Заплатi 5 рiбуксов или я подам рiпорт за авто дiхание😡"
        )

    else:
        photo = FSInputFile("cards/card8.jpg")
        text = (
            "🎭 <b>Карта #8</b>\n\n"
            "📛 Файлы эпштейна DLC\n"
            "⭐ Редкость: Секретная⚫\n\n"
            "💬 Ето не должно било бить тут??"
        )

    await message.answer_photo(
        photo=photo,
        caption=text,
        parse_mode="HTML"
    )
        
# Редкости и карты
@dp.message(lambda message: message.text == "📚 Редкости и карты")
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
        "8️⃣ Файлы эпштейна DLC ⚫",
        parse_mode="HTML"
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