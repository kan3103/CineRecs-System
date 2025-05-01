import React from "react";
import { useNavigate } from "react-router-dom";
import login from "../../assets/images/login.png";
import trend from "../../assets/images/Home/trend.png";
import heart from "../../assets/images/Home/heart.png";
import film from "../../assets/images/Home/film.png";
import settings from "../../assets/images/Home/setting.png";
import logout from "../../assets/images/Home/logout.png";

import ListTrendingFilm from "../TrendPage/components/ListFilm";

export const Trending = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        // Clear user data from localStorage
        localStorage.removeItem('user');
        // Redirect to login page
        navigate('/');
    };

    return (
        <div className="bg-white min-h-screen flex flex-col">
            <div className="grid grid-cols-[268px_1fr] h-screen overflow-hidden"
                 style={{ background: 'conic-gradient(from 357deg at 82% 63%, rgba(55,49,42,1) 49%, rgba(25,24,23,1) 100%)' }}>

                {/* Sidebar */}
                <div className="bg-[#21201e] shadow-[2px_0px_90px_#6100c266] p-4 flex flex-col">
                    <div className="flex items-center gap-2 mb-10">
                        <img src={login} alt="Logo" className="w-[35px] h-[31px] object-cover" />
                        <div className="[font-family:'Poppins-Bold',Helvetica] text-[22px] text-white font-bold tracking-[1.32px]">
                            WATCH
                        </div>
                    </div>

                    <nav className="flex flex-col gap-10">
                        {[
                            { text: "Home", icon: film, path: "/home" },
                            { text: "Favourites", icon: heart },
                            { text: "Recommended", icon: trend, path: "/trending" },
                            { text: "Settings", icon: settings, path: "/profile" },
                            { text: "Log out", icon: logout, onClick: handleLogout },
                        ].map((item, index) => (
                            <a
                                key={index}
                                href={item.path}
                                onClick={item.onClick ? (e) => {
                                    e.preventDefault();
                                    item.onClick();
                                } : undefined}
                                className="flex items-center gap-3 text-base text-white font-normal hover:font-bold transition-all duration-200 cursor-pointer"
                            >
                                <img className="w-6 h-6" alt={`${item.text} icon`} src={item.icon} />
                                {item.text}
                            </a>
                        ))}
                    </nav>
                </div>

                {/* Main Content */}
                <div className="grid grid-rows-[auto_1fr] gap-6 p-8 overflow-auto">
                    {/* Header Section */}
                    <div className="grid grid-rows-[auto_auto] gap-4">
                        <div className="flex gap-10 text-base text-white [font-family:'Poppins-Medium',Helvetica] font-medium">
                            <div>Movies</div>
                            <div>Series</div>
                            <div>Documentaries</div>
                        </div>
                    </div>

                    {/* Trending Section */}
                    <div className="grid grid-rows-[auto_1fr] gap-4">
                        <ListTrendingFilm/>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Trending;