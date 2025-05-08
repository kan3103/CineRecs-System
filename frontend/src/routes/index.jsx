import Login from "../pages/LoginPage/Login.jsx"
import HomePage from "../pages/Home/HomePage.jsx"
import Trending from "../pages/TrendPage/Trending.jsx"
import ProfilePage from "../pages/SettingPage/Profile.jsx"
import Favorite from "../pages/FavorPage/Favourite.jsx"


const routes = [
    {
        path: '/home',
        component: HomePage,
        // protected: false,
    },
    {
        path: '/trending',
        component: Trending,
        // protected: true,
        // allowedRoles: ['admin'],
    },
    {
        path: '/favorites',
        component: Favorite,
        // protected: true,
        // allowedRoles: ['staff'],
    },
    {
        path: '/',
        component: Login,
        // layout: false,
        // layoutStaff: false,
        // protected: false,
    },
    {
        path: '/add-member',
        // component: AddMember,
        // protected: false,
        // allowedRoles: ['admin'],
    },
    {
        path: '/profile',
        component: ProfilePage,
        // protected: true,
        // allowedRoles: ['admin'],
    },
    {
        path: '/profile-staff',
        // component: ProfileStaff,
        protected: true,
        allowedRoles: ['staff'],
    },
    {
        path: '/print-history',
        // component: History,
        protected: true,
        allowedRoles: ['admin'],
    },
    {
        path: '/print-history-staff',
        // component: PrintHistoryStaff,
        protected: true,
        allowedRoles: ['staff'],
    },
    {
        path : '/sign-in',
        // component: SignInPage,
    },
];

export default routes;
