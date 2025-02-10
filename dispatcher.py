from aiogram import Dispatcher, F
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from handlers import admin_handler, basic_handler
from utils.states import St
from database.db import DB
from utils.keyboard import main_kb, sub
from services.check_sub import check_sub

# Initialize dispatcher and database
dp = Dispatcher()
dp.callback_query.middleware(CallbackAnswerMiddleware())
dp.include_routers(admin_handler.router, basic_handler.router)
db = DB()

@dp.message(St.main)
@dp.message(Command("start"))
async def start(msg: Message, state: FSMContext):
    """Handle /start command and main state"""
    name = msg.from_user.first_name
    userid = msg.from_user.id
    subbed = await check_sub(userid)
    
    if subbed:
        if db.get_user(userid) is None:
            db.add_user(userid)
            print(f'[INF] New user #{userid} has been successfully added to database!')
        
        await msg.answer(
            f'🥳 Добро пожаловать, {name}!\nДля навигации воспользуйтесь кнопками.',
            reply_markup=main_kb
        )
        await state.clear()
    else:
        await msg.answer(
            f'🥳 Добро пожаловать, {name}!\nПожалуйста, подпишитесь на канал\n<a href="https://t.me/TEST1101001011">TEST1</a>, чтобы использовать функции бота.',
            parse_mode='HTML'
        )

@dp.message(F.text == "↩️ Отмена")
async def cancel(msg: Message, state: FSMContext):
    """Handle cancel button press"""
    await start(msg, state)
