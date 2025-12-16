import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { useTheme } from '../ThemeContext';

function Header() {
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const { user, logout } = useAuth();
  const { isDark } = useTheme();
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const bgColor = isDark ? 'bg-surface-2' : 'bg-white';
  const borderColor = isDark ? 'border-white/5' : 'border-black/5';
  const textColor = isDark ? 'text-white' : 'text-slate-900';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';
  const hoverBg = isDark ? 'hover:bg-white/5' : 'hover:bg-black/5';
  const dropdownBg = isDark ? 'bg-surface-2' : 'bg-white';

  const displayName = user?.full_name || user?.username || 'User';
  const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  return (
    <header className={`h-16 min-h-[64px] ${bgColor} border-b ${borderColor} flex items-center justify-end px-6 flex-shrink-0`}>
      {/* User Menu */}
      <div className="relative h-full flex items-center" ref={dropdownRef}>
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className={`flex items-center gap-3 px-3 py-1.5 rounded-lg ${hoverBg} transition-colors duration-150`}
        >
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
            {initials}
          </div>
          <span className={`text-sm font-medium ${textColor} whitespace-nowrap`}>{displayName}</span>
          <svg
            className={`w-4 h-4 flex-shrink-0 transition-transform duration-150 ${textMuted} ${showDropdown ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Dropdown */}
        {showDropdown && (
          <div className={`absolute top-full right-0 mt-1 w-56 ${dropdownBg} rounded-lg shadow-lg border ${borderColor} py-1 z-50`}>
            <div className={`px-4 py-3 border-b ${borderColor}`}>
              <p className={`text-sm font-medium ${textColor}`}>{displayName}</p>
              <p className={`text-xs ${textMuted}`}>{user?.email}</p>
            </div>

            <div className="py-1">
              <button
                onClick={() => {
                  setShowDropdown(false);
                  navigate('/settings');
                }}
                className={`w-full flex items-center gap-3 px-4 py-2 text-sm ${textColor} ${hoverBg} transition-colors duration-150`}
              >
                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Account Settings
              </button>
            </div>

            <div className={`border-t ${borderColor} py-1`}>
              <button
                onClick={handleLogout}
                className={`w-full flex items-center gap-3 px-4 py-2 text-sm text-red-500 ${hoverBg} transition-colors duration-150`}
              >
                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Sign Out
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;
