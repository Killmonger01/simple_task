# User Balance Service

Простой REST API для управления пользователями и их балансом на FastAPI.

## Установка

```bash
pip install fastapi uvicorn[standard] "pydantic[email]"
```

## Запуск

```bash
python main.py
```

Сервер запустится на `http://localhost:8000`

## API

### Создать пользователя
```
POST /users
```
```json
{
  "name": "Иван Петров",
  "email": "ivan@example.com",
  "balance": 1000.00
}
```

### Получить всех пользователей
```
GET /users
```

### Перевод средств
```
POST /transfer
```
```json
{
  "from_user_id": "id_отправителя",
  "to_user_id": "id_получателя", 
  "amount": 100.00
}
```

## Документация

Swagger UI: `http://localhost:8000/docs`