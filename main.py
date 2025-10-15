from typing import Union
import json
import hashlib
import secrets
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

file_name = 'user.json'

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

class Log_Pas(BaseModel):
    log: str
    pas: str

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    salt, stored_hash = hashed_password.split('$')
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash == stored_hash

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.post("/reg")
async def get_log_pas(log_pas: Log_Pas):
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
    # хеш пароля
        hashed_password = hash_password(log_pas.pas)
        data[log_pas.log] = hashed_password
     
    # cохранение в файл
        with open(file_name, "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        
        return {"message": "User registered successfully", "login": log_pas.log}

@app.post("/login")
async def login(log_pas: Log_Pas):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)

    
    if log_pas.log in data:
        if verify_password(log_pas.pas, data[log_pas.log]):
            return {"message": "Login successful"}
        else:
            return {"error": "Invalid password"}
    else:
        return {"error": "User not found"}