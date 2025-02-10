"""
Handlers package for the Telegram Film Bot.
Contains command handlers for both admin and basic user interactions.
"""

from .admin_handler import router as admin_router
from .basic_handler import router as basic_router

__all__ = [
    'admin_router',
    'basic_router'
]

# Handler descriptions
ADMIN_COMMANDS = {
    '/add': 'Добавить новый фильм',
    '/edit': 'Редактировать существующий фильм',
    '/del': 'Удалить фильм',
    '/films': 'Просмотреть список всех фильмов',
    '/help': 'Показать справку по командам'
}

BASIC_COMMANDS = {
    '✏️ Ввести код': 'Найти фильм по коду',
    '❔️ Случайный фильм': 'Получить случайный фильм',
    '↩️ Отмена': 'Вернуться в главное меню'
}
