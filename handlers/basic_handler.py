import logging, asyncio
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.fsm.context import FSMContext
from utils.states import St
from utils.keyboard import back, main_kb, sub
from database.db import DB
from services.film_tools.film_builder import build_film
from services.check_sub import check_sub
from bot import bot
from config.messages import *

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = Router()
router.callback_query.middleware(CallbackAnswerMiddleware())
db = DB()

not_subbed = '''😶‍🌫️ Эта функция доступна только после выполнения определённых действий. Пожалуйста, подпишитесь на канал<a href="https://t.me/TEST1101001011">TEST1</a>, чтобы использовать бота.'''

# Первая кнопка из defaultUI для обычных пользователей 
@router.message(F.text == "Ввести код ✏️")
async def code_enter(msg: Message, state: FSMContext):
    try:
        subbed = await check_sub(msg.from_user.id)
        if subbed:
            await msg.answer('Введите код фильма. 👀', reply_markup=back)
            await state.set_state(St.code)
        else:
            await msg.answer(not_subbed, parse_mode='HTML', reply_markup=sub)
    except Exception as e:
        logger.error(f"Error in code_enter: {e}")
        await msg.answer('Произошла ошибка. Попробуйте позже. 😔', reply_markup=main_kb)

# Обработчик по поиску ресурса по коду.
@router.message(St.code)
async def get_film(msg: Message, state: FSMContext):
    try:
        subbed = await check_sub(msg.from_user.id)
        if not subbed:
            await msg.answer(not_subbed, parse_mode='HTML', reply_markup=sub)
            return

        code = msg.text
        await msg.answer(f'Поиск фильма по коду {code} 🔍')
        await asyncio.sleep(1)
        
        if not code.isdigit() or not (100 <= int(code) <= 100000):
            await msg.answer('Неверный формат кода. Введите код ещё раз. 🫥', reply_markup=back)
            return
            
        try:
            code = int(code)
            film = db.get_film(code)
            
            if not film:
                await asyncio.sleep(1)
                await msg.answer(f'Упс.. Не удалось найти фильм с кодом "{code}". 😵‍💫', reply_markup=back)
                return
                
            await asyncio.sleep(1)
            try:
                await msg.answer_photo(
                    film[2],
                    caption=(f'🗝 Код: {code}\n') + 
                    build_film(film[3], film[4], film[5], film[6], 
                    film[7], film[8], film[9]),
                    reply_markup=main_kb
                )
            except Exception as e:
                logger.error(f"Error sending film photo: {e}")
                await msg.answer(
                    f'🗝 Код: {code}\n' +
                    build_film(film[3], film[4], film[5], film[6],
                    film[7], film[8], film[9]) +
                    '\n\nИзображение недоступно ⚠️',
                    reply_markup=main_kb
                )
            await state.clear()
            
        except Exception as e:
            logger.error(f"Error getting film: {e}")
            await msg.answer('Произошла ошибка при получении фильма. Попробуйте позже. 😔', reply_markup=main_kb)
            await state.clear()
    except Exception as e:
        logger.error(f"Error in get_film: {e}")
        await msg.answer('Произошла ошибка. Попробуйте позже. 😔', reply_markup=main_kb)
        await state.clear()


@router.message(F.text == "Случайный фильм 🎲")
async def random_film(msg: Message, state: FSMContext):
    try:
        subbed = await check_sub(msg.from_user.id)
        if not subbed:
            await msg.answer(not_subbed, parse_mode='HTML', reply_markup=sub)
            return

        await msg.answer('Идёт поиск случайного фильма 🔍')
        await asyncio.sleep(3)
        
        try:
            randfilm = db.get_randfilm()
            if not randfilm:
                await msg.answer('К сожалению, в базе данных пока нет фильмов.😔', reply_markup=main_kb)
                return
            
            try:
                await msg.answer_photo(
                    randfilm[2], 
                    caption=(f'🗝 Код: {randfilm[1]}\n') + 
                    build_film(randfilm[3], randfilm[4], randfilm[5], randfilm[6], 
                    randfilm[7], randfilm[8], randfilm[9]), 
                    reply_markup=main_kb
                )
            except Exception as e:
                logger.error(f"Error sending random film photo: {e}")
                await msg.answer(
                    f'🗝 Код: {randfilm[1]}\n' +
                    build_film(randfilm[3], randfilm[4], randfilm[5], randfilm[6],
                    randfilm[7], randfilm[8], randfilm[9]) +
                    '\n\nИзображение недоступно ⚠️', 
                    reply_markup=main_kb
                )
        except Exception as e:
            logger.error(f"Error getting random film: {e}")
            await msg.answer('Произошла ошибка при получении фильма. Попробуйте позже.😔', reply_markup=main_kb)
    except Exception as e:
        logger.error(f"Error in random_film: {e}")
        await msg.answer('Произошла ошибка. Попробуйте позже.😔', reply_markup=main_kb)


@router.callback_query(F.data == "checksub")
async def check(callback):
    try:
        subbed = await check_sub(callback.from_user.id)
        if subbed:
            await callback.answer('❤️')
            await bot.send_message(callback.from_user.id, 'Поздравляем! Теперь вам доступны все функции!🎉', reply_markup=main_kb)
        else:
            await bot.send_message(callback.from_user.id, 'Вы не являетесь участником канала.😭')
    except Exception as e:
        logger.error(f"Error in check subscription: {e}")
        await bot.send_message(callback.from_user.id, 'Произошла ошибка при проверке подписки. Попробуйте позже.😔')
