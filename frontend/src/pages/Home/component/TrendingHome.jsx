import React, { useState, useEffect } from "react";
import MovieCard from "../../../components/MovieCard";
import { getRecommendations, getMovieDetails } from "../../../services/movieService";

// Fallback images in case movie posters are not available
import fallbackImage1 from "../../../assets/images/Home/test1.png";
import fallbackImage2 from "../../../assets/images/Home/test2.png";
import fallbackImage3 from "../../../assets/images/Home/test3.png";
import fallbackImage4 from "../../../assets/images/Home/test4.png";

const fallbackImages = [fallbackImage1, fallbackImage2, fallbackImage3, fallbackImage4];

const Trending = () => {
    const [recommendedMovies, setRecommendedMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [refreshTrigger, setRefreshTrigger] = useState(0); // State to trigger refresh

    const handleFavoriteAdded = (userId, movieId) => {
        // Trigger a refresh of recommendations by updating the state
        setRefreshTrigger(prev => prev + 1);
    };

    useEffect(() => {
        const fetchRecommendations = async () => {
            try {
                setLoading(true);
                // Get logged in user from localStorage
                const userData = JSON.parse(localStorage.getItem('user') || '{}');
                const userId = userData.id;
                
                if (!userId) {
                    throw new Error("User not logged in");
                }
                
                // Get movie recommendations (first 4 for homepage)
                const recommendedIds = await getRecommendations(userId, 48);
                
                if (recommendedIds && recommendedIds.length > 0) {
                    // Get details for the recommended movies
                    const moviesDetails = await getMovieDetails(recommendedIds);
                    
                    // Format the movie data for display
                    const formattedMovies = moviesDetails.map((movie, index) => ({
                        id: movie.id,
                        title: movie.title,
                        year: movie.release_date ? new Date(movie.release_date).getFullYear().toString() : "Unknown",
                        genre: movie.genres?.join(", ") || "Various",
                        image: movie.poster_url || fallbackImages[index % fallbackImages.length]
                    }));
                    
                    setRecommendedMovies(formattedMovies);
                }
            } catch (error) {
                console.error("Failed to fetch recommendations:", error);
                setError("Failed to load recommendations. Please try again later.");
            } finally {
                setLoading(false);
            }
        };

        fetchRecommendations();
    }, [refreshTrigger]); // Add refreshTrigger as dependency to refresh when a movie is liked

    if (loading) {
        return (
            <div className="px-6 py-4">
                <h2 className="text-xl font-bold mb-4 text-white">Recommended for you</h2>
                <div className="flex justify-center items-center h-[300px]">
                    <p className="text-white">Loading recommendations...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="px-6 py-4">
                <h2 className="text-xl font-bold mb-4 text-white">Recommended for you</h2>
                <div className="flex justify-center items-center h-[300px]">
                    <p className="text-white">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="px-6 py-4">
            <h2 className="text-xl font-bold mb-4 text-white">Recommended for you</h2>
            <div className="flex flex-wrap gap-10">
                {recommendedMovies.length > 0 ? (
                    recommendedMovies.map((movie, index) => (
                        <MovieCard
                            key={index}
                            image={movie.image}
                            title={movie.title}
                            year={movie.year}
                            genre={movie.genre}
                            movieId={movie.id}
                            onFavoriteAdded={handleFavoriteAdded}
                        />
                    ))
                ) : (
                    <p className="text-white">No recommendations available. Try liking some movies first!</p>
                )}
            </div>
        </div>
    );
};

export default Trending;
