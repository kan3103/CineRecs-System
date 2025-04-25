import React from "react";
import login from "../../assets/images/login.png";
import trend from "../../assets/images/Home/trend.png";
import heart from "../../assets/images/Home/heart.png";
import film from "../../assets/images/Home/film.png";
import settings from "../../assets/images/Home/setting.png";
import logout from "../../assets/images/Home/logout.png";
import test from "../../assets/images/Home/test.png";
import test1 from "../../assets/images/Home/test1.png";
import Favourite from "../../components/Favourite";
import TrendingCard from "./component/TrendingHome";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";


export const HomePage = () => {
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
                            { text: "Trending", icon: trend, path: "/trending" },
                            { text: "Settings", icon: settings },
                            { text: "Log out", icon: logout },
                        ].map((item, index) => (
                            <a
                                key={index}
                                href={item.path}
                                className="flex items-center gap-3 text-base text-white font-normal hover:font-bold transition-all duration-200"
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

                        <div
                            className="flex flex-col justify-center gap-4 bg-cover bg-center h-[455px] px-10"
                            style={{ backgroundImage: `url(${test})` }}
                        >

                        <div className="[font-family: 'Poppins-SemiBold',Helvetica] text-[32px] text-white leading-[48px] font-semibold whitespace-nowrap tracking-[0]">
                                Harry Potter
                            </div>
                            <div className="text-white leading-5 font-normal text-sm whitespace-nowrap tracking-[0]">
                                2004 | Mystery | 3 Seasons
                            </div>
                            <div className="flex items-center gap-4">
                                <button className="px-6 py-[17px] bg-[#6100c2] rounded-[14px] [font-family:'Poppins-Medium',Helvetica] text-base text-white font-medium tracking-[0.25px]">
                                    Watch now
                                </button>
                                <div className="p-[15px] rounded-[14px] backdrop-brightness-[100%] [webkit-backdrop-filter:blur(10px)_brightness(100%)]">
                                    <Favourite />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Trending Section */}
                    <div className="grid grid-rows-[auto_1fr] gap-4">
                        <TrendingCard/>
                    </div>
                </div>
            </div>
            <ToastContainer position="top-right" autoClose={2000} />
        </div>
    );
};

export default HomePage;