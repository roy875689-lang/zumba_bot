import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

TOKEN = "8932412157:AAGjF_MPqvcqIV9HwsEytEHghqQDWGNLpW8"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# Ліміти
LIMIT_ZUMBA = 20
LIMIT_ZUMBA_RES = 10
LIMIT_YOGA = 20
LIMIT_YOGA_RES = 10

# Списки
zumba = []
zumba_res = []
yoga = []
yoga_res = []

def main_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Запис Зумба", callback_data="zumba"))
    kb.add(InlineKeyboardButton("Резерв Зумба", callback_data="zumba_res"))
    kb.add(InlineKeyboardButton("Запис Йога", callback_data="yoga"))
    kb.add(InlineKeyboardButton("Резерв Йога", callback_data="yoga_res"))
    kb.add(InlineKeyboardButton("❌ Видалити себе", callback_data="leave"))
    return kb

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Виберіть дію:", reply_markup=main_keyboard())

async def handle_signup(user, main_list, reserve_list, limit_main, limit_reserve, activity_name):
    if user in main_list:
        return f"Ви вже у основному списку ({activity_name})."
    if user in reserve_list:
        return f"Ви вже у резерві ({activity_name})."

    if len(main_list) < limit_main:
        main_list.append(user)
        return f"Вас додано у основний список ({activity_name})."
    elif len(reserve_list) < limit_reserve:
        reserve_list.append(user)
        return f"Основний список заповнений. Вас додано у резерв ({activity_name})."
    else:
        return f"Немає місць у основному та резервному списку ({activity_name})."

async def move_from_reserve(main_list, reserve_list):
    if reserve_list:
        user = reserve_list.pop(0)
        main_list.append(user)
        return user
    return None

async def remove_user(user):
    moved = None

    if user in zumba:
        zumba.remove(user)
        moved = await move_from_reserve(zumba, zumba_res)
        return "Зумба", moved

    if user in zumba_res:
        zumba_res.remove(user)
        return "Резерв Зумба", None

    if user in yoga:
        yoga.remove(user)
        moved = await move_from_reserve(yoga, yoga_res)
        return "Йога", moved

    if user in yoga_res:
        yoga_res.remove(user)
        return "Резерв Йога", None

    return None, None

@dp.callback_query_handler()
async def callbacks(call: types.CallbackQuery):
    user = call.from_user.full_name
    if call.data == "zumba":
        msg = await handle_signup(user, zumba, zumba_res, LIMIT_ZUMBA, LIMIT_ZUMBA_RES, "Зумба")
    elif call.data == "zumba_res":
        msg = await handle_signup(user, zumba_res, zumba, LIMIT_ZUMBA_RES, LIMIT_ZUMBA, "Резерв Зумба")
    elif call.data == "yoga":
        msg = await handle_signup(user, yoga, yoga_res, LIMIT_YOGA, LIMIT_YOGA_RES, "Йога")
    elif call.data == "yoga_res":
        msg = await handle_signup(user, yoga_res, yoga, LIMIT_YOGA_RES, LIMIT_YOGA, "Резерв Йога")
    elif call.data == "leave":
        activity, moved = await remove_user(user)
        if activity is None:
            msg = "Вас немає у жодному списку."
        else:
            msg = f"Вас видалено зі списку ({activity})."
            if moved:
                msg += f"\nКористувача {moved} перенесено з резерву в основний."
                await call.answer(msg, show_alert=True)
            return
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

