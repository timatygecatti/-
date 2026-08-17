import asyncio
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Bot, Message

from helpers import (
    MSK,
    add_event,
    ask_ai,
    format_events,
    get_future_events,
    get_month_events,
    get_next_3_days_events,
    get_tomorrow_events,
    load_all_events,
)

load_dotenv()

bot = Bot(token=os.getenv("VK_TOKEN"))

user_states: dict[int, str | dict] = {}


def build_main_keyboard() -> Keyboard:
    """Создает основную клавиатуру бота."""
    keyboard = Keyboard(one_time=False)
    keyboard.add(Text("3Д"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text("1М"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text("Р/З"), color=KeyboardButtonColor.POSITIVE)
    keyboard.add(Text("Добавить"), color=KeyboardButtonColor.SECONDARY)
    return keyboard


WELCOME_TEXT = (
    "Привет! Я бот-календарь с AI.\n\n"
    "Кнопки:\n"
    "  3Д — расписание на 3 дня\n"
    "  1М — расписание на месяц\n"
    "  Р/З — расписание на завтра\n"
    "  Добавить — добавить событие\n\n"
    "Или просто напишите сообщение — и AI ответит."
)


@bot.on.message(text=["начать", "старт", "/start", "привет"])
async def start_handler(message: Message) -> None:
    await message.answer(WELCOME_TEXT, keyboard=build_main_keyboard())


@bot.on.message(text="3Д")
async def handler_3_days(message: Message) -> None:
    events = get_next_3_days_events(message.from_id)
    text = format_events(events, "Расписание на 3 дня:")
    await message.answer(text, keyboard=build_main_keyboard())


@bot.on.message(text="1М")
async def handler_1_month(message: Message) -> None:
    events = get_month_events(message.from_id)
    text = format_events(events, "Расписание на месяц:")
    await message.answer(text, keyboard=build_main_keyboard())


@bot.on.message(text="Р/З")
async def handler_tomorrow(message: Message) -> None:
    events = get_tomorrow_events(message.from_id)
    text = format_events(events, "Расписание на завтра:")
    await message.answer(text, keyboard=build_main_keyboard())


@bot.on.message(text="Добавить")
async def handler_add_start(message: Message) -> None:
    user_states[message.from_id] = "awaiting_title"
    await message.answer(
        "Введите название события:",
        keyboard=build_main_keyboard(),
    )


@bot.on.message(text="Мои события")
async def handler_my_events(message: Message) -> None:
    events = get_future_events(message.from_id)
    text = format_events(events, "Все будущие события:")
    await message.answer(text, keyboard=build_main_keyboard())


@bot.on.message(func=lambda m: m.from_id in user_states)
async def state_handler(message: Message) -> None:
    state = user_states.get(message.from_id)
    kb = build_main_keyboard()

    if state == "awaiting_title":
        user_states[message.from_id] = {"title": message.text}
        await message.answer("Введите дату (ДД.ММ.ГГГГ):", keyboard=kb)

    elif isinstance(state, dict) and "title" in state and "date" not in state:
        try:
            datetime.strptime(message.text, "%d.%m.%Y")
        except ValueError:
            await message.answer(
                "Неверный формат. Введите дату ДД.ММ.ГГГГ:", keyboard=kb
            )
            return
        user_states[message.from_id]["date"] = message.text
        await message.answer("Введите время (ЧЧ:ММ):", keyboard=kb)

    elif (
        isinstance(state, dict)
        and "title" in state
        and "date" in state
        and "time" not in state
    ):
        try:
            datetime.strptime(message.text, "%H:%M")
        except ValueError:
            await message.answer(
                "Неверный формат. Введите время ЧЧ:ММ:", keyboard=kb
            )
            return

        user_states[message.from_id]["time"] = message.text
        state = user_states[message.from_id]
        iso_date = datetime.strptime(state["date"], "%d.%m.%Y").strftime("%Y-%m-%d")
        add_event(message.from_id, state["title"], iso_date, state["time"])
        await message.answer(
            f"Событие добавлено:\n"
            f"  {state['title']}\n"
            f"  {state['date']} {state['time']}\n"
            f"Напоминание за 3 часа.",
            keyboard=kb,
        )
        del user_states[message.from_id]


@bot.on.message(func=lambda m: "|" in m.text)
async def handler_add_event_fast(message: Message) -> None:
    parts = [part.strip() for part in message.text.split("|")]
    if len(parts) != 3:
        await message.answer("Формат: Название | ДД.ММ.ГГГГ | ЧЧ:ММ")
        return

    title, date_str, time_str = parts
    try:
        datetime.strptime(date_str, "%d.%m.%Y")
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        await message.answer(
            "Ошибка формата: Название | ДД.ММ.ГГГГ | ЧЧ:ММ",
            keyboard=build_main_keyboard(),
        )
        return

    iso_date = datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
    add_event(message.from_id, title, iso_date, time_str)
    await message.answer(
        f"Событие добавлено:\n  {title}\n  {date_str} {time_str}",
        keyboard=build_main_keyboard(),
    )


SCHEDULE_KEYWORDS = ["завтра", "расписан", "план", "событи", "дела на"]


@bot.on.message(func=lambda m: any(w in m.text.lower() for w in SCHEDULE_KEYWORDS))
async def schedule_from_text(message: Message) -> None:
    text = message.text.lower()
    uid = message.from_id

    if "завтра" in text:
        events = get_tomorrow_events(uid)
        title = "Расписание на завтра:"
    elif "3" in text and ("дн" in text or "три" in text or "3д" in text):
        events = get_next_3_days_events(uid)
        title = "Расписание на 3 дня:"
    elif "месяц" in text:
        events = get_month_events(uid)
        title = "Расписание на месяц:"
    else:
        events = get_future_events(uid)
        title = "Будущие события:"

    await message.answer(format_events(events, title), keyboard=build_main_keyboard())


@bot.on.message()
async def ai_handler(message: Message) -> None:
    response = await ask_ai(message.text)
    await message.answer(response, keyboard=build_main_keyboard())


async def check_reminders() -> None:
    """Проверяет и отправляет напоминания о событиях."""
    sent: set[str] = set()
    while True:
        try:
            now = datetime.now(MSK)
            data = load_all_events()
            for uid, events in data.items():
                for event in events:
                    event_dt = datetime.strptime(
                        f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M"
                    ).replace(tzinfo=MSK)
                    reminder_time = event_dt - timedelta(
                        hours=event.get("reminder_hours", 3)
                    )
                    diff = (now - reminder_time).total_seconds()
                    key = f"{uid}_{event['date']}_{event['time']}_{event['title']}"

                    if -35 <= diff <= 35 and key not in sent:
                        await bot.api.messages.send(
                            peer_id=int(uid),
                            message=(
                                f"Напоминание!\n"
                                f"  {event['title']}\n"
                                f"  {event['date']} {event['time']}"
                            ),
                            random_id=0,
                        )
                        sent.add(key)
        except Exception as e:
            print(f"Reminder error: {e}")
        await asyncio.sleep(15)


async def main() -> None:
    asyncio.create_task(check_reminders())
    await bot.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
