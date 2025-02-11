import logging, psutil, time, requests, subprocess, git, re, random
from aiogram import Router, F, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, URLInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from utils.keyboard import approve, back, main_kb
from utils.states import St
from services.film_tools import film_scraper, helper
from services.film_tools.film_builder import build_film
from packaging.version import parse as parse_version
from version import __version__
from database.db import DB
from config import GITHUB_TOKEN
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

# Проверяем находится ли юзер запросивший команду в листе админов
# Если что, добавлять админов нужно по userid из телеграмма и через запятую.
try:
    with open('config/admins.txt', 'r') as admin_file:
        admins = admin_file.read().split(',')
        print(f'Admin list: {", ".join(admins)}')
except Exception as e:
    logger.error(f"Error reading admin list: {e}")
    admins = []

# Обработчик для вывода лежащих в бд данных
@router.message(Command("films"))
async def get_films(msg: Message, state: FSMContext):
    if str(msg.from_user.id) in admins:
        try:
            films = db.get_keysfilms()
            if not films:
                await msg.answer("📭 В базе данных пока нет фильмов.")
                return
            answer = ''
            for i in films:
                answer += f'{i[1]}: {i[3]}\n'
            await msg.answer(f'Найдено: {len(films)} значений в базе данных.\n{answer}')
        except Exception as e:
            logger.error(f"Error retrieving films: {e}")
            await msg.answer("❌ Произошла ошибка при получении списка фильмов.")

# Обработчик для добавления фильма или сериала..
@router.message(Command("add"))
async def url_enter(msg: Message, state: FSMContext):
    if str(msg.from_user.id) in admins:
        await msg.answer('👽 Введите ссылку (film.ru): ', reply_markup=back)
        await state.set_state(St.url)

# Обработчик команды /update или же вроде как АвтоОбновление XD. + сделать так чтобы и без команды обновления проверяло при запуске бота.
@router.message(Command("update"))
async def check_for_updates(msg: Message):
    if str(msg.from_user.id) in admins:
        try:
            # Текущая версия
            from version import __version__ as current_version
            
            # Получаем версию из GitHub
            headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
            response = requests.get(
                "https://raw.githubusercontent.com/bad-cyber/CodeToMovieBot/main/version.py",
                headers=headers
            )
            response.raise_for_status()
            
            # Парсим версию
            remote_version = re.search(r'__version__\s*=\s*"([\d.]+)"', response.text).group(1)
            
            if parse_version(remote_version) > parse_version(current_version):
                await msg.answer(f"Найдена новая версия {remote_version}. Обновляем...")
                
                #subprocess.run(["git", "pull"], check=True)
                await msg.answer(f"Внимание. текущая функция находится в доработке,\n поэтому пока она отключена.")
                
                await msg.answer("✅ Обновление завершено. Перезапустите бота.")
            else:
                await msg.answer("У вас актуальная версия.")
                
        except requests.exceptions.RequestException as e:
            await msg.answer(f"❌ Ошибка связи: {str(e)}")
        except Exception as e:
            await msg.answer(f"❌ Критическая ошибка: {str(e)}")

# Обработчик команды /help
@router.message(Command("help"))
async def admin_help(msg: Message, state: FSMContext):
    if str(msg.from_user.id) in admins:
        help_text = (
            "📋 Список команд администратора:\n\n"
            "/add - Добавить фильм\n"
            "/edit - Редактировать существующий фильм\n"
            "/del - Удалить фильм\n"
            "/films - Посмотреть список всех фильмов и кодов к ним\n"
            "/ping - Отображает информацию о состоянии бота\n\n"
            "ℹ️ Управление фильмами:\n"
            "• Добавление: используйте /add и укажите ссылку на film.ru\n"
            "• Редактирование: используйте /edit и укажите код фильма\n"
            "• Удаление: используйте /del и укажите код фильма\n"
            "• Коды фильмов: числа от 100 до 100000"
        )
        await msg.answer(help_text)

