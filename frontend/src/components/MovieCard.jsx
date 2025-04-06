import React from "react";
import { toast } from "react-toastify";

const MovieCard = ({ image, title, year, genre }) => {
    const handleAddToFavourite = () => {
        toast.success("Added to Favourite!", {
            position: "top-right",
            autoClose: 2000,
            hideProgressBar: false,
            pauseOnHover: true,
            draggable: true,
            theme: "dark",
        });
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
            <button
                className="absolute top-2 right-2 bg-white/30 hover:bg-white/50 p-2 rounded-full backdrop-blur-md"
                onClick={handleAddToFavourite}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 text-purple-600 fill-purple-600"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                >
                    <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 18.343l-6.828-6.829a4 4 0 010-5.656z" />
                </svg>
            </button>

            {/* Overlay Info */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent text-white p-3">
                <h3 className="text-sm font-semibold truncate">{title}</h3>
                <p className="text-xs text-gray-300">{year} | {genre}</p>
            </div>
        </div>
    );
};

export default MovieCard;
