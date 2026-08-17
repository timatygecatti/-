# Установка и настройка

## Установка vkbottle

```bash
pip install vkbottle
```

## Инициализация API

```python
from vkbottle import API

api = API("token")
await api.wall.post(message="#vkbottle прекрасен!")
```

`API` — готовый инструмент для запросов к API ВКонтакте. Полная типизация: [vkbottle/types](https://github.com/vkbottle/types).

## Токен

- Передайте строку (токен) или список токенов
- Токены автоматически конвертируются в token-generator

## Источник

https://vkbottle.readthedocs.io/ru/latest/tutorial/first-bot/
