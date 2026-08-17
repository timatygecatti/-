# LongPoll API (Polling)

## Работа с поллингом

### Методы

- `get_server()` — получает сервер для поллинга
- `get_event()` — делает долгий POST запрос
- `listen()` — асинхронный итератор, генерирует ивенты
- `construct()` — принимает API, конструирует поллинг с обновленным API

### Стандартные параметры BotPolling

| Параметр | Описание |
|---|---|
| `api` | Если не указано, будет получено в `listen` |
| `group_id` | Если не указано, будет получено в `listen` |
| `wait` | Лимит секунд (долгий реквест) |
| `rps_delay` | Задержка (по умолчанию 0) |

## Использование в боте

```python
from vkbottle.bot import Bot

bot = Bot(token="token")
# LongPoll автоматически используется при bot.run_forever()
bot.run_forever()
```

## Явное использование Polling

```python
from vkbottle import API
from vkbottle.bot import BotPolling

api = API("token")
polling = BotPolling(api)

async for event in polling.listen():
    # обработка событий
    pass
```

## Bot vs User Polling

- `BotPolling` — для ботов (групп)
- `UserPolling` — для юзерботов

## Источник

https://vkbottle.readthedocs.io/ru/latest/low-level/polling/
