# Первый бот на vkbottle

```python
import asyncio
from vkbottle.bot import Bot, Message

bot = Bot(token="token")

@bot.on.message(text="Привет")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer("Привет, {}".format(users_info[0].first_name))

bot.run_forever()
```

## Разбор кода

- `@bot.on.message(text="Привет")` — декоратор, ловит сообщения по правилу
- `async def hi_handler(message: Message)` — хендлер с объектом Message
- `await bot.api.users.get(message.from_id)` — запрос информации о пользователе
- `await message.answer(...)` — отправка ответа (шорткат, не требует chat_id и random_id)
- `bot.run_forever()` — запуск из синхронной среды

## Типы декораторов для сообщений

| Декоратор | Описание |
|---|---|
| `.message` | Сообщения из бесед и личных переписок |
| `.private_message` | Только из личных переписок |
| `.chat_message` | Только из бесед |

## Инициализация бота

```python
# Токеном
bot = Bot(token="token")

# Или с API
bot = Bot(api=api)
```

## Источник

https://vkbottle.readthedocs.io/ru/latest/tutorial/first-bot/
