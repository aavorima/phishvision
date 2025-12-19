import React, { useState, useEffect, useCallback } from 'react';
import api from '../api/api';
import { useTheme } from '../ThemeContext';
import TemplateEditor from './TemplateEditor';

function TemplateManager() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreator, setShowCreator] = useState(false);
  const [showEditor, setShowEditor] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [filter, setFilter] = useState('all');
  const [showAll, setShowAll] = useState(false);
  const { isDark } = useTheme();

  const INITIAL_DISPLAY_COUNT = 9;
  const categories = ['all', 'Banking', 'Delivery', 'E-commerce', 'Social Media', 'Business', 'IT', 'HR', 'Finance', 'Crypto', 'General'];

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await api.getTemplates();
      // Sort templates: newest first (by created_at descending)
      const sortedTemplates = response.data.sort((a, b) => {
        return new Date(b.created_at) - new Date(a.created_at);
      });
      setTemplates(sortedTemplates);
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this template?')) {
      try {
        await api.deleteTemplate(id);
        loadTemplates();
      } catch (error) {
        console.error('Error deleting template:', error);
        alert(error.response?.data?.error || 'Failed to delete template');
      }
    }
  };

  const handleDuplicate = async (template) => {
    try {
      await api.duplicateTemplate(template.id, { name: `${template.name} (Copy)` });
      loadTemplates();
    } catch (error) {
      console.error('Error duplicating template:', error);
      alert('Failed to duplicate template');
    }
  };

  const handleEdit = (template) => {
    setEditingTemplate(template);
    setShowEditor(true);
  };

  const allFilteredTemplates = filter === 'all'
    ? templates
    : templates.filter(t => t.category === filter);

  const filteredTemplates = showAll
    ? allFilteredTemplates
    : allFilteredTemplates.slice(0, INITIAL_DISPLAY_COUNT);

  const hasMore = allFilteredTemplates.length > INITIAL_DISPLAY_COUNT;
  const remainingCount = allFilteredTemplates.length - INITIAL_DISPLAY_COUNT;

  const builtInCount = templates.filter(t => t.is_builtin).length;
  const customCount = templates.filter(t => !t.is_builtin).length;

  const bgColor = isDark ? 'bg-gray-900' : 'bg-gray-50';
  const cardBg = isDark ? 'bg-gray-800' : 'bg-white';
  const cardBorder = isDark ? 'border-gray-700' : 'border-gray-200';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-600';
  const textTertiary = isDark ? 'text-gray-500' : 'text-gray-500';

  if (showCreator) {
    return <TemplateCreator onClose={() => {setShowCreator(false); loadTemplates();}} isDark={isDark} />;
  }

  if (showEditor) {
    return (
      <TemplateEditor
        template={editingTemplate}
        onClose={() => {setShowEditor(false); setEditingTemplate(null);}}
        onSave={() => {setShowEditor(false); setEditingTemplate(null); loadTemplates();}}
        isDark={isDark}
      />
    );
  }

  return (
    <div className={'min-h-screen p-6 ' + bgColor}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className={'text-2xl font-semibold ' + textPrimary}>Template Library</h1>
            <p className={'text-sm mt-1 ' + textSecondary}>All templates stored in database</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {setEditingTemplate(null); setShowEditor(true);}}
              className={(isDark ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-300') + ' px-4 py-2 rounded-lg font-medium transition text-sm'}
            >
              Create Template
            </button>
            <button
              onClick={() => setShowCreator(true)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition text-sm"
            >
              Create with AI
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-2 overflow-x-auto pb-2">
        {categories.map(cat => {
          const count = cat === 'all'
            ? templates.length
            : templates.filter(t => t.category === cat).length;

          if (count === 0 && cat !== 'all') return null;

          return (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={
                'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition ' +
                (filter === cat
                  ? 'bg-indigo-600 text-white'
                  : (isDark ? 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700' : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'))
              }
            >
              {cat === 'all' ? 'All' : cat} ({count})
            </button>
          );
        })}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className={'rounded-lg shadow-sm p-5 border ' + cardBg + ' ' + cardBorder}>
          <div className={'text-xs font-medium uppercase tracking-wide mb-2 ' + textSecondary}>Total Templates</div>
          <div className={'text-3xl font-semibold ' + textPrimary}>{templates.length}</div>
        </div>
        <div className={'rounded-lg shadow-sm p-5 border ' + cardBg + ' ' + cardBorder}>
          <div className={'text-xs font-medium uppercase tracking-wide mb-2 ' + textSecondary}>Built-in</div>
          <div className={'text-3xl font-semibold text-indigo-600'}>{builtInCount}</div>
        </div>
        <div className={'rounded-lg shadow-sm p-5 border ' + cardBg + ' ' + cardBorder}>
          <div className={'text-xs font-medium uppercase tracking-wide mb-2 ' + textSecondary}>Custom</div>
          <div className={'text-3xl font-semibold text-green-600'}>{customCount}</div>
        </div>
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className={textPrimary}>Loading templates...</p>
        </div>
      ) : filteredTemplates.length === 0 ? (
        <div className={'rounded-lg shadow-sm p-12 text-center border ' + cardBg + ' ' + cardBorder}>
          <svg className={'w-16 h-16 mx-auto mb-4 ' + textTertiary} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className={'text-lg font-medium mb-2 ' + textPrimary}>No templates found</h3>
          <p className={textSecondary + ' text-sm mb-6'}>
            {templates.length === 0
              ? 'Run the seed script to load built-in templates'
              : 'Try a different filter or create a custom template'}
          </p>
          <button
            onClick={() => setShowEditor(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition text-sm"
          >
            Create Template
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onDelete={!template.is_builtin ? () => handleDelete(template.id) : null}
                onDuplicate={() => handleDuplicate(template)}
                onEdit={() => handleEdit(template)}
                onReload={loadTemplates}
                isDark={isDark}
              />
            ))}
          </div>

          {/* View All / Show Less Button */}
          {hasMore && (
            <div className="mt-8 text-center">
              <button
                onClick={() => setShowAll(!showAll)}
                className={(isDark
                  ? 'bg-gray-800 hover:bg-gray-700 text-white border-gray-700'
                  : 'bg-white hover:bg-gray-50 text-gray-700 border-gray-300'
                ) + ' px-8 py-3 rounded-lg font-medium transition border inline-flex items-center gap-2'}
              >
                {showAll ? (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                    </svg>
                    Show Less
                  </>
                ) : (
                  <>
                    View All Templates ({remainingCount} more)
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </>
                )}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function TemplateCard({ template, onDelete, onDuplicate, onEdit, onReload, isDark }) {
  const [showPreview, setShowPreview] = useState(false);

  const difficultyColors = {
    easy: isDark ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-green-100 text-green-800 border-green-300',
    medium: isDark ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' : 'bg-yellow-100 text-yellow-800 border-yellow-300',
    hard: isDark ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-red-100 text-red-800 border-red-300'
  };

  const cardBg = isDark ? 'bg-gray-800' : 'bg-white';
  const cardBorder = isDark ? 'border-gray-700 hover:border-gray-600' : 'border-gray-200 hover:border-gray-300';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-600';

  return (
    <>
      <div className={'rounded-lg shadow-sm overflow-hidden transition-all duration-300 border ' + cardBg + ' ' + cardBorder}>
        {/* Header */}
        <div className="p-5">
          <div className="flex items-start justify-between mb-3">
            <h3 className={'font-semibold text-base ' + textPrimary}>{template.name}</h3>
            <div className="flex gap-1">
              {template.is_builtin && (
                <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded">
                  Built-in
                </span>
              )}
              {!template.is_builtin && (
                <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded">
                  Custom
                </span>
              )}
              {template.language && (
                <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded">
                  {template.language}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 mb-4">
            <span className={'text-xs px-2 py-1 rounded font-medium border ' + (isDark ? 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30' : 'bg-indigo-100 text-indigo-800 border-indigo-300')}>
              {template.category}
            </span>
            <span className={'text-xs px-2 py-1 rounded font-medium border ' + difficultyColors[template.difficulty]}>
              {template.difficulty}
            </span>
          </div>

          <div className="mb-4">
            <p className={'text-xs font-medium mb-1 ' + textSecondary}>SUBJECT:</p>
            <p className={'text-sm line-clamp-2 ' + textPrimary}>{template.subject}</p>
          </div>

          {template.description && (
            <p className={'text-xs mb-4 ' + textSecondary}>{template.description}</p>
          )}

          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setShowPreview(true)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white py-1.5 px-4 rounded-lg transition font-medium text-xs"
            >
              Preview
            </button>
            <button
              onClick={onEdit}
              className={(isDark ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-700') + ' py-1.5 px-4 rounded-lg transition font-medium text-xs'}
            >
              Edit
            </button>
            <button
              onClick={onDuplicate}
              className={(isDark ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-700') + ' py-1.5 px-4 rounded-lg transition font-medium text-xs'}
            >
              Duplicate
            </button>
            {onDelete && (
              <button
                onClick={onDelete}
                className="bg-red-100 hover:bg-red-600 text-red-600 hover:text-white px-4 py-1.5 rounded-lg transition font-medium text-xs"
              >
                Delete
              </button>
            )}
          </div>
        </div>
      </div>

      {showPreview && (
        <TemplatePreviewModal
          template={template}
          onClose={() => setShowPreview(false)}
          onReload={onReload}
          isDark={isDark}
        />
      )}
    </>
  );
}

function TemplatePreviewModal({ template, onClose, onReload, isDark }) {
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadPreview = useCallback(async () => {
    try {
      const response = await api.previewTemplate(template.id, { email: 'john.doe@example.com' });
      setPreviewData(response.data);
    } catch (error) {
      console.error('Error loading preview:', error);
      // Fallback to template data directly
      setPreviewData({
        subject: template.subject,
        html_content: template.html_content
      });
    } finally {
      setLoading(false);
    }
  }, [template.id, template.subject, template.html_content]);

  useEffect(() => {
    loadPreview();
  }, [loadPreview]);

  const cardBg = isDark ? 'bg-gray-800' : 'bg-white';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-600';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className={'rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-xl ' + cardBg}>
        <div className={(isDark ? 'bg-gray-700' : 'bg-gray-100') + ' p-5 flex justify-between items-center border-b ' + (isDark ? 'border-gray-600' : 'border-gray-200')}>
          <div>
            <h2 className={'text-lg font-semibold ' + textPrimary}>Template Preview</h2>
            <p className={'text-sm mt-0.5 ' + textSecondary}>{template.name}</p>
          </div>
          <button onClick={onClose} className={'text-3xl hover:opacity-70 transition ' + textSecondary}>&times;</button>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600 mx-auto mb-4"></div>
              <p className={textPrimary}>Loading preview...</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className={(isDark ? 'bg-gray-700/50' : 'bg-gray-50') + ' p-4 rounded-lg'}>
                <p className={'text-xs font-medium mb-2 ' + textSecondary}>SUBJECT LINE:</p>
                <p className={'text-base font-medium ' + textPrimary}>{previewData?.subject}</p>
              </div>

              {previewData?.html_content && (
                <div className={(isDark ? 'bg-gray-700/50' : 'bg-gray-50') + ' p-4 rounded-lg'}>
                  <p className={'text-xs font-medium mb-3 ' + textSecondary}>EMAIL BODY:</p>
                  <iframe
                    srcDoc={previewData.html_content}
                    className={'border rounded-lg w-full ' + (isDark ? 'bg-white border-gray-600' : 'bg-white border-gray-300')}
                    style={{ height: '600px', maxHeight: '70vh' }}
                    title="Email Preview"
                    sandbox="allow-same-origin"
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function TemplateCreator({ onClose, isDark }) {
  const [step, setStep] = useState(1);
  const [aiData, setAiData] = useState({
    description: '',
    category: 'IT',
    difficulty: 'medium',
    company_name: ''
  });
  const [generating, setGenerating] = useState(false);
  const [generatedTemplate, setGeneratedTemplate] = useState(null);

  const categories = ['IT', 'HR', 'Finance', 'Banking', 'Delivery', 'E-commerce', 'General'];
  const difficulties = ['easy', 'medium', 'hard'];

  const handleGenerate = async () => {
    if (!aiData.description) {
      alert('Please describe what kind of phishing email you want!');
      return;
    }

    setGenerating(true);
    try {
      const response = await api.generateAITemplate(aiData);
      setGeneratedTemplate(response.data);
      setStep(2);
    } catch (error) {
      console.error('Error generating template:', error);
      alert('Failed to generate template. Make sure GEMINI_API_KEY is set in backend/.env');
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async () => {
    try {
      await api.createTemplate({
        ...generatedTemplate,
        category: aiData.category,
        difficulty: aiData.difficulty
      });
      alert('Template saved successfully!');
      onClose();
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Failed to save template');
    }
  };

  const cardBg = isDark ? 'bg-gray-800' : 'bg-white';
  const inputBg = isDark ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-600';

  return (
    <div className={'min-h-screen p-6 ' + (isDark ? 'bg-gray-900' : 'bg-gray-50')}>
      <div className={'max-w-5xl mx-auto rounded-lg shadow-lg overflow-hidden ' + cardBg}>
        <div className={(isDark ? 'bg-gray-700' : 'bg-gray-100') + ' p-5 border-b ' + (isDark ? 'border-gray-600' : 'border-gray-200')}>
          <div className="flex justify-between items-center">
            <div>
              <h2 className={'text-xl font-semibold ' + textPrimary}>AI Template Creator</h2>
              <p className={'text-sm mt-0.5 ' + textSecondary}>Describe what you want, AI will create it</p>
            </div>
            <button onClick={onClose} className={'text-3xl hover:opacity-70 transition leading-none ' + textSecondary}>&times;</button>
          </div>
        </div>

        <div className="p-6">
          {/* Progress Steps */}
          <div className="flex items-center justify-center mb-6">
            <div className={`flex items-center ${step >= 1 ? 'text-indigo-600' : textSecondary}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-medium text-sm ${step >= 1 ? 'bg-indigo-600 text-white' : (isDark ? 'bg-gray-700' : 'bg-gray-300')}`}>1</div>
              <span className="ml-2 font-medium text-sm">Describe</span>
            </div>
            <div className={`w-16 h-0.5 mx-3 ${step >= 2 ? 'bg-indigo-600' : (isDark ? 'bg-gray-700' : 'bg-gray-300')}`}></div>
            <div className={`flex items-center ${step >= 2 ? 'text-indigo-600' : textSecondary}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-medium text-sm ${step >= 2 ? 'bg-indigo-600 text-white' : (isDark ? 'bg-gray-700' : 'bg-gray-300')}`}>2</div>
              <span className="ml-2 font-medium text-sm">Review & Save</span>
            </div>
          </div>

          {step === 1 && (
            <div className="space-y-4">
              <div>
                <label className={'block text-sm font-medium mb-2 ' + textPrimary}>
                  What kind of phishing email do you want?
                </label>
                <textarea
                  value={aiData.description}
                  onChange={(e) => setAiData({ ...aiData, description: e.target.value })}
                  className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  rows="4"
                  placeholder="Example: Create a password reset email from IT department saying the user's password will expire in 24 hours..."
                />
                <p className={'text-xs mt-1 ' + textSecondary}>Be specific! Describe the sender, urgency, action needed, etc.</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Category</label>
                  <select
                    value={aiData.category}
                    onChange={(e) => setAiData({ ...aiData, category: e.target.value })}
                    className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Difficulty</label>
                  <select
                    value={aiData.difficulty}
                    onChange={(e) => setAiData({ ...aiData, difficulty: e.target.value })}
                    className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  >
                    {difficulties.map(diff => (
                      <option key={diff} value={diff}>
                        {diff.charAt(0).toUpperCase() + diff.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Company Name (Optional)</label>
                <input
                  type="text"
                  value={aiData.company_name}
                  onChange={(e) => setAiData({ ...aiData, company_name: e.target.value })}
                  className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  placeholder="e.g., Acme Corp"
                />
              </div>

              <button
                onClick={handleGenerate}
                disabled={generating || !aiData.description}
                className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium text-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {generating ? 'AI is creating your template...' : 'Generate with AI'}
              </button>
            </div>
          )}

          {step === 2 && generatedTemplate && (
            <div className="space-y-4">
              <div className={(isDark ? 'bg-green-500/20 border-green-500/30' : 'bg-green-50 border-green-200') + ' border rounded-lg p-3'}>
                <p className={(isDark ? 'text-green-400' : 'text-green-800') + ' font-medium text-sm'}>Template generated successfully!</p>
              </div>

              <div>
                <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Template Name</label>
                <input
                  type="text"
                  value={generatedTemplate.name}
                  onChange={(e) => setGeneratedTemplate({ ...generatedTemplate, name: e.target.value })}
                  className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                />
              </div>

              <div>
                <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Subject Line</label>
                <input
                  type="text"
                  value={generatedTemplate.subject}
                  onChange={(e) => setGeneratedTemplate({ ...generatedTemplate, subject: e.target.value })}
                  className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                />
              </div>

              <div>
                <label className={'block text-sm font-medium mb-2 ' + textPrimary}>HTML Content (You can edit)</label>
                <textarea
                  value={generatedTemplate.html_content}
                  onChange={(e) => setGeneratedTemplate({ ...generatedTemplate, html_content: e.target.value })}
                  className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-mono text-xs ' + inputBg}
                  rows="10"
                />
              </div>

              <div className={(isDark ? 'bg-gray-700/50 border-gray-600' : 'bg-gray-50 border-gray-300') + ' border rounded-lg p-4'}>
                <p className={'font-medium mb-3 text-sm ' + textPrimary}>Preview:</p>
                <div
                  className={(isDark ? 'bg-gray-900 border-gray-600' : 'bg-white border-gray-300') + ' border rounded-lg p-4 max-h-80 overflow-y-auto text-sm'}
                  dangerouslySetInnerHTML={{ __html: generatedTemplate.html_content }}
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className={(isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300') + ' flex-1 py-2 rounded-lg font-medium text-sm transition ' + textPrimary}
                >
                  Back
                </button>
                <button
                  onClick={handleSave}
                  className="flex-1 bg-indigo-600 text-white py-2 rounded-lg font-medium text-sm hover:bg-indigo-700 transition"
                >
                  Save Template
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TemplateManager;
