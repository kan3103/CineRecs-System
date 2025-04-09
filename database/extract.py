# import necessary libraries
import requests, json, os, random
from dotenv import load_dotenv
import pandas as pd
from faker import Faker
from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext
from pyspark.sql import functions as func
from pyspark.sql.types import StringType, StructType, StructField, IntegerType
from pyspark.sql.functions import concat, lit

#inital configuration
faker = Faker()

spark = SparkSession.builder.appName("DataProcessing").getOrCreate()
conf = SparkConf().setAppName("DataProcessing").setMaster("local[*]")
sc = SparkContext(conf=conf)

load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_API_READ_ACCESS_TOKEN = os.getenv('TDMB_API_READ_ACCESS_TOKEN')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')


# helper functions
def get_data_from_omdb_with_imdb_id(imdb_id):
    url = "http://www.omdbapi.com/?apikey=" + OMDB_API_KEY + "&i=" + imdb_id
    response = requests.get(url)
    return response.json()

def get_all_genres():
    movies_genres_url = "https://api.themoviedb.org/3/genre/movie/list"
    tv_genres_url = "https://api.themoviedb.org/3/genre/tv/list"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    movies_response = requests.get(movies_genres_url, params=params)
    tv_response = requests.get(tv_genres_url, params=params)
    if movies_response.status_code == 200 and tv_response.status_code == 200:
        genre_list = movies_response.json()["genres"] + tv_response.json()["genres"]
        result = []

        for genre in genre_list:
            genre = genre["name"]
            result.append(genre)

        return result    
    
    else:
        print("Error fetching data:", movies_response.status_code, tv_response.status_code)
        return []

# user: id, name, dob, username, password, created_at, embedding matrix
def gen_user(num_user):
    id, name, dob, username, password, created_at = [], [], [], [], [], []
    for i in range(num_user):
        id.append(i + 1)
        name.append(faker.name())
        dob.append(faker.date_of_birth(minimum_age=18, maximum_age=70))
        username.append(faker.user_name())
        password.append(faker.password())
        created_at.append(faker.date_time_this_decade())

    user_df = pd.DataFrame({
        "id": id,
        "name": name,
        "dob": dob,
        "username": username,
        "password": password,
        "created_at": created_at
    })

    return user_df

# ----------------------------------------------------------------------------------

if __name__ == "__main__":
    # dim movie: Id, name, rated, avg_rating, rating_count, runtime, release_date, budget, revenue,
    # description / plot, status, poster, language, country
    schema_links = StructType([
        StructField("movieId", StringType(), True),
        StructField("imdbId", StringType(), True),
        StructField("tmdbId", StringType(), True)
    ])

    movies = spark.read.csv("dataset/movies.csv", header=True, inferSchema=True)
    links = spark.read.csv("dataset/links.csv", header=True, schema=schema_links)

    movies = movies.select("movieId", "title", "genres")
    links = links.select("movieId", "imdbId")
    links = links.withColumn("imdbId", concat(lit("tt"), links["imdbId"].cast("string")))

    movies = movies.join(links, on="movieId", how="inner")

    movies_df = movies.toPandas()
    rated, avg_rating, rating_count, runtime, release_date, budget, revenue, desc, status, poster, language, country, genre = [], [], [], [], [], [], [], [], [], [], [], [], []
    director, writer, actor = [], [], []

    for idtf in movies["imdbId"]:
        response = get_data_from_omdb_with_imdb_id(idtf)
        rated.append(response["Rated"] if "Rated" in response else None)
        avg_rating.append(response["imdbRating"] if "imdbRating" in response else None)
        rating_count.append(response["imdbVotes"] if "imdbVotes" in response else None)
        runtime.append(response["Runtime"] if "Runtime" in response else None)
        release_date.append(response["Released"] if "Released" in response else None)
        budget.append(0)
        revenue.append(response["BoxOffice"] if "BoxOffice" in response else None)
        desc.append(response["Plot"] if "Plot" in response else None)
        status.append(response["Response"] if "Response" in response else None)
        poster.append(response["Poster"] if "Poster" in response else None)
        language.append(response["Language"] if "Language" in response else None)
        country.append(response["Country"] if "Country" in response else None)
        genre.append(response["Genre"] if "Genre" in response else None)
        director.append(response["Director"] if "Director" in response else None)
        writer.append(response["Writer"] if "Writer" in response else None)
        actor.append(response["Actors"] if "Actors" in response else None)

    movies_df["rated"] = rated
    movies_df["avg_rating"] = avg_rating
    movies_df["rating_count"] = rating_count
    movies_df["runtime"] = runtime
    movies_df["release_date"] = release_date
    movies_df["budget"] = budget
    movies_df["revenue"] = revenue
    movies_df["desc"] = desc
    movies_df["status"] = status
    movies_df["poster"] = poster
    movies_df["language"] = language
    movies_df["country"] = country

    movies_df.to_csv("dataset/movies.csv", index=False)

    # fact movie rating
    rating_df = spark.read.csv("dataset/ratings.csv", header=True, inferSchema=True)
    rating_df = rating_df.select("userId", "movieId", "rating")

    # dim movie genre
    movie_genre_id_list, movies_name_list, movies_genre_genre_list = [], [], []

    for i in range(len(movies_df)):
        genre_list = movies_df.loc[i, "genres"].split(",")
        for genre in genre_list:
            movie_genre_id_list.append(i + 1)
            movies_name_list.append(movies_df.loc[i, "title"])
            movies_genre_genre_list.append(genre)

    movie_genre_df = pd.DataFrame({
        "id": movie_genre_id_list,
        "movie_name": movies_name_list,
        "genre": movies_genre_genre_list
    })

    movie_genre_df = movie_genre_df.drop_duplicates(subset=["movie_name", "genre"])
    movie_genre_df["id"] = range(1, len(movie_genre_df) + 1)

    # dim genre
    genre_list = get_all_genres()
    genre_df = pd.DataFrame({
        "id": range(1, len(genre_list) + 1),
        "name": genre_list
    })

    # dim people 
    director_set = set()
    writer_set = set()
    actor_set = set()

    # dim crew
    crew_df = spark.read.csv("dataset/crew_info.tsv", header=True, inferSchema=True, sep="\t")

    crew_df = crew_df.select(
        "tconst",
        "nconst",
        "category",
        "characters"
    )

    # Replace "self" with "actor" in the "category" column
    crew_df = crew_df.withColumn(
        "category",
        func.when(crew_df["category"] == "self", "actor").otherwise(crew_df["category"])
    )

    # dim user
    user_df = gen_user(200948)

    # dim user search log


    # load data to csv files