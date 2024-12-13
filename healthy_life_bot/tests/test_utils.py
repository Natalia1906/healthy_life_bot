import pytest
from utils import get_greeting, calculate_water_norm


def test_get_greeting_with_name():
    """Тест генерации приветствия с именем пользователя"""
    username = "John"
    greeting = get_greeting(username)
    assert username in greeting
    assert "👋" in greeting
    assert "💪" in greeting
    assert "🍏" in greeting
    assert "🏃️" in greeting
    assert "🌟" in greeting


def test_get_greeting_with_empty_name():
    """Тест генерации приветствия с пустым именем"""
    greeting = get_greeting("")
    assert "Привет, !" in greeting


def test_calculate_water_norm_typical():
    """Тест расчета нормы воды для типичных значений"""
    weight = 70
    height = 170
    expected = round((70 * 0.03 + 170 * 0.01), 1)
    assert calculate_water_norm(weight, height) == expected


def test_calculate_water_norm_zero():
    """Тест расчета нормы воды для нулевых значений"""
    assert calculate_water_norm(0, 0) == 0.0


def test_calculate_water_norm_large_numbers():
    """Тест расчета нормы воды для больших чисел"""
    weight = 150
    height = 200
    expected = round((150 * 0.03 + 200 * 0.01), 1)
    assert calculate_water_norm(weight, height) == expected


@pytest.mark.parametrize("weight,height,expected", [
    (70, 170, 3.8),
    (50, 160, 3.1),
    (100, 190, 4.9),
    (0, 0, 0.0),
])
def test_calculate_water_norm_parametrize(weight, height, expected):
    """Параметризованный тест расчета нормы воды"""
    assert calculate_water_norm(weight, height) == expected


def test_calculate_water_norm_negative():
    """Тест расчета нормы воды для отрицательных значений"""
    # Хотя это нелогичный сценарий, функция математически его обработает
    result = calculate_water_norm(-70, -170)
    assert isinstance(result, float)
    assert result < 0