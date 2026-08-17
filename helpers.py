import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

EVENTS_FILE = "events.json"
MSK = ZoneInfo("Europe/Moscow")


def load_all_events() -> dict:
    """Загружает все события из JSON-файла."""
    if not os.path.exists(EVENTS_FILE):
        return {}
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_all_events(data: dict) -> None:
    """Сохраняет все события в JSON-файл."""
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def add_event(
    user_id: int,
    title: str,
    date: str,
    time: str,
    reminder_hours: int = 3,
) -> None:
    """Добавляет событие для пользователя."""
    data = load_all_events()
    uid = str(user_id)
    if uid not in data:
        data[uid] = []
    data[uid].append({
        "title": title,
        "date": date,
        "time": time,
        "reminder_hours": reminder_hours,
    })
    save_all_events(data)


def get_user_events(user_id: int) -> list[dict]:
    """Возвращает все события пользователя."""
    data = load_all_events()
    return data.get(str(user_id), [])


def get_future_events(user_id: int) -> list[dict]:
    """Возвращает будущие события пользователя."""
    now = datetime.now(MSK)
    future = []
    for event in get_user_events(user_id):
        event_dt = datetime.strptime(
            f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M"
        ).replace(tzinfo=MSK)
        if event_dt > now:
            future.append(event)
    future.sort(key=lambda x: (x["date"], x["time"]))
    return future


def get_events_for_period(
    user_id: int, start: datetime, end: datetime
) -> list[dict]:
    """Возвращает события за указанный период."""
    result = []
    for event in get_user_events(user_id):
        event_dt = datetime.strptime(
            f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M"
        )
        if start <= event_dt <= end:
            result.append(event)
    result.sort(key=lambda x: (x["date"], x["time"]))
    return result


def get_tomorrow_events(user_id: int) -> list[dict]:
    """Возвращает события на завтра."""
    now = datetime.now(MSK)
    tomorrow = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    )
    end = tomorrow.replace(hour=23, minute=59, second=59)
    return get_events_for_period(user_id, tomorrow, end)


def get_next_3_days_events(user_id: int) -> list[dict]:
    """Возвращает события на ближайшие 3 дня."""
    now = datetime.now(MSK)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    end = start + timedelta(days=3)
    return get_events_for_period(user_id, start, end)


def get_month_events(user_id: int) -> list[dict]:
    """Возвращает события на текущий месяц."""
    now = datetime.now(MSK)
    start = now.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    )
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1) - timedelta(seconds=1)
    else:
        end = start.replace(month=start.month + 1) - timedelta(seconds=1)
    return get_events_for_period(user_id, start, end)


def format_events(events: list[dict], title: str) -> str:
    """Форматирует список событий в текст."""
    if not events:
        return f"{title}\n\nНет событий."
    lines = [title, ""]
    for event in events:
        lines.append(f"  {event['date']} {event['time']} — {event['title']}")
    return "\n".join(lines)


async def ask_ai(user_message: str) -> str:
    """Отправляет запрос к AI и возвращает ответ."""
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты полезный AI-ассистент в VK боте. "
                        "Отвечай кратко и по-русски."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=512,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка AI: {e}"
