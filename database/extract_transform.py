# import necessary libraries
import requests, json, os, random
from dotenv import load_dotenv
from datetime import datetime
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
def get_movies_by_tmdbId(tmdbId):
    url = f"https://api.themoviedb.org/3/movie/{tmdbId}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data:", response.status_code)
        return []
    
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
    
def get_movies_cast_and_crew(tmdbId):
    url = f"https://api.themoviedb.org/3/movie/{tmdbId}/credits"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data:", response.status_code)
        return []

def people_info_with_id(id):
    url = f"https://api.themoviedb.org/3/person/{id}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data:", response.status_code)
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
    # dim movie: Id, name, rated, avg_rating, rating_count, runtime, release_date, budget, revenue, description, status, poster, language, country
    schema_links = StructType([
        StructField("movieId", IntegerType(), True),
        StructField("imdbId", StringType(), True),
        StructField("tmdbId", StringType(), True)
    ])

    movies = spark.read.csv("dataset/movies.csv", header=True, inferSchema=True)
    links = spark.read.csv("dataset/links.csv", header=True, schema=schema_links)

    movies = movies.select("movieId", "title")
    links = links.select("movieId", "imdbId", "tmdbId")
    links = links.withColumn("imdbId", concat(lit("tt"), links["imdbId"].cast("string")))

    movies = movies.join(links, on="movieId", how="inner")

    movies_df = movies.toPandas()
    movies_df.dropna(subset=["tmdbId"], inplace=True)
    movies_df["movieId"] = [x for x in range(1, len(movies_df) + 1)]

    movies_rated = []
    movies_avg_rating = []
    movies_rating_count = []
    movies_runtime = []
    movies_release_date = []    
    movies_budget = []
    movies_revenue = []
    movies_description = []
    movies_status = []
    movies_poster = []
    movies_language = []
    movies_country = []
    movies_genre = []
    
    for i in range(len(movies_df)):
        tmdbId = movies_df.iloc[i]["tmdbId"]
        movie_details_response = get_movies_by_tmdbId(tmdbId)

        movies_rated.append("For Adults" if movie_details_response["adult"] else "For all ages")
        movies_avg_rating.append(movie_details_response["vote_average"])
        movies_rating_count.append(movie_details_response["vote_count"])
        movies_runtime.append(movie_details_response["runtime"])
        movies_release_date.append(movie_details_response["release_date"])
        movies_budget.append(movie_details_response["budget"])
        movies_revenue.append(movie_details_response["revenue"])
        movies_description.append(movie_details_response["overview"])
        movies_status.append(movie_details_response["status"])
        movies_poster.append(movie_details_response["poster_path"])
        movies_language.append(movie_details_response["original_language"])
        movies_country.append(movie_details_response["origin_country"][0])
        movies_genre.append(i, [x["id"] for x in movie_details_response["genres"]])

    movies_df["rated"] = movies_rated
    movies_df["avg_rating"] = movies_avg_rating
    movies_df["rating_count"] = movies_rating_count
    movies_df["runtime"] = movies_runtime
    movies_df["release_date"] = movies_release_date
    movies_df["budget"] = movies_budget
    movies_df["revenue"] = movies_revenue
    movies_df["description"] = movies_description
    movies_df["status"] = movies_status
    movies_df["poster"] = movies_poster
    movies_df["language"] = movies_language
    movies_df["country"] = movies_country

    # dim movie genre
    movies_genre_movieId, movies_genre_genreId = [], []
    for i in range(len(movies_genre)):
        movies_genre_movieId.extend([movies_genre[i][0]] * len(movies_genre[i][1]))
        movies_genre_genreId.extend(movies_genre[i][1])

    movies_genre_df = pd.DataFrame({
        "movieId": movies_genre_movieId,
        "genreId": movies_genre_genreId
    })

    # fact movie rating
    rating_df = pd.read_csv("dataset/ratings.csv")
    rating_df["readable_timestamp"] = rating_df["timestamp"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))

    # dim genre
    genre_list = get_all_genres()
    genre_df = pd.DataFrame({
        "id": range(1, len(genre_list) + 1),
        "name": genre_list
    })

    # dim crew: movieId, personId, role
    people_set = set()

    credits_movieId, credits_personId, credits_role = [], [], []

    for i in range(len(movies_df)):
        tmdbId = movies_df.iloc[i]["tmdbId"]
        cac_response = get_movies_cast_and_crew(tmdbId)
        cast = cac_response["cast"]
        crew = cac_response["crew"]
        
        for actor in cast:
            if actor["id"] not in people_set:
                people_set.add(actor["id"])
            credits_movieId.append(i + 1)
            credits_personId.append(actor["id"])
            credits_role.append("Actor")

        for crew_member in crew:
            if crew_member["job"] not in ["Director", "Screenplay", "Producer", "Story"]: continue
            if crew_member["id"] not in people_set:
                people_set.add(crew_member["id"])
            credits_movieId.append(i + 1)
            credits_personId.append(crew_member["id"])
            credits_role.append(crew_member["job"])
        
    crew_df = pd.DataFrame({
        "movieId": credits_movieId,
        "personId": credits_personId,
        "role": credits_role
    })

    # dim people: id, name, dob, stage name, gender, known for department, profile_path, biography
    people_id = []
    people_name = []
    people_dob = []
    people_stage_name = []
    people_gender = []
    people_known_for_department = []
    people_profile_path = []
    people_biography = []

    for person in people_set:
        person_response = people_info_with_id(person)

        people_id.append(person_response["id"])
        people_name.append(person_response["also_known_as"][0] if person_response["also_known_as"] else "")
        people_dob.append(person_response["birthday"])
        people_stage_name.append(person_response["name"])
        people_gender.append(person_response["gender"])
        people_known_for_department.append(person_response["known_for_department"])
        people_profile_path.append(person_response["profile_path"])
        people_biography.append(person_response["biography"])

    # dim user
    user_df = gen_user(200948)

    # dim user search log


    # load data to csv files