# Обработчик команды для удаления фильма или же /del
@router.message(Command("del"))
async def delete_film_cmd(msg: Message, state: FSMContext):
    if str(msg.from_user.id) in admins:
        await msg.answer('🗝 Введите код фильма для удаления:', reply_markup=back)
        await state.set_state(St.delete_code)

# Функция для удаления фильма
@router.message(St.delete_code)
async def delete_film_code(msg: Message, state: FSMContext):
    if str(msg.from_user.id) in admins:
        code = msg.text.strip()
        
        if not code.isdigit() or not (100 <= int(code) <= 100000):
            await msg.answer(
                '❌ Неверный формат кода\n'
                '💡 Код должен быть числом от 100 до 100000',
                reply_markup=back
            )
            return

        code = int(code)
        film = db.get_film(code)
        
        if not film:
            await msg.answer(
                '❌ Фильм не найден\n'
                '💡 Проверьте правильность введенного кода',
                reply_markup=main_kb
            )
            await state.set_state(St.main)
            return

        try:
            # Показываем информацию о фильме и запрашиваем подтверждение
            confirm_text = (
                f"⚠️ Подтвердите удаление фильма:\n\n"
                f"📝 Информация о фильме:\n"
                f"• Название: {film[3]}\n"
                f"• Жанр: {film[6]}\n"
                f"• Год: {film[7]}\n"
                f"• Страна: {film[8]}\n"
                f"🗝 Код: {code}\n\n"
                f"❗️ Это действие нельзя отменить"
            )
            
            # Создаем клавиатуру для подтверждения
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"delete_confirm_{code}"),
                    types.InlineKeyboardButton(text="❌ Отмена", callback_data="delete_cancel")
                ]
            ])
            
            await msg.answer(confirm_text, reply_markup=keyboard)
            await state.set_state(St.delete_confirm)
            
        except Exception as e:
            logger.error(f"Error preparing delete confirmation: {str(e)}")
            await msg.answer(
                '❌ Произошла ошибка при подготовке информации о фильме\n'
                '💡 Пожалуйста, попробуйте позже',
                reply_markup=main_kb
            )
            await state.set_state(St.main)

# Команда для проверки показателей работоспособности бота /ping
@router.message(Command("ping"))
async def ping_server(msg: Message):
    if str(msg.from_user.id) in admins:
        try:
            # Gather server information
            cpu_usage = psutil.cpu_percent()
            ram_usage = psutil.virtual_memory().percent
            ssd_usage = psutil.disk_usage('/').percent
            
            # Measure server ping
            start_time = time.time()
            try:
                response = requests.get('http://yandex.ru')  # Меняйте на тот который хотите проверить
                server_ping = round((time.time() - start_time) * 1000, 2)  # Округляем до 2 знаков
            except requests.RequestException:
                server_ping = "Ошибка при измерении пинга"
            
            # Format the response message
            response = (
                f"Информация о сервере:\n"
                f"Пинг сервера: {server_ping} ms\n"
                f"Нагрузка ЦП: {cpu_usage}%\n"
                f"Нагрузка ОЗУ: {ram_usage}%\n"
                f"Нагрузка SSD: {ssd_usage}%"
            )
            await msg.answer(response)
        except Exception as e:
            logger.error(f"Error retrieving server information: {e}")
            await msg.answer("❌ Произошла ошибка при получении информации о сервере.")

