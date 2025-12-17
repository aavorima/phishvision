import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../ThemeContext';

// Icons as simple SVG components
const Icons = {
  Dashboard: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  ),
  Campaigns: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
  Email: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
  Templates: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
    </svg>
  ),
  Analyzer: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
  SOC: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  Risk: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
  Landing: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
    </svg>
  ),
  QRCode: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
    </svg>
  ),
  SMS: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
    </svg>
  ),
  Employees: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  ),
  Analytics: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
  Shield: () => (
    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
    </svg>
  ),
  Collapse: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
    </svg>
  ),
  Expand: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
    </svg>
  ),
  Sun: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  ),
  Moon: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
    </svg>
  ),
  ChevronDown: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  ),
  ChevronRight: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  ),
  Search: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  ),
  ThreatIntel: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  ),
  Profiling: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
    </svg>
  ),
  VulnDashboard: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  ),
  Program: () => (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  ),
  Book: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  ),
  Code: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
  ),
  Settings: () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  ),
};

// Navigation structure with groups
const navStructure = [
  { type: 'item', path: '/dashboard', label: 'Dashboard', icon: 'Dashboard' },
  { type: 'item', path: '/employees', label: 'Employees', icon: 'Employees' },
  {
    type: 'group',
    label: 'Campaigns',
    icon: 'Campaigns',
    children: [
      { path: '/campaigns', label: 'Email Campaigns', icon: 'Email' },
      { path: '/qr-phishing', label: 'QR Phishing', icon: 'QRCode' },
      { path: '/sms-phishing', label: 'SMS Phishing', icon: 'SMS' },
      { path: '/landing-pages', label: 'Credential Harvest', icon: 'Landing' },
    ]
  },
  { type: 'item', path: '/templates', label: 'Templates', icon: 'Templates' },
  {
    type: 'group',
    label: 'Profiling',
    icon: 'Profiling',
    children: [
      { path: '/profiling/programs', label: 'Profiling Programs', icon: 'Program' },
      { path: '/profiling/dashboard', label: 'Vulnerability Dashboard', icon: 'VulnDashboard' },
    ]
  },
  {
    type: 'group',
    label: 'Analytics',
    icon: 'Analytics',
    children: [
      { path: '/analyzer', label: 'Email Analyzer', icon: 'Search' },
      { path: '/threats', label: 'Threat Intel', icon: 'ThreatIntel' },
      { path: '/risk', label: 'User Risk', icon: 'Risk' },
    ]
  },
  { type: 'divider' },
  { type: 'item', path: '/api-docs', label: 'API Documentation', icon: 'Code' },
  { type: 'item', path: '/user-guide', label: 'User Guide', icon: 'Book' },
];

