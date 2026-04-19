import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BotCommand
# ВОТ ЭТА СТРОКА ДОЛЖНА БЫТЬ ТУТ:
from aiogram.utils.chat_action import ChatActionSender 
from brain import get_answer_from_pdf
from dotenv import load_dotenv

# Загружаем ключи из .env
load_dotenv()

# Инициализируем бота и диспетчер
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()

# Функция для настройки меню команд (синяя кнопка "Меню" в углу)
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
    ]
    await bot.set_my_commands(commands)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я твой ИИ-помощник по учебникам.\n\n"
        "Я уже прочитал загруженные PDF-файлы. Просто задай мне вопрос по теме!"
    )

# Обработка любых текстовых сообщений
@dp.message(F.text)
async def handle_question(message: types.Message):
    # 1. Создаем контекстный менеджер "печатает"
    # Он будет автоматически продлевать статус, пока выполняется код внутри блока
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        
        # 2. Отправляем текстовое уведомление (как и раньше)
        status_msg = await message.answer("🔎 Ищу информацию в учебниках...")
        
        # 3. Запускаем "мозг" (поиск и Gemini)
        # Пока эта функция работает, вверху будет написано "печатает..."
        answer = get_answer_from_pdf(message.text)
        
        # 4. Убираем текстовый статус и присылаем ответ
        await status_msg.delete()
        await message.answer(answer)

# Запуск бота
async def main():
    await set_commands(bot)
    print("Бот успешно запущен! Напиши ему в Telegram.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен пользователем")