from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[ 
        [ 
            KeyboardButton(text="📊 Мой прогресс"), 
            KeyboardButton(text="⚖️ Обновить вес") 
        ], 
        [ 
            KeyboardButton(text="🏋️ Упражнения"), 
            KeyboardButton(text="🥗 Питание") 
        ], 
        [ 
            KeyboardButton(text="💧 Норма воды"),
            KeyboardButton(text="💪 Мотивация")
        ],
        [
            KeyboardButton(text="❓ Помощь"), 
            KeyboardButton(text="⚙️ Сброс"),
        ] 
    ], 
    resize_keyboard=True 
)

exercise_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Легкий", callback_data="exercise_easy"),
            InlineKeyboardButton(text="Средний", callback_data="exercise_medium"),
            InlineKeyboardButton(text="Сложный", callback_data="exercise_hard")
        ]
    ]
)

diet_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Понедельник", callback_data="diet_monday"),
            InlineKeyboardButton(text="Вторник", callback_data="diet_tuesday")
        ],
        [
            InlineKeyboardButton(text="Среда", callback_data="diet_wednesday"),
            InlineKeyboardButton(text="Четверг", callback_data="diet_thursday")
        ],
        [
            InlineKeyboardButton(text="Пятница", callback_data="diet_friday"),
            InlineKeyboardButton(text="Суббота", callback_data="diet_saturday")
        ],
        [
            InlineKeyboardButton(text="Воскресенье", callback_data="diet_sunday")
        ]
    ]
)

keyboards = {
    'main': main_kb,
    'exercise': exercise_kb,
    'diet': diet_kb
}
