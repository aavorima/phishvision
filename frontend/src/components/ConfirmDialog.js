import React, { useEffect } from 'react';
import { useTheme } from '../ThemeContext';

function ConfirmDialog({
  isOpen,
  title,
  message,
  onConfirm,
  onCancel,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'info'
}) {
  const { isDark } = useTheme();

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onCancel();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onCancel]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const typeConfig = {
    danger: {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      iconBg: 'bg-danger/10',
      iconColor: 'text-danger',
      buttonBg: 'bg-gradient-to-r from-danger to-danger-dim',
    },
    warning: {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      iconBg: 'bg-warning/10',
      iconColor: 'text-warning',
      buttonBg: 'bg-gradient-to-r from-warning to-warning-dim',
    },
    success: {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      iconBg: 'bg-success/10',
      iconColor: 'text-success',
      buttonBg: 'bg-gradient-to-r from-success to-success-dim',
    },
    info: {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      iconBg: 'bg-primary/10',
      iconColor: 'text-primary',
      buttonBg: 'bg-gradient-to-r from-primary to-primary-dim',
    },
  };

  const config = typeConfig[type] || typeConfig.info;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={onCancel}
      />

      {/* Dialog */}
      <div
        className={`relative w-full max-w-md rounded-2xl border overflow-hidden animate-fade-in-up ${
          isDark ? 'bg-surface-2 border-white/10' : 'bg-white border-black/10 shadow-2xl'
        }`}
      >
        {/* Content */}
        <div className="p-6">
          <div className="flex items-start space-x-4">
            <div className={`p-3 rounded-xl ${config.iconBg}`}>
              <div className={config.iconColor}>{config.icon}</div>
            </div>
            <div className="flex-1 min-w-0">
              <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                {title}
              </h3>
              <p className={`text-sm leading-relaxed ${isDark ? 'text-white/60' : 'text-surface-1/60'}`}>
                {message}
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className={`p-4 flex gap-3 border-t ${isDark ? 'border-white/5 bg-surface-3/30' : 'border-black/5 bg-surface-light-2'}`}>
          <button
            onClick={onCancel}
            className={`flex-1 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 hover:scale-[1.02] ${
              isDark
                ? 'bg-surface-3 text-white border border-white/10 hover:bg-surface-4'
                : 'bg-surface-light-3 text-surface-1 border border-black/10 hover:bg-surface-light-4'
            }`}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`flex-1 px-4 py-2.5 rounded-xl font-semibold text-sm text-white transition-all duration-200 hover:scale-[1.02] ${config.buttonBg}`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