# Функция для кнопки подтверждения удаления
@router.callback_query(F.data.startswith("delete_confirm_"))
async def delete_film_confirm(callback: types.CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) in admins:
        try:
            code = int(callback.data.split('_')[2])
            film = db.get_film(code)
            
            if not film:
                await callback.message.answer(
                    '❌ Ошибка: фильм не найден\n'
                    '💡 Возможно, он уже был удален',
                    reply_markup=main_kb
                )
                await state.set_state(St.main)
                return

            if db.delete_film(code):
                await callback.message.answer(
                    f'✅ Фильм успешно удален!\n'
                    f'• Название: {film[3]}\n'
                    f'• Код: {code}',
                    reply_markup=main_kb
                )
            else:
                raise ValueError("Ошибка при удалении из базы данных")

        except Exception as e:
            logger.error(f"Error deleting film: {str(e)}")
            await callback.message.answer(
                '❌ Произошла ошибка при удалении фильма\n'
                '💡 Пожалуйста, попробуйте позже или обратитесь к администратору',
                reply_markup=main_kb
            )
        finally:
            await state.set_state(St.main)

# Функция для кнопки отмены удаления фильма
@router.callback_query(F.data == "delete_cancel")
async def delete_film_cancel(callback: types.CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) in admins:
        await callback.message.answer('🚫 Удаление отменено', reply_markup=main_kb)
        await state.set_state(St.main)

# Функция добавления фильма в бд
@router.message(St.url)
async def url_add(msg: Message, state: FSMContext):
    url = msg.text.strip()
    
    # Проверяем формат ссылки
    if not url.startswith('https://www.film.ru/movies/'):
        await msg.answer(
            '❌ Неверный формат ссылки.\n'
            '• Ссылка должна начинаться с https://www.film.ru/movies/\n'
            '• Пример: https://www.film.ru/movies/avatar-put-vody', 
            reply_markup=back
        )
        return
    
    await msg.answer('🔍 Получаем информацию о фильме...')
    
    try:
        # Получаем информацию о фильме
        data = await film_scraper.get_filminfo(url)
        
        try:
            # Пробуем загрузить изображение
            film_img = URLInputFile(data['image'])
            
            # Формируем информацию о фильме
            film_info = (
                data["name"],          # название
                data["duration"],      # продолжительность
                data["score"],         # рейтинг
                data["genre"],         # жанр
                data["year"],          # год
                data["country"],       # страна
                data["desc"]           # описание
            )
            
            # Показываем предпросмотр
            preview_text = (
                "📥 Предварительный просмотр фильма:\n\n"
                f"• Название: {data['name']}\n"
                f"• Жанр: {data['genre']}\n"
                f"• Год: {data['year']}\n"
                f"• Страна: {data['country']}\n"
                f"• Продолжительность: {data['duration']}\n"
                f"• Рейтинг: {data['score']}"
            )
            await msg.answer(preview_text)
            
            # Отправляем фото с описанием
            film_msg = await msg.answer_photo(
                film_img, 
                caption=build_film(*film_info), 
                reply_markup=approve
            )
            image_id = film_msg.photo[-1].file_id
            
            # Сохраняем данные в состояние
            await state.update_data(
                film_image_id=image_id,
                film_info=film_info
            )
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            # Если не удалось загрузить изображение, показываем только текст
            await msg.answer(
                f"⚠️ Предпросмотр фильма (без изображения):\n\n" +
                build_film(*film_info) +
                "\n\n❓ Продолжить добавление фильма?",
                reply_markup=approve
            )
            
    except ValueError as e:
        error_msg = str(e)
        if "Не удалось найти" in error_msg:
            await msg.answer(
                f'❌ Ошибка при получении данных:\n{error_msg}\n\n'
                '💡 Убедитесь, что:\n'
                '• Ссылка ведет на существующий фильм\n'
                '• Страница фильма загружается в браузере',
                reply_markup=back
            )
        else:
            await msg.answer(f'❌ {error_msg}', reply_markup=back)
        return
        
    except Exception as e:
        logger.error(f"Unexpected error adding film: {str(e)}")
        await msg.answer(
            '❌ Произошла непредвиденная ошибка.\n\n'
            '💡 Возможные причины:\n'
            '• Сайт film.ru временно недоступен\n'
            '• Ошибка при обработке данных\n'
            '• Проблемы с сетевым подключением\n\n'
            'Пожалуйста, попробуйте позже.',
            reply_markup=back
        )
        return

