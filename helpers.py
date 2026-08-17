import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

EVENTS_FILE = "events.json"
MSK = ZoneInfo("Europe/Moscow")


def load_all_events() -> dict:
    if not os.path.exists(EVENTS_FILE):
        return {}
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_all_events(data: dict):
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def add_event(user_id: int, title: str, date: str, time: str, reminder_hours: int = 3):
    data = load_all_events()
    uid = str(user_id)
    if uid not in data:
        data[uid] = []
    data[uid].append({
        "title": title,
        "date": date,
        "time": time,
        "reminder_hours": reminder_hours
    })
    save_all_events(data)


def get_user_events(user_id: int) -> list[dict]:
    data = load_all_events()
    return data.get(str(user_id), [])


def get_future_events(user_id: int) -> list[dict]:
    now = datetime.now(MSK)
    events = get_user_events(user_id)
    future = []
    for e in events:
        event_dt = datetime.strptime(f"{e['date']} {e['time']}", "%Y-%m-%d %H:%M")
        event_dt = event_dt.replace(tzinfo=MSK)
        if event_dt > now:
            future.append(e)
    future.sort(key=lambda x: (x["date"], x["time"]))
    return future


def get_events_for_period(user_id: int, start: datetime, end: datetime) -> list[dict]:
    events = get_user_events(user_id)
    result = []
    for e in events:
        event_dt = datetime.strptime(f"{e['date']} {e['time']}", "%Y-%m-%d %H:%M")
        if start <= event_dt <= end:
            result.append(e)
    result.sort(key=lambda x: (x["date"], x["time"]))
    return result


def get_tomorrow_events(user_id: int) -> list[dict]:
    now = datetime.now(MSK)
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    end = tomorrow.replace(hour=23, minute=59, second=59)
    return get_events_for_period(user_id, tomorrow, end)


def get_next_3_days_events(user_id: int) -> list[dict]:
    now = datetime.now(MSK)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    end = start + timedelta(days=3)
    return get_events_for_period(user_id, start, end)


def get_month_events(user_id: int) -> list[dict]:
    now = datetime.now(MSK)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1) - timedelta(seconds=1)
    else:
        end = start.replace(month=start.month + 1) - timedelta(seconds=1)
    return get_events_for_period(user_id, start, end)


def format_events(events: list[dict], title: str) -> str:
    if not events:
        return f"{title}\n\nНет событий."
    lines = [title, ""]
    for e in events:
        lines.append(f"  {e['date']} {e['time']} — {e['title']}")
    return "\n".join(lines)


async def ask_ai(user_message: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты полезный AI-ассистент в VK боте. Отвечай кратко и по-русски."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_output_tokens=512,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка AI: {e}"
