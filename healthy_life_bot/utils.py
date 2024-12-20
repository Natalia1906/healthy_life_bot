def get_greeting(username: str) -> str:
    """
        Генерирует персонализированное приветственное сообщение.

        Args:
            username: Имя пользователя для персонализации приветствия

        Returns:
            str: Форматированное приветственное сообщение
        """

    return (
        f'Привет, {username}! 👋 Я — твой помощник на пути к здоровому образу жизни! 💪\n\n'
        "Здесь ты найдешь советы и рекомендации по правильному питанию 🍏, "
        "физической активности 🏃️, и поддержанию здорового образа жизни 🌟.\n\n"
        "Для начала, мне нужна некоторая информация о тебе:"
    )


def calculate_water_norm(weight: float, height: float) -> float:
    """Рассчитывает рекомендуемую дневную норму потребления воды.

    Формула расчета: (вес * 0.03 + рост * 0.01) литров

    Args:
        weight: Вес пользователя в килограммах
        height: Рост пользователя в сантиметрах

    Returns:
        float: Рекомендуемое количество воды в литрах, округленное до 1 знака
    """

    return round((weight * 0.03 + height * 0.01), 1)
