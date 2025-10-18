from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
books = []
sort_books_by_author = []
books_ids = []


class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int


@app.post("/books")
def add_book(book: Book):
    if book.id not in books_ids:
        books_ids.append(book.id)
        books.append(book)
        return "book added"
    else:
        return "this book already added"

@app.get("/books")
def get_books(author: str = None):
    if author:
        sort_books_by_author.clear()
        for book in books:
            if book.author == author:
                sort_books_by_author.append(book)
        if sort_books_by_author:
            return sort_books_by_author
        else:
            return "error"
        
    return books