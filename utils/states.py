from aiogram.fsm.state import StatesGroup, State

class St(StatesGroup):
    """
    States for the Film Bot FSM (Finite State Machine).
    Controls the flow of user interactions.
    """
    main = State()        # Главное меню
    code = State()        # Ввод кода фильма
    add = State()         # Добавление фильма
    url = State()         # Ввод URL фильма
    edit_code = State()   # Ввод кода для редактирования
    edit_field = State()  # Выбор поля для редактирования
    edit_value = State()  # Ввод нового значения
    delete_code = State() # Ввод кода для удаления
    delete_confirm = State() # Подтверждение удаления