function Sidebar() {
  const location = useLocation();
  const { isDark, toggleTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState(['Campaigns', 'Profiling', 'Analytics']);

  const isActive = (path) => {
    if (path === '/campaigns') {
      return location.pathname === '/campaigns' || location.pathname.startsWith('/campaigns/');
    }
    return location.pathname === path;
  };

  const isGroupActive = (children) => {
    return children.some(child => isActive(child.path));
  };

  const toggleGroup = (groupLabel) => {
    if (collapsed) return;
    setExpandedGroups(prev =>
      prev.includes(groupLabel)
        ? prev.filter(g => g !== groupLabel)
        : [...prev, groupLabel]
    );
  };

  const renderNavItem = (item, isSubItem = false) => {
    const Icon = Icons[item.icon];
    const active = isActive(item.path);

    return (
      <Link
        key={item.path}
        to={item.path}
        className={`group relative flex items-center px-3 py-2.5 rounded-xl transition-all duration-200 ${
          active
            ? isDark
              ? 'bg-primary/10 text-primary'
              : 'bg-primary/10 text-primary-dim'
            : isDark
              ? 'text-white/50 hover:text-white hover:bg-white/5'
              : 'text-surface-1/50 hover:text-surface-1 hover:bg-black/5'
        } ${collapsed ? 'justify-center' : ''} ${isSubItem && !collapsed ? 'ml-3' : ''}`}
        title={collapsed ? item.label : ''}
      >
        {/* Active Indicator */}
        {active && (
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-primary rounded-r-full" />
        )}

        <div className={`flex-shrink-0 ${active ? 'text-primary' : ''}`}>
          <Icon />
        </div>

        {!collapsed && (
          <span className={`ml-3 font-medium text-sm truncate ${active ? 'text-primary' : ''}`}>
            {item.label}
          </span>
        )}

        {/* Hover Glow Effect */}
        {active && (
          <div className="absolute inset-0 rounded-xl bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity" />
        )}
      </Link>
    );
  };

  const renderNavGroup = (group) => {
    const Icon = Icons[group.icon];
    const isExpanded = expandedGroups.includes(group.label);
    const groupActive = isGroupActive(group.children);

    return (
      <div key={group.label} className="space-y-1">
        {/* Group Header */}
        <button
          onClick={() => toggleGroup(group.label)}
          className={`w-full flex items-center px-3 py-2.5 rounded-xl transition-all duration-200 ${
            groupActive
              ? isDark
                ? 'text-primary'
                : 'text-primary-dim'
              : isDark
                ? 'text-white/50 hover:text-white hover:bg-white/5'
                : 'text-surface-1/50 hover:text-surface-1 hover:bg-black/5'
          } ${collapsed ? 'justify-center' : ''}`}
          title={collapsed ? group.label : ''}
        >
          <div className={`flex-shrink-0 ${groupActive ? 'text-primary' : ''}`}>
            <Icon />
          </div>

          {!collapsed && (
            <>
              <span className={`ml-3 font-medium text-sm ${groupActive ? 'text-primary' : ''}`}>
                {group.label}
              </span>
              <div className={`ml-auto transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
                <Icons.ChevronDown />
              </div>
            </>
          )}
        </button>

        {/* Group Children */}
        {!collapsed && isExpanded && (
          <div className={`relative ml-4 pl-3 border-l ${isDark ? 'border-white/10' : 'border-black/10'} space-y-1`}>
            {/* Animated connector */}
            <div className="absolute left-0 top-0 bottom-0 w-px">
              <div className="h-full w-full bg-gradient-to-b from-primary/50 via-primary/20 to-transparent" />
            </div>
            {group.children.map(child => renderNavItem(child, true))}
          </div>
        )}

        {/* Collapsed Mode Popup */}
        {collapsed && (
          <div className="relative group/menu">
            {/* Hover popup could be implemented here */}
          </div>
        )}
      </div>
    );
  };

  return (
    <aside
      className={`${
        isDark ? 'bg-surface-2 border-white/5' : 'bg-white border-black/5'
      } border-r flex flex-col transition-all duration-300 h-screen sticky top-0 ${
        collapsed ? 'w-[72px]' : 'w-64'
      }`}
    >
      {/* Logo */}
      <div className={`h-16 flex items-center ${collapsed ? 'justify-center px-2' : 'px-4'} border-b ${isDark ? 'border-white/5' : 'border-black/5'}`}>
        <Link to="/" className="flex items-center group">
          <div className={`relative p-2 rounded-xl transition-all duration-300 ${
            isDark ? 'bg-primary/10' : 'bg-primary/5'
          } group-hover:scale-105`}>
            <div className="text-primary">
              <Icons.Shield />
            </div>
            {/* Glow effect */}
            <div className="absolute inset-0 rounded-xl bg-primary/20 blur-lg opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          {!collapsed && (
            <span className={`ml-3 text-lg font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-1'}`}>
              Phish<span className="text-primary">Vision</span>
            </span>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto min-h-0 scrollbar-thin">
        {navStructure.map((item, index) => {
          if (item.type === 'divider') {
            return (
              <div
                key={index}
                className={`my-4 border-t ${isDark ? 'border-white/5' : 'border-black/5'}`}
              />
            );
          }
          if (item.type === 'group') {
            return renderNavGroup(item);
          }
          return renderNavItem(item);
        })}
      </nav>

      {/* Bottom Section */}
      <div className={`p-3 border-t ${isDark ? 'border-white/5' : 'border-black/5'} space-y-1 flex-shrink-0`}>
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className={`w-full flex items-center px-3 py-2.5 rounded-xl transition-all duration-200 ${
            isDark
              ? 'text-white/50 hover:text-white hover:bg-white/5'
              : 'text-surface-1/50 hover:text-surface-1 hover:bg-black/5'
          } ${collapsed ? 'justify-center' : ''}`}
          title={collapsed ? (isDark ? 'Light Mode' : 'Dark Mode') : ''}
        >
          <div className="relative">
            {isDark ? <Icons.Sun /> : <Icons.Moon />}
            {/* Animated glow for theme toggle */}
            <div className={`absolute inset-0 rounded-full blur-md opacity-0 hover:opacity-50 transition-opacity ${
              isDark ? 'bg-warning' : 'bg-primary'
            }`} />
          </div>
          {!collapsed && (
            <span className="ml-3 font-medium text-sm">
              {isDark ? 'Light Mode' : 'Dark Mode'}
            </span>
          )}
        </button>

        {/* Collapse Toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={`w-full flex items-center px-3 py-2.5 rounded-xl transition-all duration-200 ${
            isDark
              ? 'text-white/50 hover:text-white hover:bg-white/5'
              : 'text-surface-1/50 hover:text-surface-1 hover:bg-black/5'
          } ${collapsed ? 'justify-center' : ''}`}
          title={collapsed ? 'Expand' : 'Collapse'}
        >
          <div className={`transition-transform duration-300 ${collapsed ? 'rotate-180' : ''}`}>
            <Icons.Collapse />
          </div>
          {!collapsed && (
            <span className="ml-3 font-medium text-sm">Collapse</span>
          )}
        </button>
      </div>

      {/* Version Badge */}
      {!collapsed && (
        <div className={`px-4 py-3 border-t ${isDark ? 'border-white/5' : 'border-black/5'}`}>
          <div className={`px-3 py-2 rounded-lg text-center ${
            isDark ? 'bg-surface-3/50' : 'bg-surface-light-3'
          }`}>
            <span className={`text-xs font-mono ${isDark ? 'text-white/30' : 'text-surface-1/30'}`}>
              v1.0.0 | Command Center
            </span>
          </div>
        </div>
      )}
    </aside>
  );
}

export default Sidebar;
