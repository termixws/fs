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
    for book in books:
        if book.id == book.id:
            return {"error" : "this book already exists"}
    books.append(book)
    return book

def get_books(author: str = None):
    if author:
        result = []
        for book in books:
            if book.author == author:
                result.append(book)
        return result
    else:
        return books