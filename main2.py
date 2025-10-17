from typing import Union
import json
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

data = {}
file_name = 'user.json'

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


class Feedback(BaseModel):
    name : str
    text : str


class Log_Pas(BaseModel):
    log : str
    pas : str


class CalcRequest(BaseModel):
    a : float
    b : float


@app.get("/")
def read_root():
    return {"Ye"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.post("/reg")
async def get_log_pas(log_pas : Log_Pas):
    data[log_pas.log] = log_pas.pas
    with open (file_name, "w") as file:
        json.dump({log_pas.log : log_pas.pas}, file)
    return log_pas

@app.get("/about")
def about_me():
    return{"I'am Senyor by Python"}

@app.get("/square/{number}")
def square(number : int):
    return{"number": number, "square": number * number}

@app.get("/greet")
def greet(name: str, age: int):
    return{"message": f"Hello, {name}! You're {age} years old."}

@app.get("/compare")
def comparete(a : int, b : int):
    if a > b:
        result = "a more than b"
    elif b > a:
        result = "b more than a"
    else:
        result = "numbers equal"
    
    return {"result" : result}

@app.post("/feedback")
def feedback(data : Feedback):
    if data.text=="":
        return{"error": f"review can't be empty"}
    return{"message": f"Thank You for the review, {data.name}!"}

@app.post("/calc")
def calculate(data : CalcRequest):
    if data.b == 0:
        return{"error": "division by zero is impossible"}
    return{
        "sum" : data.a + data.b,
        "sub" : data.a - data.b,
        "mul" : data.a * data.b,
        "div" : data.a / data.b
    }