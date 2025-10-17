from typing import Union
import json
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

movies = []
movie_ids = []

class Movie(BaseModel):
    id : int
    title : str
    year : int
    rating : float


@app.get("/movies")
def get_movies():
    return movies

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    for movie in movies:
        if movie.id == movie_id:
            return movie
    return {"error": "movie not found"}

        
@app.post("/movies")
def add_movie(movie : Movie):
    if movie.id in movie_ids:
        return "allready added"
    movies.append(movie)
    movie_ids.append(movie.id)

    return {"message" : f"Movie {movie.title} added!"}
