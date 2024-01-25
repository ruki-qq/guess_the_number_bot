import random

from dotenv import dotenv_values
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from sqlalchemy.future import select

from db.database import User
from db.async_session import get_session
from path_config import ENV_DIR

env = dotenv_values(ENV_DIR)
BOT_TOKEN = env.get('TOKEN')

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


ATTEMPTS = 5

users = {}


def get_random_number() -> int:
    return random.randint(1, 100)


@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        'Привет!\nДавайте сыграем в игру "Угадай число"?\n\n'
        'Чтобы получить правила игры и список доступных '
        'команд - отправьте команду /help'
    )
    user_id = message.from_user.id
    async with get_session() as session:
        res = await session.execute(select(User).filter_by(id=user_id))
        existing_user = res.scalars().first()
        if not existing_user:
            session.add(User(id=user_id))
        await session.commit()


@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(
        'Правила игры:\n\nЯ загадываю число от 1 до 100, '
        f'а вам нужно его угадать\nУ вас есть {ATTEMPTS} '
        'попыток\n\nДоступные команды:\n/help - правила '
        'игры и список команд\n/cancel - выйти из игры\n'
        '/stat - посмотреть статистику\n\nДавай сыграем?'
    )


@dp.message(Command(commands='stat'))
async def process_stat_command(message: Message):
    user_id = message.from_user.id
    async with get_session() as session:
        res = await session.execute(select(User).filter_by(id=user_id))
        existing_user = res.scalars().first()
    await message.answer(
        'Всего игр сыграно: '
        f'{existing_user.total_games}\n'
        f'Игр выиграно: {existing_user.wins}'
    )


@dp.message(Command(commands='cancel'))
async def process_cancel_command(message: Message):
    user_id = message.from_user.id
    async with get_session() as session:
        res = await session.execute(select(User).filter_by(id=user_id))
        existing_user = res.scalars().first()
        if existing_user.in_game:
            existing_user.in_game = False
            await message.answer(
                'Вы вышли из игры. Если захотите сыграть снова - напишите об этом'
            )
        else:
            await message.answer('А мы итак с вами не играем. Может, сыграем разок?')
        await session.commit()


@dp.message(
    F.text.lower().in_(['да', 'давай', 'сыграем', 'игра', 'играть', 'хочу играть'])
)
async def process_positive_answer(message: Message):
    user_id = message.from_user.id
    async with get_session() as session:
        res = await session.execute(select(User).filter_by(id=user_id))
        existing_user = res.scalars().first()
        if not existing_user.in_game:
            existing_user.in_game = True
            existing_user.secret_num = get_random_number()
            existing_user.attempts = ATTEMPTS
            await message.answer(
                'Ура!\n\nЯ загадал число от 1 до 100, попробуй угадать!'
            )
        else:
            await message.answer(
                'Пока мы играем в игру я могу '
                'реагировать только на числа от 1 до 100 '
                'и команды /cancel и /stat'
            )
        await session.commit()


@dp.message(F.text.lower().in_(['нет', 'не', 'не хочу', 'не буду']))
async def process_negative_answer(message: Message):
    user_id = message.from_user.id
    async with get_session() as session:
        res = await session.execute(select(User).filter_by(id=user_id))
        existing_user = res.scalars().first()
        if not existing_user.in_game:
            await message.answer(
                'Жаль :(\n\nЕсли захотите поиграть - просто напишите об этом'
            )
        else:
            await message.answer(
                'Мы же сейчас с вами играем. Присылайте, пожалуйста, числа от 1 до 100'
            )


@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_numbers_answer(message: Message):
    user_id = message.from_user.id
    async with get_session() as session:
        res = await session.execute(select(User).filter_by(id=user_id))
        existing_user = res.scalars().first()
        if existing_user.in_game:
            if int(message.text) == existing_user.secret_num:
                existing_user.in_game = False
                existing_user.total_games += 1
                existing_user.wins += 1
                await message.answer('Ура!!! Вы угадали число!\n\nМожет, сыграем еще?')
            elif int(message.text) > existing_user.secret_num:
                existing_user.attempts -= 1
                await message.answer('Мое число меньше')
            elif int(message.text) < existing_user.secret_num:
                existing_user.attempts -= 1
                await message.answer('Мое число больше')

            if existing_user.attempts == 0:
                existing_user.in_game = False
                existing_user.total_games += 1
                await message.answer(
                    'К сожалению, у вас больше не осталось '
                    'попыток. Вы проиграли :(\n\nМое число '
                    f'было {existing_user.secret_num}'
                    '\n\nДавайте сыграем еще?'
                )
        else:
            await message.answer('Мы еще не играем. Хотите сыграть?')
        await session.commit()


@dp.message()
async def process_other_answers(message: Message):
    user_id = message.from_user.id
    async with get_session() as session:
        res = await session.execute(select(User).filter_by(id=user_id))
        existing_user = res.scalars().first()
        if existing_user.in_game:
            await message.answer(
                'Мы же сейчас с вами играем. Присылайте, пожалуйста, числа от 1 до 100'
            )
        else:
            await message.answer(
                'Я довольно ограниченный бот, давайте просто сыграем в игру?'
            )


if __name__ == '__main__':
    dp.run_polling(bot)
