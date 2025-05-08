import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

// Configure axios base URL
axios.defaults.baseURL = 'http://localhost:5623';

const LoginForm = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loginSuccess, setLoginSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoginSuccess('');
        setLoading(true);

        try {
            const response = await axios.post('/api/users/login', {
                username,
                password
            });

            // Save the user data and token in localStorage
            localStorage.setItem('user', JSON.stringify({
                id: response.data.id,
                name: response.data.name,
                username: response.data.username,
                token: response.data.token
            }));

            // Show success message
            setLoginSuccess('Sign in successfully');
            
            // Redirect to home page after a short delay to show the message
            setTimeout(() => {
                navigate('/home');
            }, 1500);
        } catch (err) {
            console.error('Login error:', err);
            setError(err.response?.data?.detail || 'Incorrect username or password');
        } finally {
            setLoading(false);
        }
    };

    // Toggle to show signup form
    const [showSignUp, setShowSignUp] = useState(false);
    const [newUser, setNewUser] = useState({
        name: '',
        username: '',
        password: '',
        date_of_birth: ''
    });
    const [signUpError, setSignUpError] = useState('');
    const [signUpSuccess, setSignUpSuccess] = useState('');

    const handleSignUpSubmit = async (e) => {
        e.preventDefault();
        setSignUpError('');
        setSignUpSuccess('');
        setLoading(true);

        try {
            // Check if username exists - Fixed API call format to match backend expectations
            const checkResponse = await axios.post('/api/users/check-username', {
                username: newUser.username
            });

            if (checkResponse.data.exists) {
                setSignUpError('Username already exists');
                setLoading(false);
                return;
            }

            // Create new user
            await axios.post('/api/users/', {
                name: newUser.name,
                username: newUser.username,
                password: newUser.password,
                date_of_birth: newUser.date_of_birth
            });

            setSignUpSuccess('Registration successful!');
            
            // Clear form and switch back to login after a delay
            setTimeout(() => {
                setShowSignUp(false);
                setSignUpSuccess('');
                setNewUser({
                    name: '',
                    username: '',
                    password: '',
                    date_of_birth: ''
                });
                // Redirect to the login page at root path
                navigate('/');
            }, 2000);
        } catch (err) {
            console.error('Registration error:', err);
            setSignUpError(err.response?.data?.detail || 'Error creating account');
        } finally {
            setLoading(false);
        }
    };

    return (
        <StyledWrapper>
            {!showSignUp ? (
                <div className="form-container">
                    <p className="title">Login</p>
                    {error && <div className="error-message">{error}</div>}
                    {loginSuccess && <div className="success-message">{loginSuccess}</div>}
                    <form className="form" onSubmit={handleSubmit}>
                        <div className="input-group">
                            <label htmlFor="username">Username</label>
                            <input 
                                type="text" 
                                name="username" 
                                id="username" 
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="password">Password</label>
                            <input 
                                type="password" 
                                name="password" 
                                id="password" 
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <div className="forgot">
                                <a rel="noopener noreferrer" href="#">Forgot Password ?</a>
                            </div>
                        </div>
                        <button 
                            className="sign" 
                            type="submit" 
                            disabled={loading}
                        >
                            {loading ? 'Loading...' : 'Log in'}
                        </button>
                    </form>
                    <div className="social-message">
                        <div className="line" />
                        <p className="message">Login with social accounts</p>
                        <div className="line" />
                    </div>
                    <div className="social-icons">
                        <button aria-label="Log in with Google" className="icon">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" className="w-5 h-5 fill-current">
                                <path d="M16.318 13.714v5.484h9.078c-0.37 2.354-2.745 6.901-9.078 6.901-5.458 0-9.917-4.521-9.917-10.099s4.458-10.099 9.917-10.099c3.109 0 5.193 1.318 6.38 2.464l4.339-4.182c-2.786-2.599-6.396-4.182-10.719-4.182-8.844 0-16 7.151-16 16s7.156 16 16 16c9.234 0 15.365-6.49 15.365-15.635 0-1.052-0.115-1.854-0.255-2.651z" />
                            </svg>
                        </button>
                    </div>
                    <p className="signup">Don't have an account?
                        <a 
                            onClick={() => setShowSignUp(true)} 
                            href="#" 
                            className="signup-link"
                        > Sign up</a>
                    </p>
                </div>
            ) : (
                <div className="form-container">
                    <p className="title">Sign Up</p>
                    {signUpError && <div className="error-message">{signUpError}</div>}
                    {signUpSuccess && <div className="success-message">{signUpSuccess}</div>}
                    <form className="form" onSubmit={handleSignUpSubmit}>
                        <div className="input-group">
                            <label htmlFor="name">Full Name</label>
                            <input 
                                type="text" 
                                name="name" 
                                id="name" 
                                value={newUser.name}
                                onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="signupUsername">Username</label>
                            <input 
                                type="text" 
                                name="signupUsername" 
                                id="signupUsername" 
                                value={newUser.username}
                                onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="signupPassword">Password</label>
                            <input 
                                type="password" 
                                name="signupPassword" 
                                id="signupPassword" 
                                value={newUser.password}
                                onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                                required
                            />
                        </div>
                        <div className="input-group">
                            <label htmlFor="dob">Date of Birth</label>
                            <input 
                                type="date" 
                                name="dob" 
                                id="dob" 
                                value={newUser.date_of_birth}
                                onChange={(e) => setNewUser({...newUser, date_of_birth: e.target.value})}
                                required
                            />
                        </div>
                        <button 
                            className="sign" 
                            type="submit" 
                            disabled={loading}
                        >
                            {loading ? 'Creating Account...' : 'Sign Up'}
                        </button>
                    </form>
                    <p className="signup">Already have an account?
                        <a 
                            onClick={() => setShowSignUp(false)} 
                            href="#" 
                            className="signup-link"
                        > Log in</a>
                    </p>
                </div>
            )}
        </StyledWrapper>
    );
};

