import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../ThemeContext';
import { getTemplates } from '../api/api';

// Custom hook for scroll-triggered animations
function useInView(threshold = 0.1) {
  const ref = useRef(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold]);

  return [ref, isInView];
}

function LandingPage() {
  const { isDark, toggleTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [templatesLoading, setTemplatesLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Section refs for scroll animations
  const [featuresRef, featuresInView] = useInView(0.1);
  const [howItWorksRef, howItWorksInView] = useInView(0.1);
  const [templatesRef, templatesInView] = useInView(0.1);
  const [whyChooseRef, whyChooseInView] = useInView(0.1);
  const [pricingRef, pricingInView] = useInView(0.1);
  const [ctaRef, ctaInView] = useInView(0.1);

  useEffect(() => {
    setMounted(true);
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await getTemplates();
      setTemplates(response.data.slice(0, 6));
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setTemplatesLoading(false);
    }
  };

  // Integration logos for the slider
  const integrations = [
    'Microsoft 365', 'Google Workspace', 'Slack', 'Okta', 'Splunk',
    'ServiceNow', 'Jira', 'AWS', 'Azure AD', 'CrowdStrike'
  ];

  // Feature cards with colored badges (puq.ai style)
  const featureCards = [
    {
      badge: { text: 'NO-CODE', color: 'blue' },
      title: 'Visual Campaign Builder',
      description: 'Create sophisticated phishing simulations without writing a single line of code. Drag-and-drop interface for rapid deployment.',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
        </svg>
      ),
    },
    {
      badge: { text: 'AI-POWERED', color: 'purple' },
      title: 'Intelligent Threat Detection',
      description: 'Advanced NLP models analyze emails in real-time to detect phishing attempts and classify threat severity automatically.',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
    },
    {
      badge: { text: 'REAL-TIME', color: 'green' },
      title: 'Live Analytics Dashboard',
      description: 'Monitor email opens, link clicks, and credential submissions as they happen with real-time metrics and alerts.',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
  ];

  // How it works steps
  const steps = [
    {
      number: '01',
      title: 'Select Templates',
      description: 'Choose from our library of pre-built phishing templates or create custom ones tailored to your organization.',
    },
    {
      number: '02',
      title: 'Configure Campaign',
      description: 'Set target groups, schedule delivery, and customize tracking parameters for your simulation.',
    },
    {
      number: '03',
      title: 'Launch & Monitor',
      description: 'Deploy your campaign and watch real-time analytics as employees interact with the simulation.',
    },
    {
      number: '04',
      title: 'Analyze & Improve',
      description: 'Review comprehensive reports, identify at-risk users, and strengthen your security posture.',
    },
  ];

  // Feature grid (8 features)
  const featureGrid = [
    { title: 'Campaign Management', desc: 'Create and deploy phishing simulations' },
    { title: 'AI Analysis', desc: 'NLP-powered threat detection' },
    { title: 'SOC Timeline', desc: 'Track incidents with MTTD/MTTR' },
    { title: 'Risk Scoring', desc: 'Identify high-risk users' },
    { title: 'Multi-Channel', desc: 'Email, SMS, and QR attacks' },
    { title: 'Real-Time Tracking', desc: 'Live campaign monitoring' },
    { title: 'Custom Templates', desc: 'Build your own scenarios' },
    { title: 'Detailed Reports', desc: 'Comprehensive analytics' },
  ];

  // Why choose us benefits
  const benefits = [
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: 'Fast Deployment',
      description: 'Launch your first campaign in minutes, not days.',
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
        </svg>
      ),
      title: 'Enterprise Security',
      description: 'SOC 2 compliant with end-to-end encryption.',
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      title: 'Team Collaboration',
      description: 'Multi-user access with role-based permissions.',
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      ),
      title: 'Automated Workflows',
      description: 'Set it and forget it with scheduled campaigns.',
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
      ),
      title: 'Seamless Integrations',
      description: 'Connect with your existing security stack.',
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
      title: '24/7 Support',
      description: 'Expert help whenever you need it.',
    },
  ];

  // Pricing plans
  const pricingPlans = [
    {
      name: 'Starter',
      price: 'Free',
      period: '',
      description: 'Perfect for trying out PhishVision',
      features: [
        '3 campaigns per month',
        '5 phishing templates',
        'Basic email analytics',
        'Community support',
      ],
      cta: 'Get Started',
      ctaLink: '/dashboard',
      highlighted: false,
    },
    {
      name: 'Professional',
      price: '$29',
      period: '/month',
      description: 'For growing security teams',
      features: [
        'Unlimited campaigns',
        '50+ phishing templates',
        'AI-powered analysis',
        'SOC timeline integration',
        'User risk scoring',
        'Priority support',
      ],
      cta: 'Start Free Trial',
      ctaLink: '/dashboard',
      highlighted: true,
      badge: 'Most Popular',
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      description: 'For large organizations',
      features: [
        'Everything in Professional',
        'SSO/SAML authentication',
        'Custom integrations',
        'Dedicated account manager',
        'Custom SLA',
        'On-premise deployment',
      ],
      cta: 'Contact Sales',
      ctaLink: '/dashboard',
      highlighted: false,
    },
  ];

  const navLinks = [
    { name: 'Features', href: '#features' },
    { name: 'How It Works', href: '#how-it-works' },
    { name: 'Templates', href: '#templates' },
    { name: 'Pricing', href: '#pricing' },
  ];

  const getBadgeColors = (color) => {
    const colors = {
      blue: isDark ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 'bg-blue-50 text-blue-600 border-blue-200',
      purple: isDark ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' : 'bg-purple-50 text-purple-600 border-purple-200',
      green: isDark ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-green-50 text-green-600 border-green-200',
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className={`min-h-screen ${isDark ? 'bg-surface-1' : 'bg-white'}`}>
      {/* Navigation */}
      <nav className={`sticky top-0 z-50 border-b backdrop-blur-lg ${
        isDark
          ? 'bg-surface-1/90 border-white/10'
          : 'bg-white/90 border-gray-200'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-xl ${isDark ? 'bg-primary/10' : 'bg-primary-50'}`}>
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                </svg>
              </div>
              <span className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Phish<span className="text-primary">Vision</span>
              </span>
            </div>

            {/* Desktop Nav Links */}
            <div className="hidden md:flex items-center space-x-8">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  className={`text-sm font-medium transition-colors ${
                    isDark
                      ? 'text-gray-300 hover:text-white'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {link.name}
                </a>
              ))}
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-3">
              <button
                onClick={toggleTheme}
                className={`p-2 rounded-lg transition-colors ${
                  isDark
                    ? 'hover:bg-white/10 text-gray-400 hover:text-white'
                    : 'hover:bg-gray-100 text-gray-600 hover:text-gray-900'
                }`}
              >
                {isDark ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className={`md:hidden p-2 rounded-lg ${
                  isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100'
                }`}
              >
                <svg className={`w-5 h-5 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={mobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
                </svg>
              </button>

              <Link
                to="/dashboard"
                className="hidden sm:inline-flex items-center px-4 py-2 rounded-lg bg-primary text-white font-medium text-sm hover:bg-primary-600 transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>

          {/* Mobile menu */}
          {mobileMenuOpen && (
            <div className={`md:hidden py-4 border-t ${isDark ? 'border-white/10' : 'border-gray-200'}`}>
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  className={`block py-2 text-sm font-medium ${
                    isDark ? 'text-gray-300' : 'text-gray-600'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.name}
                </a>
              ))}
              <Link
                to="/dashboard"
                className="block mt-3 px-4 py-2 rounded-lg bg-primary text-white font-medium text-sm text-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className={`relative overflow-hidden ${isDark ? 'bg-surface-1' : 'bg-gradient-to-b from-primary-50/30 to-white'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20 md:pt-24 md:pb-28">
          <div className={`text-center max-w-4xl mx-auto ${mounted ? 'animate-fade-in-up' : 'opacity-0'}`}>
            {/* Badge */}
            <div className="inline-flex items-center mb-6">
              <span className={`px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase ${
                isDark
                  ? 'bg-primary/10 text-primary border border-primary/20'
                  : 'bg-primary-50 text-primary-600 border border-primary-200'
              }`}>
                Security Training Platform
              </span>
            </div>

            {/* Headline */}
            <h1 className={`text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Train Your Team.<br />
              <span className="text-primary">Stop Phishing.</span>
            </h1>

            {/* Subheadline */}
            <p className={`text-lg md:text-xl mb-10 max-w-2xl mx-auto ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              AI-powered phishing simulation platform for Red Teams and SOC analysts. Run campaigns, test defenses, and train your organization.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/dashboard"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-primary text-white font-semibold hover:bg-primary-600 transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-primary/25"
              >
                Start Free Trial
              </Link>
              <Link
                to="/analyzer"
                className={`w-full sm:w-auto px-8 py-3.5 rounded-xl font-semibold transition-all hover:scale-[1.02] active:scale-[0.98] ${
                  isDark
                    ? 'bg-white/10 text-white hover:bg-white/20 border border-white/10'
                    : 'bg-white text-gray-900 hover:bg-gray-50 border border-gray-200 shadow-sm'
                }`}
              >
                Try Email Analyzer
              </Link>
            </div>

            {/* Hero Visual - Dashboard Mockup */}
            <div className={`mt-16 p-1 rounded-2xl ${isDark ? 'bg-gradient-to-r from-primary/20 via-accent/20 to-primary/20' : 'bg-gradient-to-r from-primary/10 via-accent/10 to-primary/10'}`}>
              <div className={`rounded-xl overflow-hidden ${isDark ? 'bg-surface-2' : 'bg-white'} shadow-2xl`}>
                {/* Browser Header */}
                <div className={`h-10 flex items-center px-4 gap-2 ${isDark ? 'bg-surface-3 border-b border-white/5' : 'bg-gray-100 border-b border-gray-200'}`}>
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                  </div>
                  <div className={`flex-1 mx-4 h-6 rounded-md ${isDark ? 'bg-surface-4' : 'bg-white'} flex items-center px-3`}>
                    <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>phishvision.app/dashboard</span>
                  </div>
                </div>

                {/* Dashboard Content */}
                <div className="p-6">
                  {/* Top Stats Row */}
                  <div className="grid grid-cols-4 gap-4 mb-6">
                    {[
                      { label: 'Active Campaigns', value: '12', change: '+3', color: 'primary' },
                      { label: 'Emails Sent', value: '2,847', change: '+156', color: 'primary' },
                      { label: 'Click Rate', value: '24.3%', change: '-2.1%', color: 'warning' },
                      { label: 'Risk Score', value: '67', change: '+5', color: 'danger' },
                    ].map((stat, i) => (
                      <div key={i} className={`p-4 rounded-xl ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                        <p className={`text-xs mb-1 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{stat.label}</p>
                        <div className="flex items-end justify-between">
                          <span className={`text-xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>{stat.value}</span>
                          <span className={`text-xs font-medium ${
                            stat.color === 'primary' ? 'text-primary' :
                            stat.color === 'warning' ? 'text-warning' : 'text-danger'
                          }`}>{stat.change}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Main Content Grid */}
                  <div className="grid grid-cols-3 gap-4">
                    {/* Chart Area */}
                    <div className={`col-span-2 p-4 rounded-xl ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                      <div className="flex items-center justify-between mb-4">
                        <span className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>Campaign Performance</span>
                        <div className="flex gap-2">
                          <span className={`px-2 py-1 rounded text-xs ${isDark ? 'bg-surface-4 text-gray-400' : 'bg-white text-gray-500'}`}>7 Days</span>
                          <span className={`px-2 py-1 rounded text-xs ${isDark ? 'bg-primary/20 text-primary' : 'bg-primary-50 text-primary-600'}`}>30 Days</span>
                        </div>
                      </div>
                      {/* Fake Chart Bars */}
                      <div className="flex items-end gap-2 h-32">
                        {[40, 65, 45, 80, 55, 70, 90, 60, 75, 85, 50, 95].map((h, i) => (
                          <div key={i} className="flex-1 flex flex-col justify-end">
                            <div
                              className={`rounded-t ${i === 11 ? 'bg-primary' : isDark ? 'bg-surface-4' : 'bg-gray-300'}`}
                              style={{ height: `${h}%` }}
                            />
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Recent Activity */}
                    <div className={`p-4 rounded-xl ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                      <span className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>Recent Activity</span>
                      <div className="mt-4 space-y-3">
                        {[
                          { action: 'Email opened', user: 'john@company.com', time: '2m ago', icon: 'eye', color: 'primary' },
                          { action: 'Link clicked', user: 'sarah@company.com', time: '5m ago', icon: 'click', color: 'warning' },
                          { action: 'Credentials entered', user: 'mike@company.com', time: '12m ago', icon: 'alert', color: 'danger' },
                        ].map((activity, i) => (
                          <div key={i} className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                              activity.color === 'primary' ? (isDark ? 'bg-primary/20 text-primary' : 'bg-primary-50 text-primary') :
                              activity.color === 'warning' ? (isDark ? 'bg-warning/20 text-warning' : 'bg-yellow-50 text-yellow-600') :
                              (isDark ? 'bg-danger/20 text-danger' : 'bg-red-50 text-red-600')
                            }`}>
                              {activity.icon === 'eye' && (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                              )}
                              {activity.icon === 'click' && (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                                </svg>
                              )}
                              {activity.icon === 'alert' && (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className={`text-xs font-medium truncate ${isDark ? 'text-white' : 'text-gray-900'}`}>{activity.action}</p>
                              <p className={`text-xs truncate ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{activity.user}</p>
                            </div>
                            <span className={`text-xs ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>{activity.time}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Bottom Row - Campaign List */}
                  <div className={`mt-4 p-4 rounded-xl ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                    <div className="flex items-center justify-between mb-3">
                      <span className={`text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>Active Campaigns</span>
                      <span className={`text-xs text-primary cursor-pointer hover:underline`}>View All</span>
                    </div>
                    <div className="space-y-2">
                      {[
                        { name: 'Q4 Security Awareness', status: 'Active', sent: 450, clicked: 89 },
                        { name: 'IT Department Test', status: 'Active', sent: 120, clicked: 23 },
                        { name: 'New Employee Onboarding', status: 'Scheduled', sent: 0, clicked: 0 },
                      ].map((campaign, i) => (
                        <div key={i} className={`flex items-center gap-4 p-3 rounded-lg ${isDark ? 'bg-surface-2' : 'bg-white'}`}>
                          <div className={`w-2 h-2 rounded-full ${campaign.status === 'Active' ? 'bg-success' : 'bg-warning'}`} />
                          <span className={`flex-1 text-sm font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>{campaign.name}</span>
                          <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{campaign.sent} sent</span>
                          <span className={`text-xs font-medium ${campaign.clicked > 0 ? 'text-warning' : isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                            {campaign.clicked > 0 ? `${campaign.clicked} clicks` : '--'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Logo Slider */}
      <section className={`py-12 border-y ${isDark ? 'bg-surface-2/50 border-white/5' : 'bg-gray-50 border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className={`text-center text-sm font-medium mb-8 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
            INTEGRATES WITH YOUR SECURITY STACK
          </p>
          <div className="relative overflow-hidden">
            <div className="logo-slider flex gap-12 items-center">
              {[...integrations, ...integrations].map((name, index) => (
                <div
                  key={index}
                  className={`flex-shrink-0 px-6 py-3 rounded-lg font-medium ${
                    isDark ? 'text-gray-400 bg-surface-3' : 'text-gray-500 bg-white shadow-sm'
                  }`}
                >
                  {name}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards Section */}
      <section id="features" className={`py-20 md:py-28 ${isDark ? 'bg-surface-1' : 'bg-white'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div
            ref={featuresRef}
            className={`text-center mb-16 ${featuresInView ? 'animate-on-scroll in-view' : 'animate-on-scroll'}`}
          >
            <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase mb-4 ${
              isDark ? 'bg-primary/10 text-primary' : 'bg-primary-50 text-primary-600'
            }`}>
              FEATURES
            </span>
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Everything You Need for Security Training
            </h2>
            <p className={`text-lg max-w-2xl mx-auto ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Built for enterprise security teams, researchers, and organizations of all sizes.
            </p>
          </div>

          {/* Feature Cards with Colored Badges */}
          <div className={`grid grid-cols-1 md:grid-cols-3 gap-8 stagger-children ${featuresInView ? 'in-view' : ''}`}>
            {featureCards.map((feature, index) => (
              <div
                key={index}
                className={`animate-on-scroll ${featuresInView ? 'in-view' : ''} p-8 rounded-2xl transition-all duration-300 hover:-translate-y-1 ${
                  isDark
                    ? 'bg-surface-2 border border-white/5 hover:border-white/10 hover:shadow-lg'
                    : 'bg-white border border-gray-200 hover:border-gray-300 shadow-sm hover:shadow-xl'
                }`}
                style={{ transitionDelay: `${index * 100}ms` }}
              >
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold tracking-wide border mb-4 ${getBadgeColors(feature.badge.color)}`}>
                  {feature.badge.text}
                </span>
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${
                  isDark ? 'bg-primary/10 text-primary' : 'bg-primary-50 text-primary'
                }`}>
                  {feature.icon}
                </div>
                <h3 className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  {feature.title}
                </h3>
                <p className={`leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className={`py-20 md:py-28 ${isDark ? 'bg-surface-2/50' : 'bg-gray-50'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            {/* Left - Steps */}
            <div
              ref={howItWorksRef}
              className={`${howItWorksInView ? 'animate-on-scroll in-view' : 'animate-on-scroll'}`}
            >
              <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase mb-4 ${
                isDark ? 'bg-primary/10 text-primary' : 'bg-primary-50 text-primary-600'
              }`}>
                HOW IT WORKS
              </span>
              <h2 className={`text-3xl md:text-4xl font-bold mb-12 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                Get Started in Minutes
              </h2>

              <div className="space-y-8">
                {steps.map((step, index) => (
                  <div
                    key={index}
                    className={`flex gap-6 animate-on-scroll ${howItWorksInView ? 'in-view' : ''}`}
                    style={{ transitionDelay: `${index * 100}ms` }}
                  >
                    <div className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center font-mono font-bold ${
                      isDark
                        ? 'bg-primary/10 text-primary border border-primary/20'
                        : 'bg-primary-50 text-primary-600 border border-primary-200'
                    }`}>
                      {step.number}
                    </div>
                    <div>
                      <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                        {step.title}
                      </h3>
                      <p className={`${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                        {step.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right - Dashboard Mockup */}
            <div className={`rounded-2xl overflow-hidden ${isDark ? 'bg-surface-2 border border-white/5' : 'bg-white border border-gray-200 shadow-2xl'}`}>
              {/* Browser Header */}
              <div className={`h-10 flex items-center px-4 gap-2 ${isDark ? 'bg-surface-3 border-b border-white/5' : 'bg-gray-100 border-b border-gray-200'}`}>
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <div className={`flex-1 mx-4 h-6 rounded-md ${isDark ? 'bg-surface-4' : 'bg-white'} flex items-center px-3`}>
                  <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>phishvision.app/campaign/new</span>
                </div>
              </div>

              {/* Dashboard Content */}
              <div className="p-6">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h4 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>New Campaign</h4>
                    <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Step 1 of 4</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${isDark ? 'bg-primary/10 text-primary' : 'bg-primary-50 text-primary-600'}`}>
                    Draft
                  </div>
                </div>

                {/* Progress Bar */}
                <div className={`h-2 rounded-full mb-6 ${isDark ? 'bg-surface-4' : 'bg-gray-200'}`}>
                  <div className="h-full w-1/4 rounded-full bg-primary" />
                </div>

                {/* Template Selection */}
                <div className="space-y-3 mb-6">
                  <p className={`text-xs font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Select Template</p>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { name: 'Microsoft 365', selected: true },
                      { name: 'Google Workspace', selected: false },
                      { name: 'Slack Alert', selected: false },
                      { name: 'Custom', selected: false },
                    ].map((template, i) => (
                      <div
                        key={i}
                        className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
                          template.selected
                            ? 'border-primary bg-primary/5'
                            : isDark
                              ? 'border-white/10 hover:border-white/20'
                              : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                            template.selected
                              ? 'bg-primary/20 text-primary'
                              : isDark ? 'bg-surface-4 text-gray-500' : 'bg-gray-100 text-gray-400'
                          }`}>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                          </div>
                          <span className={`text-xs font-medium ${isDark ? 'text-white' : 'text-gray-900'}`}>{template.name}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Stats Preview */}
                <div className={`p-4 rounded-xl ${isDark ? 'bg-surface-3' : 'bg-gray-50'}`}>
                  <div className="flex items-center justify-between mb-3">
                    <span className={`text-xs font-medium ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>Campaign Preview</span>
                    <span className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>50 targets</span>
                  </div>
                  <div className="flex gap-4">
                    <div className="text-center">
                      <div className="text-lg font-bold text-primary">85%</div>
                      <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Est. Open</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-warning">32%</div>
                      <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Est. Click</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-danger">12%</div>
                      <div className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Est. Submit</div>
                    </div>
                  </div>
                </div>

                {/* Action Button */}
                <button className="w-full mt-4 py-2.5 rounded-lg bg-primary text-white text-sm font-medium hover:bg-primary-600 transition-colors">
                  Continue to Targets
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Grid Section */}
      <section className={`py-20 md:py-28 ${isDark ? 'bg-surface-1' : 'bg-white'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Comprehensive Security Platform
            </h2>
            <p className={`text-lg max-w-2xl mx-auto ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              All the tools you need to run effective phishing simulations.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {featureGrid.map((feature, index) => (
              <div
                key={index}
                className={`p-6 rounded-xl text-center transition-all duration-300 hover:-translate-y-1 ${
                  isDark
                    ? 'bg-surface-2 border border-white/5 hover:border-primary/20'
                    : 'bg-white border border-gray-200 hover:border-primary/30 shadow-sm hover:shadow-lg'
                }`}
              >
                <h4 className={`font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  {feature.title}
                </h4>
                <p className={`text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Templates Section */}
      <section id="templates" className={`py-20 md:py-28 ${isDark ? 'bg-surface-2/50' : 'bg-gray-50'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div
            ref={templatesRef}
            className={`text-center mb-16 ${templatesInView ? 'animate-on-scroll in-view' : 'animate-on-scroll'}`}
          >
            <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase mb-4 ${
              isDark ? 'bg-primary/10 text-primary' : 'bg-primary-50 text-primary-600'
            }`}>
              TEMPLATES
            </span>
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Ready-to-Use Phishing Templates
            </h2>
            <p className={`text-lg max-w-2xl mx-auto ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Start with professionally crafted templates across multiple categories and difficulty levels.
            </p>
          </div>

          {templatesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className={`h-44 rounded-2xl animate-pulse ${isDark ? 'bg-surface-3' : 'bg-gray-200'}`} />
              ))}
            </div>
          ) : templates.length > 0 ? (
            <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 stagger-children ${templatesInView ? 'in-view' : ''}`}>
              {templates.map((template, index) => (
                <TemplateCard
                  key={template.id}
                  template={template}
                  isDark={isDark}
                  index={index}
                  inView={templatesInView}
                />
              ))}
            </div>
          ) : (
            <div className={`text-center py-12 rounded-2xl ${isDark ? 'bg-surface-2' : 'bg-white'}`}>
              <p className={isDark ? 'text-gray-400' : 'text-gray-600'}>No templates available</p>
            </div>
          )}

          <div className="text-center mt-10">
            <Link
              to="/templates"
              className={`inline-flex items-center px-6 py-3 rounded-xl font-medium transition-colors ${
                isDark
                  ? 'bg-white/10 text-white hover:bg-white/20'
                  : 'bg-white text-gray-900 hover:bg-gray-50 border border-gray-200 shadow-sm'
              }`}
            >
              View all templates
              <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section className={`py-20 md:py-28 ${isDark ? 'bg-surface-1' : 'bg-white'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div
            ref={whyChooseRef}
            className={`text-center mb-16 ${whyChooseInView ? 'animate-on-scroll in-view' : 'animate-on-scroll'}`}
          >
            <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase mb-4 ${
              isDark ? 'bg-primary/10 text-primary' : 'bg-primary-50 text-primary-600'
            }`}>
              WHY CHOOSE US
            </span>
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Built for Security Teams
            </h2>
            <p className={`text-lg max-w-2xl mx-auto ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              PhishVision is designed with the needs of modern security operations in mind.
            </p>
          </div>

          <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 stagger-children ${whyChooseInView ? 'in-view' : ''}`}>
            {benefits.map((benefit, index) => (
              <div
                key={index}
                className={`animate-on-scroll ${whyChooseInView ? 'in-view' : ''} flex gap-4 p-6 rounded-xl transition-all duration-300 ${
                  isDark
                    ? 'bg-surface-2/50 hover:bg-surface-2'
                    : 'bg-gray-50 hover:bg-white hover:shadow-lg'
                }`}
                style={{ transitionDelay: `${index * 100}ms` }}
              >
                <div className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center ${
                  isDark ? 'bg-primary/10 text-primary' : 'bg-primary-50 text-primary'
                }`}>
                  {benefit.icon}
                </div>
                <div>
                  <h3 className={`font-semibold mb-1 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                    {benefit.title}
                  </h3>
                  <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                    {benefit.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className={`py-20 md:py-28 ${isDark ? 'bg-surface-2/50' : 'bg-gray-50'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div
            ref={pricingRef}
            className={`text-center mb-16 ${pricingInView ? 'animate-on-scroll in-view' : 'animate-on-scroll'}`}
          >
            <span className={`inline-block px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase mb-4 ${
              isDark ? 'bg-primary/10 text-primary' : 'bg-primary-50 text-primary-600'
            }`}>
              PRICING
            </span>
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Simple, Transparent Pricing
            </h2>
            <p className={`text-lg max-w-2xl mx-auto ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Choose the plan that best fits your organization's needs.
            </p>
          </div>

          <div className={`grid grid-cols-1 md:grid-cols-3 gap-8 items-start stagger-children ${pricingInView ? 'in-view' : ''}`}>
            {pricingPlans.map((plan, index) => (
              <PricingCard
                key={plan.name}
                plan={plan}
                isDark={isDark}
                index={index}
                inView={pricingInView}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section
        ref={ctaRef}
        className={`py-20 md:py-28 ${isDark ? 'bg-surface-1' : 'bg-white'}`}
      >
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`${ctaInView ? 'animate-on-scroll in-view' : 'animate-on-scroll'} text-center p-12 md:p-16 rounded-3xl ${
            isDark
              ? 'bg-gradient-to-br from-primary/20 via-surface-2 to-accent/20 border border-white/10'
              : 'bg-gradient-to-br from-primary-50 via-white to-accent/10 border border-gray-200 shadow-2xl'
          }`}>
            <h2 className={`text-3xl md:text-4xl font-bold mb-6 ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Ready to Strengthen Your Security?
            </h2>
            <p className={`text-lg mb-10 max-w-xl mx-auto ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Start running phishing simulations and protect your organization from real threats today.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/dashboard"
                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-primary text-white font-semibold hover:bg-primary-600 transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-primary/25"
              >
                Start Free Trial
              </Link>
              <Link
                to="/analyzer"
                className={`w-full sm:w-auto px-8 py-4 rounded-xl font-semibold transition-all hover:scale-[1.02] ${
                  isDark
                    ? 'bg-white/10 text-white hover:bg-white/20'
                    : 'bg-white text-gray-900 hover:bg-gray-50 border border-gray-200'
                }`}
              >
                Try Email Analyzer
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={`py-16 border-t ${isDark ? 'bg-surface-2/50 border-white/5' : 'bg-gray-50 border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            {/* Brand */}
            <div className="md:col-span-1">
              <div className="flex items-center space-x-3 mb-4">
                <div className={`p-2 rounded-xl ${isDark ? 'bg-primary/10' : 'bg-primary-50'}`}>
                  <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                  </svg>
                </div>
                <span className={`text-lg font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  PhishVision
                </span>
              </div>
              <p className={`text-sm mb-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                AI-powered phishing simulation platform for modern security teams.
              </p>
              <a
                href="https://github.com/adilaxmdv/phishvision"
                target="_blank"
                rel="noopener noreferrer"
                className={`inline-flex items-center gap-2 text-sm ${isDark ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-900'}`}
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
                View on GitHub
              </a>
            </div>

            {/* Product Links */}
            <div>
              <h4 className={`font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>Product</h4>
              <ul className="space-y-3">
                {[
                  { name: 'Dashboard', path: '/dashboard' },
                  { name: 'Campaigns', path: '/campaigns' },
                  { name: 'Templates', path: '/templates' },
                  { name: 'Analyzer', path: '/analyzer' },
                ].map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.path}
                      className={`text-sm transition-colors ${isDark ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-900'}`}
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Features Links */}
            <div>
              <h4 className={`font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>Features</h4>
              <ul className="space-y-3">
                {[
                  'AI Analysis',
                  'SOC Timeline',
                  'Risk Scoring',
                  'Multi-Channel',
                ].map((feature) => (
                  <li key={feature}>
                    <a
                      href="#features"
                      className={`text-sm transition-colors ${isDark ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-900'}`}
                    >
                      {feature}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Company Links */}
            <div>
              <h4 className={`font-semibold mb-4 ${isDark ? 'text-white' : 'text-gray-900'}`}>Resources</h4>
              <ul className="space-y-3">
                {[
                  { name: 'SOC Timeline', path: '/soc' },
                  { name: 'Risk Report', path: '/risk-report' },
                  { name: 'Settings', path: '/settings' },
                ].map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.path}
                      className={`text-sm transition-colors ${isDark ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-900'}`}
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Bottom */}
          <div className={`mt-12 pt-8 border-t ${isDark ? 'border-white/5' : 'border-gray-200'}`}>
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <p className={`text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                Hackathon Project 2024. Built with React, Flask & AI.
              </p>
              <div className="flex items-center gap-6">
                <span className={`text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                  Made with passion by the PhishVision team
                </span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Template Card Component
function TemplateCard({ template, isDark, index, inView }) {
  const difficultyColors = {
    easy: isDark ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-green-50 text-green-700 border-green-200',
    medium: isDark ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' : 'bg-yellow-50 text-yellow-700 border-yellow-200',
    hard: isDark ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-red-50 text-red-700 border-red-200',
  };

  const categoryColors = isDark
    ? 'bg-primary/10 text-primary border-primary/20'
    : 'bg-primary-50 text-primary-600 border-primary-200';

  return (
    <div
      className={`animate-on-scroll ${inView ? 'in-view' : ''} p-6 rounded-2xl transition-all duration-300 hover:-translate-y-1 ${
        isDark
          ? 'bg-surface-2 border border-white/5 hover:border-white/10 hover:shadow-lg'
          : 'bg-white border border-gray-200 hover:border-gray-300 shadow-sm hover:shadow-xl'
      }`}
      style={{ transitionDelay: `${index * 100}ms` }}
    >
      <div className="flex items-center gap-2 mb-3 flex-wrap">
        <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${categoryColors}`}>
          {template.category}
        </span>
        <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${difficultyColors[template.difficulty] || difficultyColors.medium}`}>
          {template.difficulty}
        </span>
      </div>
      <h3 className={`font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
        {template.name}
      </h3>
      <p className={`text-sm line-clamp-2 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
        {template.description || template.subject}
      </p>
    </div>
  );
}

// Pricing Card Component
function PricingCard({ plan, isDark, index, inView }) {
  const isHighlighted = plan.highlighted;

  return (
    <div
      className={`animate-on-scroll ${inView ? 'in-view' : ''} relative rounded-2xl p-8 transition-all duration-300 ${
        isHighlighted
          ? `border-2 border-primary ${isDark ? 'bg-surface-2' : 'bg-white'} shadow-xl md:scale-105`
          : `border ${isDark ? 'bg-surface-2 border-white/10' : 'bg-white border-gray-200'} shadow-sm`
      }`}
      style={{ transitionDelay: `${index * 100}ms` }}
    >
      {plan.badge && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-primary text-white text-xs font-semibold rounded-full whitespace-nowrap">
          {plan.badge}
        </span>
      )}

      <div className="text-center mb-6">
        <h3 className={`text-xl font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
          {plan.name}
        </h3>
        <div className="flex items-baseline justify-center gap-1">
          <span className={`text-4xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
            {plan.price}
          </span>
          <span className={`${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
            {plan.period}
          </span>
        </div>
        <p className={`mt-2 text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
          {plan.description}
        </p>
      </div>

      <ul className="space-y-3 mb-8">
        {plan.features.map((feature, idx) => (
          <li key={idx} className="flex items-start gap-3">
            <svg className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
              {feature}
            </span>
          </li>
        ))}
      </ul>

      <Link
        to={plan.ctaLink}
        className={`block w-full py-3 px-4 rounded-xl text-center font-semibold transition-all duration-300 hover:scale-[1.02] ${
          isHighlighted
            ? 'bg-primary text-white hover:bg-primary-600 shadow-lg shadow-primary/25'
            : isDark
              ? 'bg-white/10 text-white hover:bg-white/20'
              : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
        }`}
      >
        {plan.cta}
      </Link>
    </div>
  );
}

export default LandingPage;
