import React from "react";
import test from "../../../assets/images/Home/test.png";
import test1 from "../../../assets/images/Home/test1.png";
import test2 from "../../../assets/images/Home/test2.png";
import test3 from "../../../assets/images/Home/test3.png";
import test4 from "../../../assets/images/Home/test4.png";
import MovieCard from "../../../components/MovieCard";

const trendingMovies = [
    {
        title: "Godzilla y Kong",
        year: "2024",
        genre: "Action",
        image: test1,
    },
    {
        title: "Del revés 2",
        year: "2024",
        genre: "Sci-fi",
        image: test2,
    },
    {
        title: "El reino del planeta de los simios",
        year: "2024",
        genre: "Documentary Action",
        image: test3,
    },
    {
        title: "Deadpool 3",
        year: "2021",
        genre: "Action",
        image: test4,
    },
];

const Trending = () => {
    return (
        <div className="px-6 py-4">
            <h2 className="text-xl font-bold mb-4 text-white">Trending</h2>
            <div className="flex flex-wrap gap-10">
                {trendingMovies.map((movie, index) => (
                    <MovieCard
                        key={index}
                        image={movie.image}
                        title={movie.title}
                        year={movie.year}
                        genre={movie.genre}
                    />
                ))}
            </div>
        </div>
    );
};

export default Trending;