# Функция если подтверждаем добавление фильма в бд
@router.callback_query(F.data == 'accept')
async def accept_film(callback: types.CallbackQuery, state: FSMContext):
    try:
        # Получаем сохраненные данные из состояния
        data = await state.get_data()
        film_info = data.get('film_info')
        image_id = data.get('film_image_id')

        if not film_info:
            await callback.message.answer(
                '❌ Ошибка: данные о фильме не найдены\n'
                '💡 Попробуйте добавить фильм заново',
                reply_markup=main_kb
            )
            await state.set_state(St.main)
            return

        # Проверяем наличие всех необходимых данных
        if len(film_info) != 7:  # name, duration, score, genre, year, country, desc
            await callback.message.answer(
                '❌ Ошибка: неполные данные о фильме\n'
                '💡 Убедитесь, что на странице фильма указаны все необходимые данные',
                reply_markup=main_kb
            )
            await state.set_state(St.main)
            return

        # Генерируем уникальный код (расширенный диапазон)
        attempts = 0
        max_attempts = 10
        key = random.randint(100, 100000)
        
        while db.get_film(key):
            key = random.randint(100, 100000)
            attempts += 1
            if attempts >= max_attempts:
                await callback.message.answer(
                    '❌ Ошибка: не удалось сгенерировать уникальный код\n'
                    '💡 Пожалуйста, попробуйте позже',
                    reply_markup=main_kb
                )
                await state.set_state(St.main)
                return

        try:
            # Добавляем фильм в базу данных
            if not db.add_film(key, image_id, *film_info):
                raise ValueError("Ошибка при добавлении в базу данных")
            
            # Проверяем, что фильм действительно добавлен
            added_film = db.get_film(key)
            if not added_film:
                raise ValueError("Фильм не был добавлен в базу данных")
            
            # Формируем сообщение об успехе
            success_message = (
                f'✅ Фильм успешно добавлен!\n\n'
                f'📝 Информация:\n'
                f'• Название: {film_info[0]}\n'
                f'• Жанр: {film_info[3]}\n'
                f'• Год: {film_info[4]}\n'
                f'• Страна: {film_info[5]}\n'
                f'🗝 Код фильма: {key}'
            )
            await callback.message.answer(success_message, reply_markup=main_kb)
            
        except Exception as db_error:
            logger.error(f"Database error in accept_film: {str(db_error)}")
            await callback.message.answer(
                '❌ Ошибка при сохранении в базу данных\n'
                '💡 Пожалуйста, попробуйте позже или обратитесь к администратору',
                reply_markup=main_kb
            )

    except Exception as e:
        logger.error(f"Unexpected error in accept_film: {str(e)}")
        await callback.message.answer(
            '❌ Произошла непредвиденная ошибка\n'
            '💡 Пожалуйста, попробуйте позже или обратитесь к администратору',
            reply_markup=main_kb
        )
    finally:
        await state.clear()
        await state.set_state(St.main)

