from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
books = []


class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int


@app.post("/books")
def add_book(book: Book):
    for b in books:
        if b.id == book.id:
            return {"error" : "this book already exists"}
    books.append(book)
    return book

@app.get("/books")
def get_books(author: str = None):  # <-- просто значение по умолчанию
    if author:
        return [b for b in books if b.author == author]
    return books