const StyledWrapper = styled.div`
  .form-container {
    width: 320px;
    border-radius: 0.75rem;
    background-color: rgba(17, 24, 39, 1);
    padding: 2rem;
    color: rgba(243, 244, 246, 1);
  }

  .title {
    text-align: center;
    font-size: 1.5rem;
    line-height: 2rem;
    font-weight: 700;
  }

  .form {
    margin-top: 1.5rem;
  }

  .input-group {
    margin-top: 0.25rem;
    font-size: 0.875rem;
    line-height: 1.25rem;
  }

  .input-group label {
    display: block;
    color: rgba(156, 163, 175, 1);
    margin-bottom: 4px;
  }

  .input-group input {
    width: 100%;
    border-radius: 0.375rem;
    border: 1px solid rgba(55, 65, 81, 1);
    outline: 0;
    background-color: rgba(17, 24, 39, 1);
    padding: 0.75rem 1rem;
    color: rgba(243, 244, 246, 1);
  }

  .input-group input:focus {
    border-color: rgba(167, 139, 250);
  }

  .forgot {
    display: flex;
    justify-content: flex-end;
    font-size: 0.75rem;
    line-height: 1rem;
    color: rgba(156, 163, 175,1);
    margin: 8px 0 14px 0;
  }

  .forgot a,.signup a {
    color: rgba(243, 244, 246, 1);
    text-decoration: none;
    font-size: 14px;
  }

  .forgot a:hover, .signup a:hover {
    text-decoration: underline rgba(167, 139, 250, 1);
  }

  .sign {
    display: block;
    width: 100%;
    background-color: rgba(167, 139, 250, 1);
    padding: 0.75rem;
    text-align: center;
    color: rgba(17, 24, 39, 1);
    border: none;
    border-radius: 0.375rem;
    font-weight: 600;
    cursor: pointer;
  }

  .sign:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .social-message {
    display: flex;
    align-items: center;
    padding-top: 1rem;
  }

  .line {
    height: 1px;
    flex: 1 1 0%;
    background-color: rgba(55, 65, 81, 1);
  }

  .social-message .message {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
    font-size: 0.875rem;
    line-height: 1.25rem;
    color: rgba(156, 163, 175, 1);
  }

  .social-icons {
    display: flex;
    justify-content: center;
  }

  .social-icons .icon {
    border-radius: 0.125rem;
    padding: 0.75rem;
    border: none;
    background-color: transparent;
    margin-left: 8px;
    cursor: pointer;
  }

  .social-icons .icon svg {
    height: 1.25rem;
    width: 1.25rem;
    fill: #fff;
  }

  .signup {
    text-align: center;
    font-size: 0.75rem;
    line-height: 1rem;
    color: rgba(156, 163, 175, 1);
  }
  
  .signup-link {
    cursor: pointer;
  }
  
  .error-message {
    color: #ff6b6b;
    text-align: center;
    margin-top: 0.5rem;
    font-size: 0.875rem;
  }
  
  .success-message {
    color: #66bb6a;
    text-align: center;
    margin-top: 0.5rem;
    font-size: 0.875rem;
  }
`;

export default LoginForm;
