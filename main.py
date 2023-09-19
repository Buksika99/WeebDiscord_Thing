from typing import List, Optional
from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from fastapi.responses import JSONResponse, PlainTextResponse
from dotenv import load_dotenv
import os

# Load environment variables from credentials.env
load_dotenv(".env")

app = FastAPI()


# Database configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}


def connect_to_database():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error connecting to database:", e)
        return None



def close_database_connection(connection):
    if connection.is_connected():
        connection.close()


class Anime(BaseModel):
    id: int = 0
    Title: str = 'Unknown'
    mediaType: str = 'Unknown'
    episodes: int = 0
    duration: str = 'Unknown'
    ongoing: str = 'Unknown'
    start_year: Optional[str] = None
    finish_year: Optional[str] = None
    Season_of_Release: str = 'Unknown'
    description: str = 'No description available'
    studios: str = 'Unknown'
    tags: str = 'Unknown'
    content_warning: str = 'Unknown'
    watched: int = 0
    watching: int = 0
    want_to_watch: int = 0
    dropped: int = 0
    rating: str = 'Unknown'
    votes: int = 0


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/anime/{anime_id}", response_model=Anime)
def read_anime(anime_id: int):
    connection = connect_to_database()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM animetrying WHERE id = %s"  # Use the new table name and column names
        cursor.execute(query, (anime_id,))
        anime = cursor.fetchone()
        if anime:
            # Create a formatted plain text response
            formatted_response = f"ID: {anime['id']}\n" \
                                 f"Title: {anime['Title']}\n" \
                                 f"mediaType: {anime['mediaType']}\n" \
                                 f"episodes: {anime['episodes']}\n" \
                                 f"duration: {anime['duration']}\n" \
                                 f"ongoing: {anime['ongoing']}\n" \
                                 f"start_year: {anime['start_year']}\n" \
                                 f"finish_year: {anime['finish_year']}\n" \
                                 f"Season_of_Release: {anime['Season_of_Release']}\n" \
                                 f"description: {anime['description']}\n" \
                                 f"studios: {anime['studios']}\n" \
                                 f"tags: {anime['tags']}\n" \
                                 f"content_warning: {anime['content_warning']}\n" \
                                 f"watched: {anime['watched']}\n" \
                                 f"watching: {anime['watching']}\n" \
                                 f"want_to_watch: {anime['want_to_watch']}\n" \
                                 f"dropped: {anime['dropped']}\n" \
                                 f"rating: {anime['rating']}\n" \
                                 f"votes: {anime['votes']}\n"

            return PlainTextResponse(content=formatted_response)
        else:
            raise HTTPException(status_code=404, detail="Anime not found")
    except Error as e:
        print("Error querying database:", e)
        raise HTTPException(status_code=500, detail="Database query error")
    finally:
        close_database_connection(connection)

@app.post("/anime/", response_model=Anime)
def create_anime(anime: Anime):
    connection = connect_to_database()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection error")

    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO animetrying (
            Title, mediaType, episodes, duration, ongoing, start_year, finish_year,
            Season_of_Release, description, studios, tags, content_warning, watched,
            watching, want_to_watch, dropped, rating, votes
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            anime.Title, anime.mediaType, anime.episodes, anime.duration, anime.ongoing,
            anime.start_year, anime.finish_year, anime.Season_of_Release, anime.description,
            anime.studios, anime.tags, anime.content_warning, anime.watched, anime.watching,
            anime.want_to_watch, anime.dropped, anime.rating, anime.votes
        )
        cursor.execute(query, data)
        connection.commit()
        return anime
    except Error as e:
        print("Error inserting into database:", e)
        raise HTTPException(status_code=500, detail="Database insertion error")
    finally:
        close_database_connection(connection)
