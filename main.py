from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict
from decimal import Decimal
import uuid

app = FastAPI(title="User Balance Service", version="1.0.0")


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    balance: Decimal = Field(..., ge=0, decimal_places=2)

class User(BaseModel):
    id: str
    name: str
    email: str
    balance: Decimal

class TransferRequest(BaseModel):
    from_user_id: str
    to_user_id: str
    amount: Decimal = Field(..., gt=0, decimal_places=2)

class TransferResponse(BaseModel):
    success: bool
    message: str
    from_user_balance: Decimal
    to_user_balance: Decimal


users_storage: Dict[str, Dict] = {}
email_index: Dict[str, str] = {}



@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Создание нового пользователя"""
    

    if user_data.email in email_index:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    

    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "name": user_data.name,
        "email": user_data.email,
        "balance": user_data.balance
    }
    

    users_storage[user_id] = user
    email_index[user_data.email] = user_id
    
    return User(**user)


@app.get("/users", response_model=List[User])
async def get_users():
    """Получение списка всех пользователей"""
    return [User(**user) for user in users_storage.values()]


@app.post("/transfer", response_model=TransferResponse)
async def make_transfer(transfer: TransferRequest):
    """Перевод средств между пользователями"""
    

    if transfer.from_user_id not in users_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь-отправитель не найден"
        )
    
    if transfer.to_user_id not in users_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь-получатель не найден"
        )
    

    if transfer.from_user_id == transfer.to_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя переводить средства самому себе"
        )
    
    sender = users_storage[transfer.from_user_id]
    receiver = users_storage[transfer.to_user_id]
    

    if sender["balance"] < transfer.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно средств для перевода"
        )
    

    sender["balance"] -= transfer.amount
    receiver["balance"] += transfer.amount
    
    return TransferResponse(
        success=True,
        message=f"Успешно переведено {transfer.amount} от {sender['name']} к {receiver['name']}",
        from_user_balance=sender["balance"],
        to_user_balance=receiver["balance"]
    )


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Получение информации о конкретном пользователе"""
    if user_id not in users_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return User(**users_storage[user_id])


@app.get("/")
async def root():
    return {"message": "User Balance Service API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)