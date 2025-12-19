import React, { useState, useEffect } from 'react';
import api from '../api/api';

function TemplateEditor({ template, onClose, onSave, isDark }) {
  const [formData, setFormData] = useState({
    name: '',
    category: 'General',
    subject: '',
    html_content: '',
    from_name: '',
    difficulty: 'medium',
    description: '',
    language: 'EN'
  });
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('editor'); // 'editor' or 'preview'

  const categories = ['Banking', 'Delivery', 'E-commerce', 'Education', 'Marketing', 'IT', 'HR', 'Finance', 'Crypto', 'General'];
  const difficulties = ['easy', 'medium', 'hard'];
  const languages = ['EN', 'AZ', 'TR', 'RU'];

  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name || '',
        category: template.category || 'General',
        subject: template.subject || '',
        html_content: template.html_content || '',
        from_name: template.from_name || '',
        difficulty: template.difficulty || 'medium',
        description: template.description || '',
        language: template.language || 'EN'
      });
    }
  }, [template]);

  const handleSave = async () => {
    if (!formData.name || !formData.subject || !formData.html_content) {
      alert('Please fill in Name, Subject, and HTML Content');
      return;
    }

    setSaving(true);
    try {
      if (template?.id) {
        // Update existing template
        await api.updateTemplate(template.id, formData);
      } else {
        // Create new template
        await api.createTemplate(formData);
      }
      onSave();
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Failed to save template: ' + (error.response?.data?.error || error.message));
    } finally {
      setSaving(false);
    }
  };

  const handleImportHTML = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.html,.htm';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (file) {
        const text = await file.text();
        setFormData({ ...formData, html_content: text });
      }
    };
    input.click();
  };

  const bgColor = isDark ? 'bg-gray-900' : 'bg-gray-50';
  const cardBg = isDark ? 'bg-gray-800' : 'bg-white';
  const inputBg = isDark ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' : 'bg-white border-gray-300 text-gray-900';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-600';
  const borderColor = isDark ? 'border-gray-700' : 'border-gray-200';

  return (
    <div className={'min-h-screen p-6 ' + bgColor}>
      <div className={'max-w-6xl mx-auto rounded-lg shadow-lg overflow-hidden ' + cardBg}>
        {/* Header */}
        <div className={(isDark ? 'bg-gray-700' : 'bg-gray-100') + ' p-5 border-b ' + borderColor}>
          <div className="flex justify-between items-center">
            <div>
              <h2 className={'text-xl font-semibold ' + textPrimary}>
                {template?.id ? 'Edit Template' : 'Create New Template'}
              </h2>
              <p className={'text-sm mt-0.5 ' + textSecondary}>
                {template?.id ? 'Modify the template HTML and settings' : 'Create a custom phishing template with HTML'}
              </p>
            </div>
            <button onClick={onClose} className={'text-3xl hover:opacity-70 transition leading-none ' + textSecondary}>&times;</button>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Form */}
            <div className="space-y-4">
              {/* Template Name */}
              <div>
                <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Template Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  placeholder="e.g., IT Password Reset"
                />
              </div>

              {/* Category, Difficulty, Language Row */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
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
                    value={formData.difficulty}
                    onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                    className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  >
                    {difficulties.map(diff => (
                      <option key={diff} value={diff}>{diff.charAt(0).toUpperCase() + diff.slice(1)}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Language</label>
                  <select
                    value={formData.language}
                    onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                    className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  >
                    {languages.map(lang => (
                      <option key={lang} value={lang}>{lang}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Subject Line */}
              <div>
                <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Email Subject *</label>
                <input
                  type="text"
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  placeholder="e.g., Urgent: Your Password Expires in 24 Hours"
                />
              </div>

              {/* From Name (Sender Display Name) */}
              <div>
                <label className={'block text-sm font-medium mb-2 ' + textPrimary}>
                  Sender Name
                  <span className={textSecondary + ' font-normal ml-2'}>(optional)</span>
                </label>
                <input
                  type="text"
                  value={formData.from_name}
                  onChange={(e) => setFormData({ ...formData, from_name: e.target.value })}
                  className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  placeholder="e.g., Zoom Support Team, Amazon Delivery, IT Security"
                />
                <p className={'text-xs mt-1 ' + textSecondary}>
                  Display name shown in the "From" field. Leave empty to use default SMTP settings.
                </p>
              </div>

              {/* Description */}
              <div>
                <label className={'block text-sm font-medium mb-2 ' + textPrimary}>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-sm ' + inputBg}
                  rows="2"
                  placeholder="Brief description of this phishing template..."
                />
              </div>
            </div>

            {/* Right Column - HTML Editor & Preview */}
            <div className="space-y-4">
              {/* Tabs */}
              <div className="flex border-b border-gray-700">
                <button
                  onClick={() => setActiveTab('editor')}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
                    activeTab === 'editor'
                      ? 'border-indigo-500 text-indigo-500'
                      : 'border-transparent ' + textSecondary + ' hover:text-indigo-400'
                  }`}
                >
                  HTML Editor
                </button>
                <button
                  onClick={() => setActiveTab('preview')}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition ${
                    activeTab === 'preview'
                      ? 'border-indigo-500 text-indigo-500'
                      : 'border-transparent ' + textSecondary + ' hover:text-indigo-400'
                  }`}
                >
                  Live Preview
                </button>
                <div className="flex-1"></div>
                <button
                  onClick={handleImportHTML}
                  className={'px-3 py-1 text-xs rounded hover:bg-gray-700 transition ' + textSecondary}
                >
                  Import HTML
                </button>
              </div>

              {/* Editor/Preview Content */}
              {activeTab === 'editor' ? (
                <div>
                  <textarea
                    value={formData.html_content}
                    onChange={(e) => setFormData({ ...formData, html_content: e.target.value })}
                    className={'w-full px-3 py-2 border rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-mono text-xs ' + inputBg}
                    rows="20"
                    placeholder="Paste or write your HTML email template here..."
                    spellCheck="false"
                  />
                </div>
              ) : (
                <div className={(isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-300') + ' border rounded-lg p-4'}>
                  <iframe
                    srcDoc={formData.html_content || '<p style="color: #666; text-align: center; padding: 40px;">No HTML content yet...</p>'}
                    className="w-full bg-white rounded-lg border"
                    style={{ height: '400px' }}
                    title="Email Preview"
                    sandbox="allow-same-origin"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 mt-6 pt-6 border-t border-gray-700">
            <button
              onClick={onClose}
              className={(isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300') + ' flex-1 py-2.5 rounded-lg font-medium text-sm transition ' + textPrimary}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !formData.name || !formData.subject || !formData.html_content}
              className="flex-1 bg-indigo-600 text-white py-2.5 rounded-lg font-medium text-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {saving ? 'Saving...' : (template?.id ? 'Update Template' : 'Create Template')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TemplateEditor;
