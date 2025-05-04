-- Bảng: dim_user
CREATE TABLE dim_user (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding JSONB
);

-- Bảng: dim_movie
CREATE TABLE dim_movie (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rated VARCHAR(15),
    total_rating DOUBLE PRECISION CHECK (total_rating BETWEEN 0 AND 5) DEFAULT 5,
    rating_total_count INT DEFAULT 0 CHECK (rating_total_count >= 0),
    runtime INT,
    release_date DATE,
    budget BIGINT,
    revenue BIGINT,
    description TEXT DEFAULT '',
    status VARCHAR(63),
    poster TEXT,
    country VARCHAR(255),
    language VARCHAR(255)
);

-- Bảng: dim_genres
CREATE TABLE dim_genres (
    id SERIAL PRIMARY KEY,
    type VARCHAR(63) NOT NULL
);

-- Bảng: dim_person
CREATE TABLE dim_person (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    stage_name VARCHAR(255),
    profile TEXT DEFAULT '',
    gender INT NOT NULL CHECK (gender IN (0, 1, 2, 3)),
    known_for_dept VARCHAR(255)
);

-- Bảng: dim_movie_genres (liên kết Movie và Genre - many-to-many)
CREATE TABLE dim_movie_genres (
    movie_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES dim_movie (id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES dim_genres (id) ON DELETE CASCADE
);

-- Bảng: dim_credits (liên kết Movie và Person)
CREATE TABLE dim_credits (
    movie_id INT NOT NULL,
    person_id INT NOT NULL,
	role VARCHAR(255) NOT NULL,
    job TEXT NOT NULL,
	PRIMARY KEY (movie_id, person_id),
    FOREIGN KEY (movie_id) REFERENCES dim_movie (id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES dim_person (id) ON DELETE CASCADE
);

-- Bảng: fact_movie_rating (rating phim của user)
CREATE TABLE fact_movie_rating (
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    rating DOUBLE PRECISION DEFAULT 5 CHECK (rating BETWEEN 0 AND 5),
	timestamp INT,
	date DATE,
	PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES dim_user (id) ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES dim_movie (id) ON DELETE CASCADE
);

-- Bảng: dim_search_log (lưu lịch sử tìm kiếm)
CREATE TABLE dim_search_log (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    searched_content TEXT NOT NULL DEFAULT '',
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES dim_user (id)
);

-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;