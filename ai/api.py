import pandas as pd
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine ,text
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
if os.path.exists('metadata/data.json'):
    with open('metadata/data.json', 'r') as f:
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
        # Load environment variables
        dotenv.load_dotenv()
        
        # Get the database URL from environment variables or use a default value
        self.db_url = os.getenv("DATABASE_URL")

        
        # If the database URL is None or empty, use a default connection string
        if not self.db_url:
            # Default PostgreSQL connection string (modify this to match your database)
            self.db_url = "postgresql+asyncpg://avnadmin:AVNS_4QIAupJ-5VLHdr7KGKM@btl-data-mining-btl-data-mining.f.aivencloud.com:18362/defaultdb"
            print(f"WARNING: DATABASE_URL environment variable not set. Using default: {self.db_url}")
        
        self.engine = create_engine(self.db_url)
        if not os.path.exists('models/knn_model.pkl'):
            self.create_movies_matrix()

    
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
        self.X = np.concatenate([movie_id,X_genre, X_year, X_country, X_name, X_roles], axis=1)
        
        X_genre_shape = X_genre.shape[1]
        X_year_shape = X_year.shape[1]
        X_country_shape = X_country.shape[1]
        X_name_shape = X_name.shape[1]

        
        with open('metadata/data.json', 'w') as f:
            data = {
                'X_genre': X_genre_shape,
                'X_year': X_year_shape,
                'X_country': X_country_shape,
                'X_name': X_name_shape
            }
            json.dump(data, f)
        x_train = self.X[:, 1:]
        knn = NearestNeighbors(n_neighbors=250, metric=DistanceMetric.get_metric('pyfunc', func=custom_distance))
        knn.fit(x_train)
        joblib.dump(knn, 'models/knn_model.pkl')
        
    def get_user_recommendations(self, user_id, n_recommendations=10):
        """
        Get personalized movie recommendations for a user based on their liked movies.
        If the user hasn't liked any movies, returns an empty list.
        """
        # Check if the user has any liked movies
        if not self.has_liked_movies(user_id):
            print(f"User {user_id} has no liked movies, returning empty list")
            return []
            
        # Otherwise, get personalized recommendations
        try:
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
            knn = joblib.load('models/knn_model.pkl')
            distances, indices = knn.kneighbors(embedding)
            id_movies = []
            for i in range(len(indices[0])):
                index = indices[0][i]
                movie_id = movies_id[index]
                if str(movie_id) in movies_user:
                    continue
                else:
                    id_movies.append(int(movie_id))
                if len(id_movies) >= n_recommendations:
                    break
                    
            return id_movies[:n_recommendations]
            
        except Exception as e:
            print(f"Error in get_user_recommendations: {e}")
            return []

    def update_embedding(self, user_id):
        query = f"""
            SELECT 
                du.id AS user_id,
                du.name AS user_name,
                fmr.rating AS rating,
                fmr.movie_id AS movie_id,
                fmr.timestamp AS timestamp

            FROM dim_user du
            JOIN fact_movie_rating fmr ON du.id = fmr.user_id
            wHERE du.id = {user_id}
        """

        users = pd.read_sql(query, self.engine)


        train, test = train_test_split(users, test_size=0.2, random_state=40)

        movie_user_train = np.zeros((len(train), self.X[:,1:].shape[1]))
        for i in range(len(train)):
            movie_id = train["movie_id"].iloc[i]
            indices = np.where(self.X[:, 0] == movie_id)[0]
            if len(indices) > 0:
                movie_user_train[i, :] = self.X[indices[0], 1:]
            else:
                movie_user_train[i, :] = np.zeros(self.X[:, 1:].shape[1])
            

        year_rating = train["timestamp"].values
        latest_time = np.max(year_rating)
        # Tính độ lệch thời gian
        time_deltas = latest_time - year_rating  # càng cũ thì càng lớn

        # Chuyển đổi độ lệch thời gian thành trọng số (càng cũ thì càng nhỏ)
        alpha = 1e-8
        year_rating = 1 / (1 + alpha * time_deltas)

        user_rating = train["rating"].values
        user_rating = list(map(lambda x: x-2.9, user_rating))
        user_rating = user_rating*year_rating



        result = np.dot(user_rating,movie_user_train)
        result = (result - np.min(result)) / (np.max(result) - np.min(result))
    
        result_list = result.tolist()
        result_json = json.dumps(result_list)
        query = text("""
            UPDATE dim_user
            SET embedding = :recs
            WHERE id = :uid
        """)

        with self.engine.connect() as conn:
            conn.execute(query, {"recs": result_json, "uid": user_id})
            conn.commit()

    def get_top_rated_movies(self, count=10):
        """
        Get the highest rated movies from the database.
        Used for new users or for the initial homepage recommendations.
        """
        query = """
            SELECT 
                dm.id AS movie_id
            FROM 
                dim_movie dm
            WHERE
                dm.rating IS NOT NULL
            ORDER BY 
                dm.rating DESC, dm.rating_total_count DESC
            LIMIT :count
        """
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), {"count": count})
                movie_ids = [row[0] for row in result]
                return movie_ids
        except Exception as e:
            print(f"Error getting top rated movies: {e}")
            return []

    def update_user_embedding(self, user_id):
        """
        Update the user embedding after they like a movie.
        This will recalculate the user's embedding based on their liked movies.
        """
        # Fetch all the user's liked movies
        query = f"""
            SELECT 
                fmr.user_id,
                STRING_AGG(fmr.movie_id::text, ',') AS movie_ids
            FROM 
                fact_movie_rating fmr
            WHERE 
                fmr.user_id = {user_id}
            GROUP BY 
                fmr.user_id
        """
        
        # Get user's liked movies
        try:
            user_movies_df = pd.read_sql(query, self.engine)
            
            if user_movies_df.empty:
                print(f"No liked movies found for user {user_id}")
                return False
            
            # Get movie IDs liked by the user
            movie_ids = user_movies_df['movie_ids'].values[0].split(',')
            movie_ids = [int(mid) for mid in movie_ids]
            
            # Fetch feature vectors for these movies
            # First, we need all movies to get the indices in our model
            all_movies_query = """
                SELECT 
                    dm.id AS movie_id,
                    dm.name AS movie_name
                FROM 
                    dim_movie dm
                ORDER BY 
                    dm.id
            """
            all_movies = pd.read_sql(all_movies_query, self.engine)
            all_movie_ids = all_movies['movie_id'].values.astype(int)
            
            # Get the matrix we saved earlier
            try:
                # Ensure we have the latest model
                self.create_movies_matrix()
                knn = joblib.load('models/knn_model.pkl')
                
                # Create a new embedding for the user based on their liked movies
                # First find the indices of the user's liked movies in our dataset
                movie_indices = []
                for mid in movie_ids:
                    indices = np.where(all_movie_ids == mid)[0]
                    if len(indices) > 0:
                        movie_indices.append(indices[0])
                
                if not movie_indices:
                    print(f"None of user {user_id}'s liked movies are in our dataset")
                    return False
                
                # Get the feature vectors for these movies and create user embedding
                # We're taking the average embedding of all the movies they liked
                user_embedding = np.mean([knn._fit_X[idx] for idx in movie_indices], axis=0)
                
                # Update the user's embedding in the database
                update_query = f"""
                    UPDATE dim_user
                    SET embedding = ARRAY{user_embedding.tolist()}::float[]
                    WHERE id = {user_id}
                """
                
                with self.engine.connect() as connection:
                    connection.execute(text(update_query))
                    connection.commit()
                    
                print(f"Successfully updated embedding for user {user_id}")
                return True
                
            except Exception as e:
                print(f"Error updating user embedding: {e}")
                return False
                
        except Exception as e:
            print(f"Error in update_user_embedding: {e}")
            return False

    def has_liked_movies(self, user_id):
        """
        Check if a user has liked any movies.
        Returns True if the user has liked at least one movie, False otherwise.
        """
        query = f"""
            SELECT COUNT(*) as like_count
            FROM fact_movie_rating
            WHERE user_id = {user_id}
        """
        
        try:
            like_count_df = pd.read_sql(query, self.engine)
            like_count = like_count_df['like_count'].values[0]
            return like_count > 0
        except Exception as e:
            print(f"Error checking if user has liked movies: {e}")
            return False



