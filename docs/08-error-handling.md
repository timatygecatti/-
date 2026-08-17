# Обработка ошибок

## Базовая обработка ошибок

```python
from vkbottle.bot import Bot

bot = Bot(token="token")

@bot.on.error_handler.register
async def error_handler(e: Exception):
    print(f"Ошибка: {e}")
```

## Источник

https://vkbottle.readthedocs.io/ru/latest/tutorial/error-handling/
