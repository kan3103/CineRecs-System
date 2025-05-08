import React, { useState, useEffect } from "react";
import MovieCard from "../../../components/MovieCard";
import { getPersonalizedRecommendations, getMovieDetails } from "../../../services/movieService";

// Fallback images in case movie posters are not available
import fallbackImage1 from "../../../assets/images/Home/test1.png";
import fallbackImage2 from "../../../assets/images/Home/test2.png";
import fallbackImage3 from "../../../assets/images/Home/test3.png";
import fallbackImage4 from "../../../assets/images/Home/test4.png";

const fallbackImages = [fallbackImage1, fallbackImage2, fallbackImage3, fallbackImage4];
const MOVIES_PER_PAGE = 8;

const ListTrendingFilm = () => {
    const [recommendedMovies, setRecommendedMovies] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [hasLikedMovies, setHasLikedMovies] = useState(false);

    useEffect(() => {
        const fetchPersonalizedRecommendations = async () => {
            try {
                setLoading(true);
                // Get logged in user from localStorage
                const userData = JSON.parse(localStorage.getItem('user') || '{}');
                const userId = userData.id;
                
                if (!userId) {
                    throw new Error("User not logged in");
                }
                
                // Get personalized recommendations (up to 100 for trending page)
                const recommendedIds = await getPersonalizedRecommendations(userId, 100);
                
                // Check if the user has liked any movies (if recommendedIds is empty, they haven't)
                if (recommendedIds && recommendedIds.length > 0) {
                    setHasLikedMovies(true);
                    
                    // Get details for the recommended movies
                    const moviesDetails = await getMovieDetails(recommendedIds);
                    
                    // Format the movie data for display
                    const formattedMovies = moviesDetails.map((movie, index) => ({
                        id: movie.id,
                        title: movie.title,
                        year: new Date(movie.release_date).getFullYear().toString(),
                        genre: movie.genres?.join(", ") || "Various", // Changed "Unknown" to "Various"
                        image: movie.poster_url || fallbackImages[index % fallbackImages.length]
                    }));
                    
                    setRecommendedMovies(formattedMovies);
                } else {
                    // User hasn't liked any movies
                    setHasLikedMovies(false);
                    setRecommendedMovies([]);
                }
            } catch (error) {
                console.error("Failed to fetch personalized recommendations:", error);
                setError("Failed to load recommendations. Please try again later.");
            } finally {
                setLoading(false);
            }
        };

        fetchPersonalizedRecommendations();
    }, []);

    // Calculate pagination values
    const totalPages = Math.ceil(recommendedMovies.length / MOVIES_PER_PAGE);
    const startIndex = (currentPage - 1) * MOVIES_PER_PAGE;
    const currentMovies = recommendedMovies.slice(startIndex, startIndex + MOVIES_PER_PAGE);

    const handlePrevious = () => {
        setCurrentPage((prev) => Math.max(prev - 1, 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => Math.min(prev + 1, totalPages));
    };

    if (loading) {
        return (
            <div className="px-6 py-4">
                <h2 className="text-xl font-bold mb-4 text-white">Personalized Recommendations</h2>
                <div className="flex justify-center items-center h-[300px]">
                    <p className="text-white">Loading recommendations...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="px-6 py-4">
                <h2 className="text-xl font-bold mb-4 text-white">Personalized Recommendations</h2>
                <div className="flex justify-center items-center h-[300px]">
                    <p className="text-white">{error}</p>
                </div>
            </div>
        );
    }

    if (!hasLikedMovies) {
        return (
            <div className="px-6 py-4">
                <h2 className="text-xl font-bold mb-4 text-white">Personalized Recommendations</h2>
                <div className="flex justify-center items-center h-[300px]">
                    <p className="text-white text-center">
                        Please select a favorite movie to start recommending movies 
                        that match your preferences. 
                        <br /><br />
                        You can like movies from the "Top Rated Movies" section on the Homepage.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="px-6 py-4">
            <h2 className="text-xl font-bold mb-4 text-white">Personalized Recommendations</h2>

            {/* Movie Cards */}
            <div className="flex flex-wrap gap-10 justify-start">
                {currentMovies.length > 0 ? (
                    currentMovies.map((movie, index) => (
                        <MovieCard
                            key={index}
                            image={movie.image}
                            title={movie.title}
                            year={movie.year}
                            genre={movie.genre}
                            movieId={movie.id}
                        />
                    ))
                ) : (
                    <p className="text-white">No movies found that match your preferences.</p>
                )}
            </div>

            {/* Pagination Controls */}
            {recommendedMovies.length > MOVIES_PER_PAGE && (
                <div className="mt-6 flex justify-center gap-4">
                    <button
                        onClick={handlePrevious}
                        disabled={currentPage === 1}
                        className={`px-4 py-2 rounded-lg ${currentPage === 1 ? 'bg-gray-500 cursor-not-allowed' : 'bg-purple-600 hover:bg-purple-700'} text-white`}
                    >
                        Previous
                    </button>
                    <span className="text-white my-auto">Page {currentPage} of {totalPages}</span>
                    <button
                        onClick={handleNext}
                        disabled={currentPage === totalPages}
                        className={`px-4 py-2 rounded-lg ${currentPage === totalPages ? 'bg-gray-500 cursor-not-allowed' : 'bg-purple-600 hover:bg-purple-700'} text-white`}
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
};

export default ListTrendingFilm;
