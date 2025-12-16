import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { ThemeProvider, useTheme } from './ThemeContext';
import { AuthProvider, useAuth } from './AuthContext';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import LandingPage from './components/LandingPage';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import CampaignManager from './components/CampaignManager';
import EmailAnalyzer from './components/EmailAnalyzer';
import CampaignDetails from './components/CampaignDetails';
import TemplateManager from './components/TemplateManager';
import UserRiskDashboard from './components/UserRiskDashboard';
import EmployeeManager from './components/EmployeeManager';
import LandingPagesManager from './components/LandingPagesManager';
import QRPhishing from './components/QRPhishing';
import SMSPhishing from './components/SMSPhishing';
import Settings from './components/Settings';
import ApiDocs from './components/ApiDocs';
import UserGuide from './components/UserGuide';
import ThreatFeed from './components/ThreatFeed';
import ThreatDetail from './components/ThreatDetail';
import VulnerabilityDashboard from './components/VulnerabilityDashboard';
import ProfilingProgramManager from './components/ProfilingProgramManager';
import CampaignReport from './components/CampaignReport';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function AppLayout() {
  const location = useLocation();
  const { isDark } = useTheme();
  const { user, loading } = useAuth();

  // Don't show sidebar on landing page, login page, or threat intel pages (semi-public)
  const isPublicPage = location.pathname === '/' || location.pathname === '/login';
  const isThreatPage = location.pathname.startsWith('/threats');

  const bgColor = isDark ? 'bg-slate-900' : 'bg-slate-50';

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${bgColor}`}>
        <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (isPublicPage) {
    return (
      <div className={`min-h-screen ${bgColor}`}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Login />} />
        </Routes>
      </div>
    );
  }

  // Threat Intel pages - semi-public (work with or without login)
  if (isThreatPage) {
    if (user) {
      // Logged in - show with sidebar
      return (
        <div className={`h-screen flex ${bgColor}`}>
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-auto">
              <Routes>
                <Route path="/threats" element={<ThreatFeed />} />
                <Route path="/threats/:shortId" element={<ThreatDetail />} />
              </Routes>
            </main>
          </div>
        </div>
      );
    } else {
      // Not logged in - show without sidebar
      return (
        <div className={`min-h-screen ${bgColor}`}>
          <Routes>
            <Route path="/threats" element={<ThreatFeed />} />
            <Route path="/threats/:shortId" element={<ThreatDetail />} />
          </Routes>
        </div>
      );
    }
  }

  return (
    <ProtectedRoute>
      <div className={`h-screen flex ${bgColor}`}>
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/employees" element={<EmployeeManager />} />
              <Route path="/campaigns" element={<CampaignManager />} />
              <Route path="/campaigns/:id" element={<CampaignDetails />} />
              <Route path="/campaigns/:id/report" element={<CampaignReport />} />
              <Route path="/templates" element={<TemplateManager />} />
              <Route path="/landing-pages" element={<LandingPagesManager />} />
              <Route path="/qr-phishing" element={<QRPhishing />} />
              <Route path="/sms-phishing" element={<SMSPhishing />} />
              <Route path="/analyzer" element={<EmailAnalyzer />} />
              <Route path="/risk" element={<UserRiskDashboard />} />
              <Route path="/profiling/dashboard" element={<VulnerabilityDashboard />} />
              <Route path="/profiling/programs" element={<ProfilingProgramManager />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/api-docs" element={<ApiDocs />} />
              <Route path="/user-guide" element={<UserGuide />} />
              <Route path="/threats" element={<ThreatFeed />} />
              <Route path="/threats/:shortId" element={<ThreatDetail />} />
            </Routes>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <AppLayout />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
