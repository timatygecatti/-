# Правила (Rules)

## Встроенные правила

Импорт из `vkbottle.dispatch.rules.base`:

```python
from vkbottle.dispatch.rules.base import CommandRule

@bot.on.message(CommandRule("say", ["!", "/"], 1))
async def say_handler(message: Message, args: tuple[str]):
    await message.answer(f"<<{args[0]}>>")
```

## Шорткаты правил

```python
@bot.on.message(command=("say", 1))
async def say_handler(message: Message, args: tuple[str]):
    await message.answer(f"<<{args[0]}>>")
```

## Создание собственных правил

```python
from typing import Any
from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule

class MyRule(ABCRule[Message]):
    def __init__(self, lt: int = 100):
        self.lt = lt

    async def check(self, event: Message) -> bool:
        return len(event.text) < self.lt
```

## Регистрация кастомного правила

```python
bot.labeler.custom_rules["my_rule"] = MyRule

@bot.on.message(my_rule=50)
async def handler(message: Message):
    ...
```

## Правила-врапперы

```python
# FuncRule — принимает функцию
@bot.on.message(func=lambda message: len(message.text) < 100)
async def short_handler(message: Message):
    ...

# CoroutineRule — принимает корутину
```

## Источник

https://vkbottle.readthedocs.io/ru/latest/tutorial/rules/
