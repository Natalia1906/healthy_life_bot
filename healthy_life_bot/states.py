from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """Группа состояний пользователя в процессе регистрации и обновления данных.

    Attributes:
        waiting_for_age: Ожидание ввода возраста
        waiting_for_height: Ожидание ввода роста
        waiting_for_weight: Ожидание ввода начального веса
        updating_weight: Ожидание ввода нового значения веса
    """

    waiting_for_age = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    updating_weight = State()
