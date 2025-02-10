from aiogram import types

def create_main_keyboard():
    """Create main menu keyboard"""
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="✏️ Ввести код")],
            [types.KeyboardButton(text="❔️ Случайный фильм")]
        ],
        resize_keyboard=True
    )

def create_back_keyboard():
    """Create back button keyboard"""
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="↩️ Отмена")]],
        resize_keyboard=True
    )

def create_sub_keyboard():
    """Create subscription keyboard"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[[
            types.InlineKeyboardButton(
                text="✅ Проверить подписку",
                callback_data="checksub"
            )
        ]]
    )

def create_approve_keyboard():
    """Create approval keyboard"""
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data="accept"
                ),
                types.InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="reject"
                )
            ]
        ]
    )

# Initialize keyboards
main_kb = create_main_keyboard()
back = create_back_keyboard()
sub = create_sub_keyboard()
approve = create_approve_keyboard()

__all__ = ['main_kb', 'back', 'sub', 'approve']