import React, { useState } from "react";
import test1 from "../../../assets/images/Home/test1.png";
import test2 from "../../../assets/images/Home/test2.png";
import test3 from "../../../assets/images/Home/test3.png";
import test4 from "../../../assets/images/Home/test4.png";
import MovieCard from "../../../components/MovieCard";

const trendingMovies = [
    { title: "Godzilla y Kong", year: "2024", genre: "Action", image: test1 },
    { title: "Del revés 2", year: "2024", genre: "Sci-fi", image: test2 },
    { title: "El reino del planeta de los simios", year: "2024", genre: "Documentary Action", image: test3 },
    { title: "Deadpool 3", year: "2021", genre: "Action", image: test4 },
    { title: "Spider-Verse", year: "2023", genre: "Animation", image: test1 },
    { title: "Dune Part Two", year: "2024", genre: "Sci-fi", image: test2 },
    { title: "Oppenheimer", year: "2023", genre: "Biography", image: test3 },
    { title: "Avatar 2", year: "2022", genre: "Adventure", image: test4 },
    { title: "Barbie", year: "2023", genre: "Fantasy", image: test1 },
    { title: "The Batman", year: "2022", genre: "Thriller", image: test2 },
    // Add more items as needed
];

const MOVIES_PER_PAGE = 8;

const ListTrendingFilm = () => {
    const [currentPage, setCurrentPage] = useState(1);

    const totalPages = Math.ceil(trendingMovies.length / MOVIES_PER_PAGE);
    const startIndex = (currentPage - 1) * MOVIES_PER_PAGE;
    const currentMovies = trendingMovies.slice(startIndex, startIndex + MOVIES_PER_PAGE);

    const handlePrevious = () => {
        setCurrentPage((prev) => Math.max(prev - 1, 1));
    };

    const handleNext = () => {
        setCurrentPage((prev) => Math.min(prev + 1, totalPages));
    };

    return (
        <div className="px-6 py-4">
            <h2 className="text-xl font-bold mb-4 text-white">Trending</h2>

            {/* Movie Cards */}
            <div className="flex flex-wrap gap-10 justify-start">
                {currentMovies.map((movie, index) => (
                    <MovieCard
                        key={index}
                        image={movie.image}
                        title={movie.title}
                        year={movie.year}
                        genre={movie.genre}
                    />
                ))}
            </div>

            {/* Pagination Controls */}
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
        </div>
    );
};

export default ListTrendingFilm;