# Функция если отклоняем добавлние фильма в бд
@router.callback_query(F.data == 'reject')
async def reject_film(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('🚫 Отмена...', reply_markup=main_kb)
    await state.clear()
    await state.set_state(St.main)

# Обработчик для приёма кода фильма для последующего редактирования данных о нем
@router.message(Command("edit"))
async def edit_film(msg: Message, state: FSMContext):
    if str(msg.from_user.id) in admins:
        await msg.answer('👀 Введите код фильма для редактирования:', reply_markup=back)
        await state.set_state(St.edit_code)

# Функция для редактирования данных фильма
@router.message(St.edit_code)
async def edit_film_code(msg: Message, state: FSMContext):
    if str(msg.from_user.id) in admins:
        code = msg.text
        if code.isdigit() and 100 <= int(code) <= 100000:
            film = db.get_film(int(code))
            if film:
                await state.update_data(edit_film_code=code)
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="Название", callback_data="edit_name")],
                    [types.InlineKeyboardButton(text="Описание", callback_data="edit_desc")],
                    [types.InlineKeyboardButton(text="Жанр", callback_data="edit_genre")],
                    [types.InlineKeyboardButton(text="Год", callback_data="edit_year")],
                    [types.InlineKeyboardButton(text="Страна", callback_data="edit_country")],
                    [types.InlineKeyboardButton(text="Изображение", callback_data="edit_image")],
                    [types.InlineKeyboardButton(text="Отмена", callback_data="edit_cancel")]
                ])
                await msg.answer(
                    f"🎬 Фильм: {film[3]}\n"
                    f"🗝 Код: {film[1]}\n\n"
                    "Выберите, что хотите отредактировать:",
                    reply_markup=keyboard
                )
                await state.set_state(St.edit_field)
            else:
                await msg.answer('😵‍💫 Фильм с таким кодом не найден.', reply_markup=main_kb)
                await state.set_state(St.main)
        else:
            await msg.answer('🫥 Неверный формат кода.', reply_markup=main_kb)
            await state.set_state(St.main)

# Функция для редактирования данных фильма
@router.callback_query(F.data.startswith("edit_"))
async def edit_field(callback: types.CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) in admins:
        action = callback.data.split("_")[1]
        if action == "cancel":
            await callback.message.edit_text("❌ Редактирование отменено")
            await state.set_state(St.main)
            return

        field_names = {
            "name": "название",
            "desc": "описание",
            "genre": "жанр",
            "year": "год",
            "country": "страну",
            "image": "изображение"
        }
        
        await state.update_data(edit_field=action)
        await callback.message.edit_text(f"✏️ Введите новое {field_names[action]}:")
        await state.set_state(St.edit_value)

# Подтверждение сохранения изменений после редактирования фильма
@router.message(St.edit_value)
async def save_edit(msg: Message, state: FSMContext):
    if str(msg.from_user.id) in admins:
        try:
            data = await state.get_data()
            code = int(data['edit_film_code'])
            field = data['edit_field']
            value = msg.text

            if field == "image":
                try:
                    photo = URLInputFile(value)
                    photo_msg = await msg.answer_photo(photo)
                    value = photo_msg.photo[-1].file_id
                except Exception as e:
                    logger.error(f"Error processing image URL: {str(e)}")
                    await msg.answer("❌ Неверный URL изображения", reply_markup=main_kb)
                    await state.set_state(St.main)
                    return

            if not db.update_film(code, field, value):
                raise ValueError("Ошибка при обновлении базы данных")

            await msg.answer("✅ Изменения сохранены успешно!", reply_markup=main_kb)
            
            film = db.get_film(code)
            if not film:
                raise ValueError("Не удалось получить обновленную информацию о фильме")

            try:
                await msg.answer_photo(
                    film[2],
                    caption=build_film(film[3], film[4], film[5], film[6], film[7], film[8], film[9]),
                    reply_markup=main_kb
                )
            except Exception as e:
                logger.error(f"Error sending updated film photo: {str(e)}")
                await msg.answer(
                    build_film(film[3], film[4], film[5], film[6], film[7], film[8], film[9]) +
                    "\n\n⚠️ Изображение недоступно",
                    reply_markup=main_kb
                )
        except Exception as e:
            logger.error(f"Error saving edit: {str(e)}")
            await msg.answer(f"❌ Ошибка при сохранении изменений: {str(e)}", reply_markup=main_kb)
        finally:
            await state.set_state(St.main)

# Выводная справка о команде для редактирования информации о фильме
@router.callback_query(F.data == 'change')
async def change_film(callback: types.CallbackQuery, state: FSMContext):
    if str(callback.from_user.id) in admins:
        await callback.message.answer('👀 Используйте команду /edit для редактирования фильма', reply_markup=main_kb)
    await state.set_state(St.main)
