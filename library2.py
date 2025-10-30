from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import  Optional

app = FastAPI()

DATABASE_URL = "sqlite:///./library.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread" : False})

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    published_year: Optional[int] = Field(default=None)

class BookBase(SQLModel):
    title: str
    author: str
    published_year: Optional[int] = None

class BookCreate(BookBase):
    pass

class BooKRead(BookBase):
    id: int

class BookUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    published_year: Optional[int] = None

SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/books")
def create_books(book: BookCreate, session: Session = Depends(get_session)):
    db_book = Book(title=book.title, author=book.author, published_year=book.published_year)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@app.get("/books")
def read_books(session: Session = Depends(get_session)):
    book = session.exec(select(Book)).all()
    return book

@app.get("/books/{book_id}")
def read_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}")
def update_book(book_id: int, book_update: BookUpdate, session: Session = Depends(get_session)):
    db_book = session.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book_update.title:
        db_book.title = book_update.title
    if book_update.author:
        db_book.author = book_update.author
    if book_update.published_year:
        db_book.published_year = book_update.published_year
    
    session.commit()
    return db_book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"message": "Book deleted successfully"}