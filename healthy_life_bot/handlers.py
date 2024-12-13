import os
import random
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.fsm.context import FSMContext
from states import UserState
from utils import get_greeting, calculate_water_norm
from database import Database
from keyboards import keyboards
from config import WORKOUTS, DAILY_MENU, MOTIVATION_PHRASES

router = Router()
db = Database()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start.

    Начинает взаимодействие с пользователем: если пользователь новый - запускает
    процесс регистрации, если существующий - показывает главное меню.

    Args:
        message: Входящее сообщение от пользователя
        state: Состояние FSM для хранения данных

    Returns:
        None
    """

    user_data = db.get_user_stats(message.from_user.id)

    if user_data:
        await message.answer(
            "С возвращением! Выберите нужную опцию:",
            reply_markup=keyboards['main']
        )
        return

    await message.answer(get_greeting(message.from_user.first_name), reply_markup=ReplyKeyboardRemove())

    await message.answer("Пожалуйста, укажите ваш возраст:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserState.waiting_for_age)


@router.message(UserState.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Обработка ввода возраста пользователя.

    Проверяет корректность введенного возраста и сохраняет его в состоянии.

    Args:
        message: Входящее сообщение с возрастом
        state: Состояние FSM для сохранения данных

    Returns:
        None
    """

    try:
        age = int(message.text)
        if age < 12 or age > 100:
            await message.answer("Пожалуйста, введите корректный возраст (12-100 лет)",
                                 reply_markup=ReplyKeyboardRemove())
            return

        await state.update_data(age=age)
        await message.answer("Теперь укажите ваш рост в сантиметрах:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(UserState.waiting_for_height)

    except ValueError:
        await message.answer("Пожалуйста, введите число", reply_markup=ReplyKeyboardRemove())


@router.message(UserState.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    """Обработка ввода роста пользователя.

    Проверяет корректность введенного роста и сохраняет его в состоянии.

    Args:
        message: Входящее сообщение с ростом
        state: Состояние FSM для сохранения данных

    Returns:
        None
    """

    try:
        height = int(message.text)
        if height < 50 or height > 250:
            await message.answer("Пожалуйста, введите корректный рост (50-250 см)", reply_markup=ReplyKeyboardRemove())
            return

        await state.update_data(height=height)
        await message.answer("Теперь укажите ваш текущий вес в килограммах:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(UserState.waiting_for_weight)

    except ValueError:
        await message.answer("Пожалуйста, введите число", reply_markup=ReplyKeyboardRemove())


@router.message(UserState.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка ввода веса пользователя.

    Проверяет корректность введенного веса, сохраняет все данные в БД
    и завершает регистрацию.

    Args:
        message: Входящее сообщение с весом
        state: Состояние FSM для сохранения данных

    Returns:
        None
    """

    try:
        weight = float(message.text)
        if weight < 30 or weight > 300:
            await message.answer("Пожалуйста, введите корректный вес (30-300 кг)", reply_markup=ReplyKeyboardRemove())
            return

        user_data = await state.get_data()
        height = user_data['height']
        age = user_data['age']

        db.add_user(message.from_user.id, age, height, weight)

        await state.clear()
        await message.answer(
            "Отлично! Ваши данные сохранены. Теперь вы можете использовать все функции бота:",
            reply_markup=keyboards['main']
        )

    except ValueError:
        await message.answer("Пожалуйста, введите число", reply_markup=ReplyKeyboardRemove())


@router.message(F.text == "🏋️ Упражнения")
async def show_exercises(message: Message):
    """Отображение меню выбора уровня сложности упражнений.

    Args:
        message: Входящее сообщение

    Returns:
        None
    """

    await message.answer(
        "Выберите уровень сложности:",
        reply_markup=keyboards['exercise']
    )


@router.callback_query(F.data.startswith("exercise_"))
async def process_exercise_choice(callback: CallbackQuery):
    """Обработка выбора уровня сложности упражнений.

    Args:
        callback: Callback-запрос с выбранным уровнем

    Returns:
        None
    """

    level = callback.data.split('_')[1]
    await callback.message.answer(WORKOUTS[level])
    await callback.answer()


@router.message(F.text == "🥗 Питание")
async def show_diet_menu(message: Message):
    """Отображение меню выбора дня для просмотра плана питания.

    Args:
        message: Входящее сообщение

    Returns:
        None
    """

    await message.answer(
        "Выберите день недели для просмотра плана питания:",
        reply_markup=keyboards['diet']
    )


@router.callback_query(lambda c: c.data.startswith('diet_'))
async def process_diet_day(callback: CallbackQuery):
    """Обработка выбора дня недели для отображения плана питания.

    Args:
        callback: Callback-запрос с выбранным днем недели

    Returns:
        None
    """

    day = callback.data.split('_')[1]
    await callback.message.answer(DAILY_MENU[day])
    await callback.answer()


@router.message(F.text == "💪 Мотивация")
async def show_motivation(message: Message):
    """Показ мотивационной фразы.

    Args:
        message: Входящее сообщение

    Returns:
        None
    """

    phrase = random.choice(MOTIVATION_PHRASES)
    await message.answer(phrase)


@router.message(F.text == "❓ Помощь")
async def show_help(message: Message):
    """Отображение справочной информации о командах бота.

    Args:
        message: Входящее сообщение

    Returns:
        None
    """

    help_text = """
    Как пользоваться ботом:
    
    📊 Мой прогресс - просмотр ваших показателей
    ⚖️ Обновить вес - внести новый вес
    🏋️ Упражнения - программы тренировок
    🥗 Питание - пример меню на день
    💪 Мотивация - мотивирующие фразы
    ❓ Помощь - это сообщение
    """
    await message.answer(help_text)


@router.message(F.text == "📊 Мой прогресс")
async def show_progress(message: Message):
    """Отображение статистики прогресса пользователя.

    Показывает текущие показатели, изменение веса и график прогресса.

    Args:
        message: Входящее сообщение

    Returns:
        None
    """

    stats = db.get_user_stats(message.from_user.id)
    if not stats:
        await message.answer("Сначала необходимо зарегистрироваться. Используйте /start")
        return

    graph_path = db.create_weight_graph(message.from_user.id)

    bmi = stats['current_weight'] / ((stats['height'] / 100) ** 2)
    weight_diff = stats['current_weight'] - stats['initial_weight']

    progress_text = f"""
    Ваша статистика:
    Рост: {stats['height']} см
    Начальный вес: {stats['initial_weight']} кг
    Текущий вес: {stats['current_weight']} кг
    Изменение веса: {weight_diff:+.1f} кг
    ИМТ: {bmi:.1f}
    """
    await message.answer(progress_text)

    if graph_path:
        try:
            await message.answer_photo(photo=FSInputFile(graph_path))
        finally:
            if os.path.exists(graph_path):
                os.remove(graph_path)


@router.message(F.text == "⚖️ Обновить вес")
async def update_weight_cmd(message: Message, state: FSMContext):
    """Начало процесса обновления веса.

    Args:
        message: Входящее сообщение
        state: Состояние FSM для сохранения данных

    Returns:
        None
    """

    await message.answer("Укажите ваш текущий вес в килограммах:")
    await state.set_state(UserState.updating_weight)


@router.message(UserState.updating_weight)
async def process_weight_update(message: Message, state: FSMContext):
    """Обработка обновления веса пользователя.

    Проверяет корректность введенного веса и сохраняет в БД.

    Args:
        message: Входящее сообщение с новым весом
        state: Состояние FSM для сохранения данных

    Returns:
        None
    """

    try:
        weight = float(message.text)
        if weight < 30 or weight > 300:
            await message.answer("Пожалуйста, введите корректный вес (30-300 кг)")
            return

        db.update_weight(message.from_user.id, weight)
        await state.clear()
        await message.answer("Вес успешно обновлен!")

    except ValueError:
        await message.answer("Пожалуйста, введите число")


@router.message(F.text == "💧 Норма воды")
async def show_water_norm(message: Message):
    """Расчет и отображение рекомендуемой нормы воды.

    Args:
        message: Входящее сообщение

    Returns:
        None
    """

    user_stats = db.get_user_stats(message.from_user.id)
    if not user_stats:
        await message.answer("Сначала необходимо зарегистрироваться. Используйте /start")
        return

    weight = float(user_stats['current_weight'])
    height = float(user_stats['height'])
    water_norm = calculate_water_norm(weight, height)

    response_text = f"""
💧 Ваша рекомендуемая норма воды:
{water_norm} литров в день

📊 Расчёт на основе:
• Вес: {weight} кг
• Рост: {height} см

💡 Советы:
• Начинайте день со стакана воды
• Держите бутылку воды всегда под рукой
• Пейте воду за 30 минут до еды
• Распределите приём воды равномерно в течение дня
"""
    await message.answer(response_text)


@router.message(F.text == "⚙️ Сброс")
async def reset_progress(message: Message):
    """Запрос подтверждения сброса прогресса пользователя.

    Args:
        message: Входящее сообщение

    Returns:
        None
    """

    confirmation_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, сбросить", callback_data="confirm_reset"),
                InlineKeyboardButton(text="Отмена", callback_data="cancel_reset")
            ]
        ]
    )

    await message.answer(
        "⚠️ Вы уверены, что хотите сбросить весь прогресс? Это действие нельзя отменить.",
        reply_markup=confirmation_kb
    )


@router.callback_query(F.data == "confirm_reset")
async def process_reset_confirmation(callback: CallbackQuery):
    """Обработка подтверждения сброса данных пользователя.

    Args:
        callback: Callback-запрос с подтверждением

    Returns:
        None

    Raises:
        Exception: При ошибке удаления данных из БД
    """

    try:
        db.delete_user_data(callback.from_user.id)
        await callback.message.edit_text("🔄 Данные успешно сброшены. Используйте /start для новой регистрации")
    except Exception as e:
        print(f"Error during reset: {e}")
        await callback.message.edit_text("❌ Произошла ошибка при сбросе данных")
    finally:
        await callback.answer()


@router.callback_query(F.data == "cancel_reset")
async def process_cansel_reset(message: Message):
    """
    Отмена сброса данных.

    Args:
        message : Входящее сообщение

    Returns:
        None
    """
    await message.answer("Хорошо, тогда выберите команду😀")


@router.message()
async def unknown_command(message: Message):
    """Обработка неизвестных команд.

    Args:
        message: Входящее сообщение

    Returns:
        None
    """

    await message.answer(f"Неизвестная команда.\n\nНажмите кнопку  <❓ Помощь > , чтобы узнать мои команды ")
