# Разделение кода (Blueprint)

## Blueprint

Для разделения кода на модули используйте Blueprint:

```python
from vkbottle.bot import Blueprint

bp = Blueprint()

@bp.on.message(text="Привет")
async def hi_handler(message: Message):
    await message.answer("Привет!")
```

## Подключение Blueprint к боту

```python
from vkbottle.bot import Bot
from my_module import bp

bot = Bot(token="token")
bp.load(bot)

bot.run_forever()
```

## Источник

https://vkbottle.readthedocs.io/ru/latest/tutorial/code-separation/
