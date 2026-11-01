import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    FSInputFile
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

# Токен уже ДРУГОГО бота (DropStudio)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в переменных окружения")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Описание подобрано под функционал вашего HTML (релизы, статистика, альбомы)
WELCOME_TEXT = (
    "🎛 <b>Добро пожаловать в DropStudio!</b>\n\n"
    "Это твоя личная студия артиста прямо в Telegram. Здесь ты управляешь своей музыкой:\n\n"
    "📊 <b>Статистика</b> — следи за прослушиваниями, лайками и вовлечённостью\n"
    "🗂 <b>Карточка</b> — настрой аватар, шапку профиля и соцсети\n"
    "🎵 <b>Релизы</b> — загружай треки, добавляй обложки и выбирай жанры\n"
    "⏱ <b>Планирование</b> — настраивай дату выхода и пресейвы\n"
    "💽 <b>Альбомы</b> — собирай свои треки в плейлисты\n\n"
    "👇 Нажми кнопку ниже, чтобы открыть студию и начать творить!"
)

# Ваша ссылка на Mini App
STUDIO_URL = "https://t.me/droptunestudio_bot?startapp=game_heart"

def studio_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎛 Открыть DropStudio",
                    url=STUDIO_URL,
                )
            ]
        ]
    )

dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    # Если хотите добавить картинку, положите файл welcome_studio.jpg рядом с кодом
    photo_path = "welcome_studio.jpg" 
    
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(
            photo=photo,
            caption=WELCOME_TEXT,
            reply_markup=studio_keyboard(),
            parse_mode=ParseMode.HTML
        )
    else:
        # Если картинки нет, отправит просто красивый текст
        await message.answer(
            WELCOME_TEXT,
            reply_markup=studio_keyboard(),
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML
        )

@dp.message(F.text == "/help")
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Команды:\n/start — показать приветствие и кнопку входа в студию\n/help — эта справка"
    )

# --- Фейковый веб-сервер для Render (чтобы не было ошибки "No open ports") ---
async def handle(request):
    return web.Response(text="DropStudio Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Веб-сервер запущен на порту {port}")

async def main() -> None:
    asyncio.create_task(start_web_server())
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    logger.info("DropStudio Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
