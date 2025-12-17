import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { useTheme } from '../ThemeContext';

function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, register } = useAuth();
  const { isDark } = useTheme();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        await login({ username: formData.username, password: formData.password });
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }
        if (formData.password.length < 6) {
          setError('Password must be at least 6 characters');
          setLoading(false);
          return;
        }
        await register({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          first_name: formData.first_name,
          last_name: formData.last_name
        });
      }
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      // Show more detailed error messages
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.message) {
        setError(err.message);
      } else if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
        setError('Cannot connect to server. Make sure the backend is running on http://localhost:5000');
      } else {
        setError('An error occurred. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const bgColor = isDark ? 'bg-slate-900' : 'bg-slate-50';
  const cardBg = isDark ? 'bg-slate-800' : 'bg-white';
  const textColor = isDark ? 'text-white' : 'text-slate-900';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const inputBg = isDark ? 'bg-slate-700 border-slate-600' : 'bg-white border-slate-300';
  const inputText = isDark ? 'text-white placeholder-slate-400' : 'text-slate-900 placeholder-slate-400';

  return (
    <div className={`min-h-screen ${bgColor} flex items-center justify-center p-4`}>
      <div className={`w-full max-w-md ${cardBg} rounded-2xl shadow-xl p-8`}>
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
          </div>
          <h1 className={`text-2xl font-bold ${textColor}`}>PhishVision</h1>
          <p className={`${textMuted} mt-1`}>
            {isLogin ? 'Sign in to your account' : 'Create a new account'}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-sm">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={`block text-sm font-medium ${textMuted} mb-1`}>First Name</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className={`w-full px-4 py-2.5 rounded-lg border ${inputBg} ${inputText} focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                  placeholder="John"
                />
              </div>
              <div>
                <label className={`block text-sm font-medium ${textMuted} mb-1`}>Last Name</label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className={`w-full px-4 py-2.5 rounded-lg border ${inputBg} ${inputText} focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                  placeholder="Doe"
                />
              </div>
            </div>
          )}

          <div>
            <label className={`block text-sm font-medium ${textMuted} mb-1`}>Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className={`w-full px-4 py-2.5 rounded-lg border ${inputBg} ${inputText} focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
              placeholder="Enter your username"
            />
          </div>

          {!isLogin && (
            <div>
              <label className={`block text-sm font-medium ${textMuted} mb-1`}>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className={`w-full px-4 py-2.5 rounded-lg border ${inputBg} ${inputText} focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                placeholder="john@example.com"
              />
            </div>
          )}

          <div>
            <label className={`block text-sm font-medium ${textMuted} mb-1`}>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className={`w-full px-4 py-2.5 rounded-lg border ${inputBg} ${inputText} focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
              placeholder="Enter your password"
            />
          </div>

          {!isLogin && (
            <div>
              <label className={`block text-sm font-medium ${textMuted} mb-1`}>Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className={`w-full px-4 py-2.5 rounded-lg border ${inputBg} ${inputText} focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                placeholder="Confirm your password"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        {/* Toggle */}
        <div className="mt-6 text-center">
          <p className={textMuted}>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
              }}
              className="text-blue-500 hover:text-blue-400 font-medium"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
