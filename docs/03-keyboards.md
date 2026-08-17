# Клавиатуры и вложения

## Создание клавиатуры

```python
from vkbottle import Keyboard

keyboard = Keyboard(one_time=False)
keyboard.add({"type": "text", "label": "Кнопка 1", "color": "primary"})
keyboard.row()
keyboard.add({"type": "text", "label": "Кнопка 2", "color": "secondary"})
```

## Параметры Keyboard

- `one_time` — клавиатура исчезает после нажатия
- `inline` — инлайн-клавиатура

## Методы Keyboard

- `add(action, color)` — добавляет кнопку к текущему ряду
- `row()` — создаёт следующий ряд кнопок
- `get_json()` — преобразует клавиатуру в JSON

## Отправка клавиатуры

```python
keyboard = ...  # see examples above

@bot.on.message()
async def send_keyboard(message):
    await message.answer("Here is your keyboard!", keyboard=keyboard)
```

## Цвета кнопок

- `primary` — синий
- `secondary` — белый
- `positive` — зелёный
- `negative` — красный

## Типы кнопок

```python
# Текстовая кнопка
{"type": "text", "label": "Название", "color": "primary"}

# Кнопка-ссылка
{"type": "open_link", "link": "https://example.com", "label": "Ссылка"}

# Кнопка-локация
{"type": "location", "payload": "{...}"}

# Кнопка-оплата
{"type": "vkpay", "hash": "action=transfer-to-group&group_id=123&amount=500"}
```

## Вложения

```python
# Если уже есть ссылка на вложение
attachment = "photo-41629685_457239401"

@bot.on.message
async def send_attachment(message):
    await message.answer("See that attachment!", attachment=attachment)
```

## Шаблоны (карусель)

```python
from vkbottle.tools import template_gen, TemplateElement

my_template = template_gen(
    TemplateElement(...),
    TemplateElement(...),
    TemplateElement(...)
)

@bot.on.message()
async def send_template(message):
    await message.answer("Sending template...", template=my_template)
```

## Источник

https://vkbottle.readthedocs.io/ru/latest/tutorial/keyboards-attachments/
