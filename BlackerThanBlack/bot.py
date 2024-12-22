from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN
from keyboards import get_days_kb, get_route_kb
from weather import get_weather

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class RouteState(StatesGroup):
    start_point = State()
    end_point = State()
    add_point = State()


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет! Я бот прогноза погоды по маршруту.\n"
        "Используй /weather чтобы узнать погоду"
    )


@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "Команды:\n"
        "/start - Запустить бота\n"
        "/help - Показать помощь\n"
        "/weather - Получить прогноз погоды"
    )


@dp.message(Command("weather"))
async def weather_cmd(message: types.Message, state: FSMContext):
    await state.set_state(RouteState.start_point)
    await message.answer("Введите начальную точку маршрута:")


@dp.message(RouteState.start_point)
async def process_start(message: types.Message, state: FSMContext):
    await state.update_data(route=[message.text])
    await state.set_state(RouteState.end_point)
    await message.answer("Введите конечную точку маршрута:")


@dp.message(RouteState.end_point)
async def process_end(message: types.Message, state: FSMContext):
    data = await state.get_data()
    route = data["route"]
    route.append(message.text)

    points = "\n→ ".join(route)
    await state.update_data(route=route)

    await message.answer(
        f"Ваш маршрут:\n→ {points}\n\nЧто дальше?",
        reply_markup=get_route_kb()
    )


@dp.callback_query(lambda c: c.data == "route_add")
async def add_point(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(RouteState.add_point)
    await callback.message.answer("Введите промежуточную точку:")
    await callback.answer()


@dp.message(RouteState.add_point)
async def process_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    route = data["route"]
    route.append(message.text)
    points = "\n→ ".join(route)

    await state.update_data(route=route)
    await message.answer(
        f"Обновленный маршрут:\n→ {points}\n\nЧто дальше?",
        reply_markup=get_route_kb()
    )


@dp.callback_query(lambda c: c.data == "route_ok")
async def confirm_route(callback: types.CallbackQuery):
    await callback.message.answer(
        "Выберите период прогноза:",
        reply_markup=get_days_kb()
    )
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("days_"))
async def process_days(callback: types.CallbackQuery, state: FSMContext):
    days = int(callback.data.split("_")[1])
    data = await state.get_data()

    await callback.message.answer("Получаю прогноз погоды...")

    for city in data["route"]:
        weather = await get_weather(city, days)
        if not weather:
            await callback.message.answer(f"Не удалось найти город {city}")
            continue

        text = f"Погода в {weather['city']}:\n\n"
        for forecast in weather['forecasts']:
            text += (
                f"📅 {forecast['date']}:\n"
                f"🌡️ Температура: {forecast['temp']}°C\n"
                f"💧 Осадки: {forecast['rain']}мм\n"
                f"💨 Ветер: {forecast['wind']} м/с\n\n"
            )
        await callback.message.answer(text)

    await state.clear()
    await callback.answer()