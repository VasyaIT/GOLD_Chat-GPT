from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.exceptions import CantParseEntities, MessageToDeleteNotFound

from middleware import wait_answer_by_gpt, AntiFloodMiddleware, r
from openai_api import generate_answer
from utils import GREETING_TEXT
import config


bot = Bot(config.BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=RedisStorage2())


async def on_startup(_) -> None:
    print('Бот запущен')


@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    await message.answer(GREETING_TEXT.format(message.from_user.first_name))


@dp.message_handler(commands=['creator'])
async def creator(message: types.Message) -> None:
    await message.answer('Мой творец - <b>@Solevaaaya</b>')


@dp.message_handler()
@wait_answer_by_gpt
async def ask(message: types.Message) -> None:
    user_id = message.from_user.id
    await message.answer('Ща отвечу, жди')
    answer = await generate_answer(message.text, user_id)
    try:
        await bot.delete_message(message.chat.id, message.message_id + 1)
    except MessageToDeleteNotFound:
        pass
    try:
        await message.answer(answer)
    except CantParseEntities:
        await message.answer('Ошибка на сервере')
    await r.delete(f'ask:{user_id}')
    await r.close()


@dp.errors_handler(exception=Exception)
async def all_exception_handler(update: types.Update, exception: Exception) -> None:
    for admin in config.ADMINS:
        await bot.send_message(
            admin,
            f'Бот упал\n\n{exception} | '
            f'user_id: {update.message.from_id} | text: {update.message.text}'
        )
    config.logger.error(
        f'{exception} | user_id: {update.message.from_id} | text: {update.message.text}'
    )


if __name__ == "__main__":
    dp.middleware.setup(AntiFloodMiddleware())
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
