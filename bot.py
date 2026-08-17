import asyncio
from datetime import datetime, timedelta

from dotenv import load_dotenv
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text

from helpers import (
    add_event,
    ask_ai,
    format_events,
    get_next_3_days_events,
    get_month_events,
    get_tomorrow_events,
    get_future_events,
    MSK,
)

load_dotenv()

bot = Bot(token=__import__("os").getenv("VK_TOKEN"))

user_states = {}


def main_keyboard() -> Keyboard:
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
async def start_handler(message: Message):
    print(f"USER ID: {message.from_id}")
    await message.answer(WELCOME_TEXT, keyboard=main_keyboard())


@bot.on.message(text="3Д")
async def handler_3d(message: Message):
    events = get_next_3_days_events(message.from_id)
    text = format_events(events, "Расписание на 3 дня:")
    await message.answer(text, keyboard=main_keyboard())


@bot.on.message(text="1М")
async def handler_1m(message: Message):
    events = get_month_events(message.from_id)
    text = format_events(events, "Расписание на месяц:")
    await message.answer(text, keyboard=main_keyboard())


@bot.on.message(text="Р/З")
async def handler_tomorrow(message: Message):
    events = get_tomorrow_events(message.from_id)
    text = format_events(events, "Расписание на завтра:")
    await message.answer(text, keyboard=main_keyboard())


@bot.on.message(text="Добавить")
async def handler_add_start(message: Message):
    user_states[message.from_id] = "awaiting_title"
    await message.answer(
        "Введите название события:",
        keyboard=main_keyboard(),
    )


@bot.on.message(text="Мои события")
async def handler_my_events(message: Message):
    events = get_future_events(message.from_id)
    text = format_events(events, "Все будущие события:")
    await message.answer(text, keyboard=main_keyboard())


@bot.on.message(func=lambda m: m.from_id in user_states)
async def state_handler(message: Message):
    state = user_states.get(message.from_id)

    if state == "awaiting_title":
        user_states[message.from_id] = {"title": message.text}
        await message.answer("Введите дату (ДД.ММ.ГГГГ):", keyboard=main_keyboard())

    elif isinstance(state, dict) and "title" in state and "date" not in state:
        try:
            datetime.strptime(message.text, "%d.%m.%Y")
            user_states[message.from_id]["date"] = message.text
            await message.answer("Введите время (ЧЧ:ММ):", keyboard=main_keyboard())
        except ValueError:
            await message.answer("Неверный формат. Введите дату ДД.ММ.ГГГГ:", keyboard=main_keyboard())

    elif isinstance(state, dict) and "title" in state and "date" in state and "time" not in state:
        try:
            datetime.strptime(message.text, "%H:%M")
            user_states[message.from_id]["time"] = message.text
            s = user_states[message.from_id]
            iso_date = datetime.strptime(s["date"], "%d.%m.%Y").strftime("%Y-%m-%d")
            add_event(message.from_id, s["title"], iso_date, s["time"])
            await message.answer(
                f"Событие добавлено:\n  {s['title']}\n  {s['date']} {s['time']}\nНапоминание за 3 часа.",
                keyboard=main_keyboard(),
            )
            del user_states[message.from_id]
        except ValueError:
            await message.answer("Неверный формат. Введите время ЧЧ:ММ:", keyboard=main_keyboard())


@bot.on.message(func=lambda m: "|" in m.text)
async def handler_add_event_fast(message: Message):
    try:
        parts = [p.strip() for p in message.text.split("|")]
        if len(parts) != 3:
            await message.answer("Формат: Название | ДД.ММ.ГГГГ | ЧЧ:ММ")
            return
        title = parts[0]
        datetime.strptime(parts[1], "%d.%m.%Y")
        datetime.strptime(parts[2], "%H:%M")
        iso_date = datetime.strptime(parts[1], "%d.%m.%Y").strftime("%Y-%m-%d")
        add_event(message.from_id, title, iso_date, parts[2])
        await message.answer(
            f"Событие добавлено:\n  {title}\n  {parts[1]} {parts[2]}",
            keyboard=main_keyboard(),
        )
    except ValueError:
        await message.answer("Ошибка формата: Название | ДД.ММ.ГГГГ | ЧЧ:ММ", keyboard=main_keyboard())


@bot.on.message(func=lambda m: any(w in m.text.lower() for w in ["завтра", "расписан", "план", "событи", "дела на"]))
async def schedule_from_text(message: Message):
    text = message.text.lower()
    if "завтра" in text:
        events = get_tomorrow_events(message.from_id)
        answer = format_events(events, "Расписание на завтра:")
    elif "3" in text and ("дн" in text or "три" in text or "3д" in text):
        events = get_next_3_days_events(message.from_id)
        answer = format_events(events, "Расписание на 3 дня:")
    elif "месяц" in text:
        events = get_month_events(message.from_id)
        answer = format_events(events, "Расписание на месяц:")
    else:
        events = get_future_events(message.from_id)
        answer = format_events(events, "Будущие события:")
    await message.answer(answer, keyboard=main_keyboard())


@bot.on.message()
async def ai_handler(message: Message):
    response = await ask_ai(message.text)
    await message.answer(response, keyboard=main_keyboard())


async def check_reminders():
    sent = set()
    while True:
        try:
            now = datetime.now(MSK)
            data = __import__("helpers").load_all_events()
            for uid, events in data.items():
                for event in events:
                    event_dt = datetime.strptime(
                        f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M"
                    ).replace(tzinfo=MSK)
                    reminder_time = event_dt - timedelta(hours=event.get("reminder_hours", 3))
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


async def main():
    asyncio.create_task(check_reminders())
    await bot.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
