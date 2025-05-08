import React from "react";
import { toast } from "react-toastify";
import { likeMovie, getFavoriteMovies } from "../services/movieService";
import Like from "./Like";

const MovieCard = ({ image, title, year, genre, movieId, onFavoriteAdded }) => {
    const handleAddToFavourite = async () => {
        try {
            // Get user data from localStorage
            const userData = JSON.parse(localStorage.getItem('user') || '{}');
            const userId = userData.id;
            
            if (!userId) {
                toast.error("Please log in to add favorites", {
                    position: "top-right",
                    autoClose: 2000,
                    theme: "dark",
                });
                return;
            }
            
            // Check if movie is already in favorites
            const favorites = getFavoriteMovies();
            if (favorites.includes(movieId)) {
                toast.info("Movie already in favorites", {
                    position: "top-right",
                    autoClose: 2000,
                    theme: "dark",
                });
                return;
            }
            
            // Call the API to like the movie
            if (movieId) {
                await likeMovie(userId, movieId);
                
                // Notify parent component that a favorite was added
                // This will trigger a refresh of the recommendations
                if (onFavoriteAdded) {
                    onFavoriteAdded(userId, movieId);
                }
            }
            
            toast.success("Add to favourite!", {
                position: "top-right",
                autoClose: 2000,
                hideProgressBar: false,
                pauseOnHover: true,
                draggable: true,
                theme: "dark",
            });
        } catch (error) {
            console.error("Error adding to favorites:", error);
            toast.error("Failed to add to favorites", {
                position: "top-right",
                autoClose: 2000,
                theme: "dark",
            });
        }
    };

    return (
        <div className="relative w-[240px] rounded-xl overflow-hidden shadow-md hover:scale-105 transition-transform duration-300">
            {/* Image */}
            <img
                src={image}
                alt={title}
                className="w-full h-[300px] object-cover"
            />

            {/* Favorite Icon */}
            <div className="absolute top-2 right-2">
                <Like movieId={movieId} onLiked={onFavoriteAdded} />
            </div>

            {/* Overlay Info */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent text-white p-3">
                <h3 className="text-sm font-semibold truncate">{title}</h3>
                <p className="text-xs text-gray-300">{year} | {genre}</p>
            </div>
        </div>
    );
};

export default MovieCard;
