import React, { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext';
import { getLandingPages, createLandingPage, deleteLandingPage, cloneWebsite, getRepeatOffenders, getUsersRequiringTraining } from '../api/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function LandingPagesManager() {
  const [pages, setPages] = useState([]);
  const [repeatOffenders, setRepeatOffenders] = useState({ users: [], total: 0 });
  const [trainingRequired, setTrainingRequired] = useState({ users: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showCloneModal, setShowCloneModal] = useState(false);
  const [activeTab, setActiveTab] = useState('pages');
  const { isDark } = useTheme();

  // Theme classes
  const cardBg = isDark ? 'bg-slate-800' : 'bg-white';
  const cardBorder = isDark ? 'border-slate-700' : 'border-slate-200';
  const textPrimary = isDark ? 'text-slate-50' : 'text-slate-900';
  const textSecondary = isDark ? 'text-slate-400' : 'text-slate-500';
  const inputBg = isDark ? 'bg-slate-700 border-slate-600' : 'bg-white border-slate-300';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [pagesRes, offendersRes, trainingRes] = await Promise.all([
        getLandingPages(),
        getRepeatOffenders(),
        getUsersRequiringTraining()
      ]);
      setPages(pagesRes.data);
      setRepeatOffenders(offendersRes.data);
      setTrainingRequired(trainingRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this landing page?')) {
      try {
        await deleteLandingPage(id);
        loadData();
      } catch (error) {
        console.error('Error deleting:', error);
      }
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className={`h-8 ${isDark ? 'bg-slate-700' : 'bg-slate-200'} rounded w-64`}></div>
          <div className={`h-64 ${isDark ? 'bg-slate-700' : 'bg-slate-200'} rounded`}></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-2xl font-bold ${textPrimary}`}>Credential Harvesting</h1>
          <p className={textSecondary}>Fake login pages for phishing simulations</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowCloneModal(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Clone Website
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Create Page
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Total Pages</p>
          <p className={`text-2xl font-bold ${textPrimary}`}>{pages.length}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Active Pages</p>
          <p className="text-2xl font-bold text-green-500">{pages.filter(p => p.is_active).length}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Repeat Offenders</p>
          <p className="text-2xl font-bold text-red-500">{repeatOffenders.total}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Need Training</p>
          <p className="text-2xl font-bold text-yellow-500">{trainingRequired.total}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-slate-700">
        {['pages', 'offenders', 'training'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 font-medium transition-colors ${
              activeTab === tab
                ? 'border-b-2 border-blue-500 text-blue-500'
                : textSecondary
            }`}
          >
            {tab === 'pages' ? 'Landing Pages' : tab === 'offenders' ? 'Repeat Offenders' : 'Training Required'}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'pages' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pages.map((page) => (
            <div key={page.id} className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
              <div className="flex justify-between items-start mb-3">
                <h3 className={`font-semibold ${textPrimary}`}>{page.name}</h3>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(page.difficulty)}`}>
                  {page.difficulty}
                </span>
              </div>
              <p className={`text-sm ${textSecondary} mb-3`}>{page.description || 'No description'}</p>
              <div className="flex items-center gap-2 mb-3">
                <span className={`px-2 py-1 rounded text-xs ${isDark ? 'bg-slate-700' : 'bg-slate-100'} ${textSecondary}`}>
                  {page.category}
                </span>
                <span className={`px-2 py-1 rounded text-xs ${page.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                  {page.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="flex gap-2">
                <a
                  href={`${API_BASE_URL}/api/landing/preview/${page.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 text-center px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
                >
                  Preview
                </a>
                <button
                  onClick={() => handleDelete(page.id)}
                  className="px-3 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
          {pages.length === 0 && (
            <div className={`col-span-3 text-center py-12 ${textSecondary}`}>
              No landing pages yet. Create one to get started!
            </div>
          )}
        </div>
      )}

      {activeTab === 'offenders' && (
        <div className={`${cardBg} rounded-xl border ${cardBorder} overflow-hidden`}>
          <table className="w-full">
            <thead className={isDark ? 'bg-slate-700' : 'bg-slate-50'}>
              <tr>
                <th className={`px-4 py-3 text-left ${textSecondary}`}>Email</th>
                <th className={`px-4 py-3 text-left ${textSecondary}`}>Department</th>
                <th className={`px-4 py-3 text-left ${textSecondary}`}>Click Count</th>
                <th className={`px-4 py-3 text-left ${textSecondary}`}>Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {repeatOffenders.users?.map((user) => (
                <tr key={user.id} className={`border-t ${cardBorder}`}>
                  <td className={`px-4 py-3 ${textPrimary}`}>{user.email}</td>
                  <td className={`px-4 py-3 ${textSecondary}`}>{user.department}</td>
                  <td className={`px-4 py-3 ${textPrimary}`}>{user.campaigns_clicked}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      user.risk_level === 'critical' ? 'bg-red-100 text-red-800' :
                      user.risk_level === 'high' ? 'bg-orange-100 text-orange-800' :
                      user.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {user.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
              {(!repeatOffenders.users || repeatOffenders.users.length === 0) && (
                <tr>
                  <td colSpan="4" className={`px-4 py-8 text-center ${textSecondary}`}>
                    No repeat offenders found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'training' && (
        <div className={`${cardBg} rounded-xl border ${cardBorder} overflow-hidden`}>
          <table className="w-full">
            <thead className={isDark ? 'bg-slate-700' : 'bg-slate-50'}>
              <tr>
                <th className={`px-4 py-3 text-left ${textSecondary}`}>Email</th>
                <th className={`px-4 py-3 text-left ${textSecondary}`}>Department</th>
                <th className={`px-4 py-3 text-left ${textSecondary}`}>Risk Score</th>
                <th className={`px-4 py-3 text-left ${textSecondary}`}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {trainingRequired.users?.map((user) => (
                <tr key={user.id} className={`border-t ${cardBorder}`}>
                  <td className={`px-4 py-3 ${textPrimary}`}>{user.email}</td>
                  <td className={`px-4 py-3 ${textSecondary}`}>{user.department}</td>
                  <td className={`px-4 py-3 ${textPrimary}`}>{user.risk_score?.toFixed(1)}</td>
                  <td className="px-4 py-3">
                    <button className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                      Assign Training
                    </button>
                  </td>
                </tr>
              ))}
              {(!trainingRequired.users || trainingRequired.users.length === 0) && (
                <tr>
                  <td colSpan="4" className={`px-4 py-8 text-center ${textSecondary}`}>
                    No users require training
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreatePageModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => { setShowCreateModal(false); loadData(); }}
          isDark={isDark}
        />
      )}

      {/* Clone Modal */}
      {showCloneModal && (
        <CloneWebsiteModal
          onClose={() => setShowCloneModal(false)}
          onSuccess={() => { setShowCloneModal(false); loadData(); }}
          isDark={isDark}
        />
      )}
    </div>
  );
}

function CreatePageModal({ onClose, onSuccess, isDark }) {
  const [formData, setFormData] = useState({
    name: '',
    category: 'corporate',
    description: '',
    difficulty: 'medium',
    html_content: '',
    redirect_url: '/api/landing/training'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createLandingPage(formData);
      onSuccess();
    } catch (error) {
      console.error('Error creating page:', error);
      alert('Failed to create page');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = isDark
    ? 'w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white'
    : 'w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className={`${isDark ? 'bg-slate-800' : 'bg-white'} rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto`}>
        <h2 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>Create Landing Page</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className={inputClass}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className={inputClass}
              >
                <option value="corporate">Corporate</option>
                <option value="banking">Banking</option>
                <option value="social">Social Media</option>
                <option value="ecommerce">E-Commerce</option>
                <option value="government">Government</option>
              </select>
            </div>
            <div>
              <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Difficulty</label>
              <select
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                className={inputClass}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          </div>
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className={inputClass}
              rows="2"
            />
          </div>
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>HTML Content</label>
            <textarea
              value={formData.html_content}
              onChange={(e) => setFormData({ ...formData, html_content: e.target.value })}
              className={`${inputClass} font-mono text-sm`}
              rows="10"
              placeholder="Paste your HTML login page content here..."
              required
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-slate-600 text-white rounded-lg">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
              {loading ? 'Creating...' : 'Create Page'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function CloneWebsiteModal({ onClose, onSuccess, isDark }) {
  const [url, setUrl] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await cloneWebsite({ url, name });
      onSuccess();
    } catch (error) {
      console.error('Error cloning:', error);
      alert('Failed to clone website');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = isDark
    ? 'w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white'
    : 'w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className={`${isDark ? 'bg-slate-800' : 'bg-white'} rounded-xl p-6 w-full max-w-md`}>
        <h2 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>Clone Website</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Website URL</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className={inputClass}
              placeholder="https://example.com/login"
              required
            />
          </div>
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Page Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={inputClass}
              placeholder="Cloned Login Page"
              required
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-slate-600 text-white rounded-lg">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="px-4 py-2 bg-purple-600 text-white rounded-lg">
              {loading ? 'Cloning...' : 'Clone Website'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default LandingPagesManager;
