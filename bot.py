import asyncio
import logging
import random
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = "8323429693:AAFBnM2u7t9QUzps_sWlz7fxA5gCckfzGSg"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Создаем клавиатуру
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


# Команда /start
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

 # Узнать IQ
@dp.message(lambda message: message.text == "🧠 Узнать свой IQ")
async def iq_handler(message: Message):
    number = random.randint(1, 160)

    await message.answer(f"🧠 Твой IQ: {number}")

    if number < 50:
        await message.answer("Ти тупарилий ишак бля че ты тут делаешь те в детский садик завтра")
    elif number < 100:
        await message.answer("Ну лучше чем бля меньше 50 но все равно ты еще ишак")
    elif number < 130:
        await message.answer("Харош (скажи что я умнее пж😭)")
    else:
        await message.answer("Хули ты все еще тут сидишь без нобелевской премии иди в космос бля")

 # Узнать возраст
@dp.message(lambda message: message.text == "🔢 Узнать свой настоящий возраст по таблице эпштейна 🤫")
async def age_handler(message: Message):
    number = random.randint(1, 100)

    await message.answer(f"🔢 Твой настоящий возраст: {number}")

    if number == 67:
        await message.answer("Сиксевеееееееееен сиксевен, сиксевен, сиксевен, сиксевен, сиксевен, да короче я хотел песню газана сюда ебнуть но я ща другое слушаю и лень крч да но ты понял(а) рофлiк")
    elif number < 10:
        await message.answer("Пиривет иищак ммелкий миня звати Сосык яя аутисд")
    elif number < 20:
        await message.answer("Бля как те сложно там с впром в шкiлке бля дед инсайд аа у мя жизнь сложная пиздец")
    elif number < 30:
        await message.answer("Работу ищи чудовище бля")
    elif number < 50:
        await message.answer("Все тебе нельзя больше на остров эпстеина ойой то есть секретную вечеринку🤫")
    else:
        await message.answer("Иди на пенсию пень ржавый бля")


# Профиль
@dp.message(lambda message: message.text == "👤 Мой профиль")
async def profile(message: Message):
    user = message.from_user

    await message.answer(
        f"👤 Имя: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📛 Username: @{user.username}"
    )


# Если команда неизвестна
@dp.message()
async def unknown(message: Message):
    await message.answer("Я пока не знаю такую команду 🤔")


async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())