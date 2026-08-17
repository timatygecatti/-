# Мидлвари и Return менеджеры

## Мидлвари

Мидлвари выполняются до или после хендлера:

```python
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.middleware import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    async def pre_process(self, message: Message) -> dict | None:
        # код до хендлера
        return {"user_id": message.from_id}

    async def post_process(self, message: Message, dict: dict) -> None:
        # код после хендлера
        pass

bot.labeler.message_middleware_view.middleware(MyMiddleware())
```

## Return менеджеры

Для возврата данных из хендлеров:

```python
from vkbottle import Bot
from vkbottle.dispatch.return_manager import ReturnManager

# Использование return_manager
```

## Источник

https://vkbottle.readthedocs.io/ru/latest/tutorial/middlewares-return-managers/
