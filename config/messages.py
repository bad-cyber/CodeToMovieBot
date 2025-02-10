"""
Message templates for the Telegram Film Bot.
Contains all text messages used in the bot.
"""

# Welcome messages
WELCOME_MESSAGE = """
🥳 Добро пожаловать, {name}!
Для навигации воспользуйтесь кнопками.
"""

SUBSCRIBE_MESSAGE = """
🥳 Добро пожаловать, {name}!
Пожалуйста, подпишитесь на канал
<a href="https://t.me/TEST1101001011">TEST1</a>, чтобы использовать функции бота.
"""

# Error messages
INVALID_CODE = "🫥 Неверный формат кода. Введите код ещё раз."
FILM_NOT_FOUND = "😵‍💫 Не удалось найти фильм с таким кодом."
DATABASE_ERROR = "😔 Произошла ошибка при работе с базой данных. Попробуйте позже."
INVALID_URL = """
❌ Неверный формат ссылки.
• Ссылка должна начинаться с https://www.film.ru/movies/
• Пример: https://www.film.ru/movies/avatar-put-vody
"""

# Success messages
FILM_ADDED = "✅ Фильм успешно добавлен!"
FILM_DELETED = "✅ Фильм успешно удален!"
FILM_UPDATED = "✅ Изменения сохранены успешно!"

# Search messages
SEARCHING = "🔍 Поиск фильма по коду {code}..."
RANDOM_SEARCH = "🔍 Идёт поиск случайного фильма..."
NO_FILMS = "😔 К сожалению, в базе данных пока нет фильмов."

# Admin messages
ADMIN_HELP = """
📋 Список команд администратора:

/add - Добавить фильм
/edit - Редактировать существующий фильм
/del - Удалить фильм
/films - Посмотреть список всех фильмов и кодов к ним

ℹ️ Управление фильмами:
• Добавление: используйте /add и укажите ссылку на film.ru
• Редактирование: используйте /edit и укажите код фильма
• Удаление: используйте /del и укажите код фильма
• Коды фильмов: числа от {min_code} до {max_code}
"""

# Subscription messages
NOT_SUBSCRIBED = """
😶‍🌫️ Эта функция доступна только подписчикам.

Пожалуйста, подпишитесь на канал
<a href="https://t.me/TEST1101001011">TEST1</a>, чтобы использовать бота.
"""

# Preview messages
PREVIEW_MESSAGE = """
📥 Предварительный просмотр фильма:

• Название: {name}
• Жанр: {genre}
• Год: {year}
• Страна: {country}
• Продолжительность: {duration}
• Рейтинг: {score}
"""

# Delete confirmation
DELETE_CONFIRM = """
⚠️ Подтвердите удаление фильма:

📝 Информация о фильме:
• Название: {name}
• Жанр: {genre}
• Год: {year}
• Страна: {country}
🗝 Код: {code}

❗️ Это действие нельзя отменить
"""
