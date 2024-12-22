from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_route_kb() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для добавления точки маршрута и подтверждения маршрута.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить точку", callback_data="route_add")],
            [InlineKeyboardButton(text="Подтвердить маршрут", callback_data="route_ok")]
        ]
    )

def get_days_kb() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для выбора периода прогноза погоды.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1 день", callback_data="days_1")],
            [InlineKeyboardButton(text="3 дня", callback_data="days_3")],
            [InlineKeyboardButton(text="5 дней", callback_data="days_5")]
        ]
    )
