import pandas as pd
from sqlalchemy import create_engine
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import DistanceMetric
from copy import deepcopy
import json
import joblib
import dotenv
import os

X_genre_shape = 0
X_year_shape = 0
X_country_shape = 0
X_name_shape = 0

# Kiểm tra xem tệp JSON đã tồn tại chưa
if os.path.exists('data.json'):
    with open('data.json', 'r') as f:
                temp_data = json.load(f)
    X_genre_shape = temp_data['X_genre'] 
    X_year_shape = temp_data['X_year'] 
    X_country_shape = temp_data['X_country'] 
    X_name_shape = temp_data['X_name']

def custom_distance(vec1, vec2):
    genre_dist = np.linalg.norm(vec1[:X_genre_shape] - vec2[:X_genre_shape])
    year_dist = np.linalg.norm(vec1[X_genre_shape:X_genre_shape + X_year_shape] - vec2[X_genre_shape:X_genre_shape + X_year_shape])
    country_dist = np.linalg.norm(vec1[X_genre_shape + X_year_shape:X_genre_shape + X_year_shape + X_country_shape] - vec2[X_genre_shape + X_year_shape:X_genre_shape + X_year_shape + X_country_shape])
    name_dist = np.linalg.norm(vec1[X_genre_shape + X_year_shape + X_country_shape:X_genre_shape + X_year_shape + X_country_shape+ X_name_shape] - vec2[X_genre_shape + X_year_shape + X_country_shape:X_genre_shape + X_year_shape + X_country_shape+ X_name_shape])
    roles_dist = np.linalg.norm(vec1[X_genre_shape + X_year_shape + X_country_shape + X_name_shape:] - vec2[X_genre_shape + X_year_shape + X_country_shape + X_name_shape:])
    return genre_dist*0.45 + year_dist*0.03 + country_dist*0.15 + name_dist*0.15 + roles_dist*0.22

class API:

    def __init__(self):
        
        dotenv.load_dotenv()
        self.db_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.db_url)


    
    def create_movies_matrix(self):
        global X_genre_shape, X_year_shape, X_country_shape, X_name_shape
        # Truy vấn SQL
        query = """
        WITH genre_agg AS (
            SELECT 
                dmg.movie_id,
                STRING_AGG(DISTINCT dg.type, ', ') AS genres
            FROM 
                dim_movie_genres dmg
            JOIN 
                dim_genres dg ON dmg.genre_id = dg.id
            GROUP BY 
                dmg.movie_id
        ),
        credit_agg AS (
            SELECT 
                dc.movie_id,
                STRING_AGG(DISTINCT dp.name::text, ', ') AS roles
            FROM 
                dim_credits dc 
            JOIN
                dim_person dp ON dc.person_id = dp.id
            WHERE 
                dc.job = 'Director' or (dc.role = 'cast' and dc.job !='role')
            GROUP BY 
                dc.movie_id
        )

        SELECT 
            dm.id AS movie_id,
            dm.name AS movie_name,
            dm.release_date,
            dm.description,
            dm.total_rating,
            dm.country,
            ga.genres,
            ca.roles
        FROM 
            dim_movie dm
        LEFT JOIN 
            genre_agg ga ON dm.id = ga.movie_id
        LEFT JOIN 
            credit_agg ca ON dm.id = ca.movie_id
        ORDER BY 
            dm.id;

        """

        movies = pd.read_sql(query, self.engine)

        movies["genres"] = movies['genres'].fillna('').str.split(',')
        movies["genres"] = movies["genres"].apply(
            lambda x: ['unknown'] if not any(x) else [genre.strip() for genre in x]
        )
        movies["roles"] = movies['roles'].fillna('').str.split(',')
        movies["roles"] = movies["roles"].apply(
            lambda x: ['unknown'] if not any(x) else [role.strip() for role in x]
        )
        movies["release_date"] = pd.to_datetime(movies["release_date"])
        movies["release_date"] = movies["release_date"].dt.year.astype('Int32')
        movies["release_date"] = movies["release_date"].astype(str).fillna("unknown")
        
        train = deepcopy(movies)
        train['genres'] = train['genres'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x))
        train['roles'] = train['roles'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x))
        movie_id = train['movie_id'].values.astype(int)
        movie_id = movie_id.reshape(-1, 1).astype(int)

        # Vector hóa thể loại (genre) và date (director)
        vectorizer = TfidfVectorizer()
        vectorizer2 = TfidfVectorizer()
        vectorizer3 = TfidfVectorizer()
        vectorizer4 = TfidfVectorizer(max_features=1000)  
        vectorizer5 = TfidfVectorizer(max_features=2500)

        X_genre = vectorizer.fit_transform(train['genres']).toarray()
        X_year = vectorizer2.fit_transform(train['release_date']).toarray()
        X_country = vectorizer3.fit_transform(train['country']).toarray()
        X_name = vectorizer4.fit_transform(train['movie_name']).toarray()
        X_roles = vectorizer5.fit_transform(train['roles']).toarray()
        X = np.concatenate([movie_id,X_genre, X_year, X_country, X_name, X_roles], axis=1)
        
        X_genre_shape = X_genre.shape[1]
        X_year_shape = X_year.shape[1]
        X_country_shape = X_country.shape[1]
        X_name_shape = X_name.shape[1]

        
        with open('data.json', 'w') as f:
            data = {
                'X_genre': X_genre_shape,
                'X_year': X_year_shape,
                'X_country': X_country_shape,
                'X_name': X_name_shape
            }
            json.dump(data, f)
        x_train = X[:, 1:]
        knn = NearestNeighbors(n_neighbors=250, metric=DistanceMetric.get_metric('pyfunc', func=custom_distance))
        knn.fit(x_train)
        joblib.dump(knn, 'knn_model.pkl')
        
    def get_user_recommendations(self,user_id,n_recommendations=10):
        query = """
        SELECT 
            dm.id AS movie_id,
            dm.name AS movie_name
        FROM 
            dim_movie dm
        ORDER BY 
            dm.id;

        """

        movies = pd.read_sql(query, self.engine)
        movies_id = movies['movie_id'].values.astype(int)

        query2= f"""
            SELECT 
                du.id AS user_id,
                du.name AS user_name,
                du.embedding AS user_embedding,
                STRING_AGG(fmr.movie_id::text, ',') AS movie_ids
            FROM dim_user du
            JOIN fact_movie_rating fmr ON du.id = fmr.user_id
            WHERE du.id = {user_id}
            GROUP BY du.id

        """
        userss = pd.read_sql(query2, self.engine)
        embedding_str = userss['user_embedding'].values[0]
        embedding = np.array(embedding_str).reshape(1, -1)  

        movies_user = userss['movie_ids'].values[0]
        movies_user = movies_user.split(',')
        

        print(X_genre_shape, X_year_shape, X_country_shape, X_name_shape)
        knn = joblib.load('knn_model.pkl')
        distances, indices = knn.kneighbors(embedding)
        id_movies = []
        for i in range(len(indices[0])):
            index = indices[0][i]
            movie_id = movies_id[index]
            if movie_id in movies_user:
                continue
            else:
                id_movies.append(int(movie_id))
            if len(id_movies) >= n_recommendations:
                break
                
        return id_movies[:n_recommendations]
    
    
        
