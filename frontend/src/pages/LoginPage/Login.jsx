import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion'; // Import Framer Motion để thêm animation
import login from "../../assets/images/login.png";
import login1 from "../../assets/images/login1.png";
import LoginForm from "../../components/LoginForm";

export const Login = () => {
    const [showLoginForm, setShowLoginForm] = React.useState(false);
    const navigate = useNavigate();

    return (
        <div className="flex justify-center items-center h-screen w-full relative">
            {/* Background Image */}
            <div
                className="absolute inset-0 bg-cover bg-center opacity-70"
                style={{ backgroundImage: `url(${login1})` }}
            ></div>

            {/* Overlay */}
            <div className="absolute inset-0 bg-gradient-to-b from-black/50 to-black/90"></div>

            {/* Content */}
            <div className="relative z-10 text-white text-center p-8 bg-black bg-opacity-60 rounded-lg shadow-lg w-80">
                {/* Logo */}
                <img src={login} alt="Logo" className="relative w-[35px] h-[31px] top-3 left-[55px] object-cover" />

                {/* Title */}
                <div className="relative top-[-20px] left-3 text-[22px] font-bold [font-family: 'Poppins-Medium',Helvetica] whitespace-nowrap tracking-[1.32px]">WATCH</div>
                <p className="text-sm text-gray-300 [font-family: 'Poppins-Regular',Helvetica]">Enjoy the newest movies</p>

                {/* Login Button */}
                <button
                    className="mt-6 bg-[#6100c2] hover:bg-[#5000a3] text-white font-semibold py-2 px-6 rounded-lg w-full"
                    onClick={() => setShowLoginForm(true)}
                >
                    Log in
                </button>

                {/* Sign Up Link */}
                <p className="mt-4 text-sm">
                    No account? <span className="font-bold underline cursor-pointer">Sign up</span>
                </p>
            </div>

            {/* Fullscreen LoginForm */}
            {showLoginForm && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                    className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-80 backdrop-blur-sm z-50"
                >
                    <LoginForm />
                </motion.div>
            )}
        </div>
    );
};

export default Login;
