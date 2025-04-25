# Movie Recommendation System

## Overview
This project is part of our **Data Mining course** and aims to build a **Movie Recommendation System** using data mining techniques. The system utilizes a dataset containing **user ratings, user information, and movie details** to generate personalized movie recommendations.

## Team Members
- **Phạm Lê Hoài Hải** 
- **Phan Lương Hưng** 
- **Ngô Khoa** 
- **Nguyễn Trường Giang** 
- **Lý Nguyên Khang** 
- **Bùi Thanh Bách**

## Features
- **User-based and Item-based Collaborative Filtering**
- **Content-Based Recommendation**
- **Hybrid Recommendation Model**
- **Scalable Backend with FastAPI**
- **Interactive Frontend using ReactJS**
- **Optimized Database and Data Warehouse for Efficient Querying**

## Dataset
Our dataset includes:
1. **User Ratings** - Information about users' interactions with movies.
2. **User Information** - Basic demographic details (age, location, etc.).
3. **Movie Details** - Metadata such as genre, actors, directors, and descriptions.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: ReactJS (JavaScript)
- **AI Algorithm**: Scikit-learn, TensorFlow/PyTorch
- **Database**: PostgreSQL (Data Warehouse), Apache Airflow (ETL), Apache Spark (Data Processing)
- **Data Visualization**: Matplotlib, Seaborn, Power BI

## How It Works
1. **Data Processing**: Cleaning and preprocessing user and movie data.
2. **Model Training**: Implementing collaborative filtering and content-based filtering.
3. **Recommendation Generation**: Using trained models to predict user preferences.
4. **User Interaction**: Allowing users to rate movies and receive real-time recommendations.

## Installation


### Backend Setup
```bash
git clone https://github.com/kan3103/CineRecs-System.git
cd backend
pip install -r requirements.txt
python main.py # Port 5623
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Contribution
We welcome contributions! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for more details.

