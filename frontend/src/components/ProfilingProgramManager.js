import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../ThemeContext';
import {
  getPrograms,
  getProgram,
  createProgram,
  scheduleProgram,
  startProgram,
  pauseProgram,
  resumeProgram,
  completeProgram,
  deleteProgram,
  getProgramStats,
  getProgramCampaigns,
  getEmployeeDepartments,
  getTemplates,
  getEmployees,
  getLandingPages,
  getSMSTemplates,
  getCampaign,
  getProgramReport,
  getQRCampaigns
} from '../api/api';

const VECTORS = [
  { id: 'email', name: 'Email Phishing', icon: '📧', description: 'Traditional email-based phishing simulations' },
  { id: 'qr', name: 'QR Code Phishing', icon: '📱', description: 'QR code-based phishing (quishing)' },
  { id: 'sms', name: 'SMS Phishing', icon: '💬', description: 'SMS-based phishing (smishing)' }
];

const AZERBAIJAN_COMPANIES = [
  'Birbank', 'Umico', 'Kapital Bank', 'Bakcell', 'Azercell', 'Azericard',
  'Nar Mobile', 'ABB', 'Pasha Bank', 'Rabitabank', 'Express Bank',
  'Bank Respublika', 'Turanbank', 'Yelo Bank', 'PASHA Life', 'AtaBank'
];

// Program Details Modal Component
const ProgramDetailsModal = ({ program, onClose, isDarkMode }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [emailCampaign, setEmailCampaign] = useState(null);
  const [smsCampaign, setSmsCampaign] = useState(null);
  const [qrCampaign, setQrCampaign] = useState(null);

  useEffect(() => {
    loadCampaigns();
  }, [program.id]);

  const loadCampaigns = async () => {
    try {
      setLoading(true);

      console.log('[DEBUG] Loading campaigns for program:', program.id, program.name);

      // Get all campaigns associated with this program
      const response = await getProgramCampaigns(program.id);

      console.log('[DEBUG] API Response:', response);
      console.log('[DEBUG] Response data:', response.data);
      console.log('[DEBUG] Response data.campaigns:', response.data?.campaigns);

      const campaignsData = response.data.campaigns || response.data || [];
      console.log('[DEBUG] Campaigns array:', campaignsData);
      console.log('[DEBUG] Campaigns count:', campaignsData.length);

      setCampaigns(campaignsData);

      // Separate campaigns by vector type
      let email = null;
      let sms = null;
      let qr = null;

      for (const campaign of campaignsData) {
        console.log('[DEBUG] Processing campaign:', campaign.name, 'Type:', campaign.type);
        // Determine campaign type from the 'type' field returned by backend
        if (campaign.type === 'email') {
          email = campaign;
          console.log('[DEBUG] Found email campaign:', campaign.name);
        } else if (campaign.type === 'sms') {
          sms = campaign;
          console.log('[DEBUG] Found SMS campaign:', campaign.name);
        } else if (campaign.type === 'qr') {
          qr = campaign;
          console.log('[DEBUG] Found QR campaign:', campaign.name);
        }
      }

      console.log('[DEBUG] Setting state - Email:', email?.name, 'SMS:', sms?.name, 'QR:', qr?.name);

      // Set all state at once
      setEmailCampaign(email);
      setSmsCampaign(sms);
      setQrCampaign(qr);
    } catch (error) {
      console.error('Error loading program campaigns:', error);
      console.error('Error details:', error.response?.data);
      console.error('Error status:', error.response?.status);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className={`rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto ${
        isDarkMode ? 'bg-gray-800' : 'bg-white'
      }`}>
        {/* Header */}
        <div className={`sticky top-0 z-10 border-b ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex justify-between items-center p-6">
            <div>
              <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                {program.name}
              </h2>
              <p className={`text-sm mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                {program.description}
              </p>
            </div>
            <button
              onClick={onClose}
              className={`p-2 rounded-lg ${isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            >
              <span className="text-2xl">&times;</span>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="spinner mb-4"></div>
                <p className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>Loading campaign results...</p>
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              {/* Email Campaign Results */}
              {emailCampaign && (
                <VectorResults
                  vectorName="Email Phishing"
                  vectorIcon="📧"
                  campaign={emailCampaign}
                  isDarkMode={isDarkMode}
                />
              )}

              {/* SMS Campaign Results */}
              {smsCampaign && (
                <SMSVectorResults
                  vectorName="SMS Phishing"
                  vectorIcon="💬"
                  campaign={smsCampaign}
                  isDarkMode={isDarkMode}
                />
              )}

              {/* QR Campaign Results */}
              {qrCampaign && (
                <QRVectorResults
                  vectorName="QR Code Phishing"
                  vectorIcon="📱"
                  campaign={qrCampaign}
                  isDarkMode={isDarkMode}
                />
              )}

              {!emailCampaign && !smsCampaign && !qrCampaign && (
                <div className={`text-center py-12 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  <p>No campaign results found for this program</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Email/General Vector Results Component
const VectorResults = ({ vectorName, vectorIcon, campaign, isDarkMode }) => {
  const targets = campaign.targets || [];
  const stats = campaign.stats || {};

  // Use stats from backend if available, otherwise calculate from targets
  const totalTargets = stats.total || targets.length;
  const opened = stats.opened || targets.filter(t => t.opened_at).length;
  const clicked = stats.clicked || targets.filter(t => t.clicked_at).length;
  const submitted = stats.submitted || targets.filter(t => t.submitted_at).length;
  const openRate = stats.open_rate || (totalTargets > 0 ? ((opened / totalTargets) * 100).toFixed(1) : 0);
  const clickRate = stats.click_rate || (totalTargets > 0 ? ((clicked / totalTargets) * 100).toFixed(1) : 0);
  const submitRate = stats.submit_rate || (totalTargets > 0 ? ((submitted / totalTargets) * 100).toFixed(1) : 0);

  return (
    <div className={`border rounded-lg p-6 ${isDarkMode ? 'border-gray-700 bg-gray-900/50' : 'border-gray-200 bg-gray-50'}`}>
      <div className="flex items-center mb-4">
        <span className="text-3xl mr-3">{vectorIcon}</span>
        <div>
          <h3 className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            {vectorName}
          </h3>
          <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Campaign: {campaign.name}
          </p>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Total Sent</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{totalTargets}</div>
        </div>
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Opened</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{opened}</div>
          <div className="text-sm text-blue-500">{openRate}% rate</div>
        </div>
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Clicked</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{clicked}</div>
          <div className="text-sm text-orange-500">{clickRate}% rate</div>
        </div>
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Submitted Credentials</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{submitted}</div>
          <div className="text-sm text-red-500">{submitRate}% rate</div>
        </div>
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Not Opened</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{totalTargets - opened}</div>
        </div>
      </div>

      {/* Target Details Table */}
      <div className={`rounded-lg overflow-hidden border ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
        <table className="w-full">
          <thead className={isDarkMode ? 'bg-gray-800' : 'bg-gray-100'}>
            <tr>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Name</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Email</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Department</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Opened</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Clicked</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Submitted</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Device</th>
            </tr>
          </thead>
          <tbody className={isDarkMode ? 'bg-gray-900' : 'bg-white'}>
            {targets.map((target, index) => (
              <tr key={target.id || index} className={`border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
                <td className={`px-4 py-3 text-sm font-medium ${isDarkMode ? 'text-gray-200' : 'text-gray-900'}`}>{target.name || '-'}</td>
                <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-900'}`}>{target.email}</td>
                <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>{target.department || '-'}</td>
                <td className="px-4 py-3 text-sm">
                  {target.opened_at ? (
                    <span className="text-blue-500">✓ {new Date(target.opened_at).toLocaleDateString('en-US')}</span>
                  ) : (
                    <span className={isDarkMode ? 'text-gray-500' : 'text-gray-400'}>-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm">
                  {target.clicked_at ? (
                    <span className="text-orange-500">✓ {new Date(target.clicked_at).toLocaleDateString('en-US')}</span>
                  ) : (
                    <span className={isDarkMode ? 'text-gray-500' : 'text-gray-400'}>-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm">
                  {target.submitted_at ? (
                    <span className="text-red-500">✓ {new Date(target.submitted_at).toLocaleDateString('en-US')}</span>
                  ) : (
                    <span className={isDarkMode ? 'text-gray-500' : 'text-gray-400'}>-</span>
                  )}
                </td>
                <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                  {target.device_type || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// SMS Vector Results Component
const SMSVectorResults = ({ vectorName, vectorIcon, campaign, isDarkMode }) => {
  const targets = campaign.targets || [];
  const stats = campaign.stats || {};

  // Use stats from backend if available, otherwise calculate from targets
  const totalTargets = stats.total || targets.length;
  const clicked = stats.clicked || targets.filter(t => t.clicked_at).length;
  const submitted = stats.submitted || targets.filter(t => t.submitted_at).length;
  const clickRate = stats.click_rate || (totalTargets > 0 ? ((clicked / totalTargets) * 100).toFixed(1) : 0);
  const submitRate = stats.submit_rate || (totalTargets > 0 ? ((submitted / totalTargets) * 100).toFixed(1) : 0);

  return (
    <div className={`border rounded-lg p-6 ${isDarkMode ? 'border-gray-700 bg-gray-900/50' : 'border-gray-200 bg-gray-50'}`}>
      <div className="flex items-center mb-4">
        <span className="text-3xl mr-3">{vectorIcon}</span>
        <div>
          <h3 className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            {vectorName}
          </h3>
          <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Campaign: {campaign.name}
          </p>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Total Sent</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{totalTargets}</div>
        </div>
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Link Clicked</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{clicked}</div>
          <div className="text-sm text-orange-500">{clickRate}% rate</div>
        </div>
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Submitted Credentials</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{submitted}</div>
          <div className="text-sm text-red-500">{submitRate}% rate</div>
        </div>
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Not Clicked</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{totalTargets - clicked}</div>
        </div>
      </div>

      {/* Target Details Table */}
      <div className={`rounded-lg overflow-hidden border ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
        <table className="w-full">
          <thead className={isDarkMode ? 'bg-gray-800' : 'bg-gray-100'}>
            <tr>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Name</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Phone Number</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Department</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Clicked</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Submitted</th>
              <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Device</th>
            </tr>
          </thead>
          <tbody className={isDarkMode ? 'bg-gray-900' : 'bg-white'}>
            {targets.map((target, index) => (
              <tr key={target.id || index} className={`border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
                <td className={`px-4 py-3 text-sm font-medium ${isDarkMode ? 'text-gray-200' : 'text-gray-900'}`}>{target.name || '-'}</td>
                <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-900'}`}>{target.phone_number}</td>
                <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>{target.department || '-'}</td>
                <td className="px-4 py-3 text-sm">
                  {target.clicked_at ? (
                    <span className="text-orange-500">✓ {new Date(target.clicked_at).toLocaleDateString('en-US')}</span>
                  ) : (
                    <span className={isDarkMode ? 'text-gray-500' : 'text-gray-400'}>-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm">
                  {target.submitted_at ? (
                    <span className="text-red-500">✓ {new Date(target.submitted_at).toLocaleDateString('en-US')}</span>
                  ) : (
                    <span className={isDarkMode ? 'text-gray-500' : 'text-gray-400'}>-</span>
                  )}
                </td>
                <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                  {target.device_type || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// QR Vector Results Component
const QRVectorResults = ({ vectorName, vectorIcon, campaign, isDarkMode }) => {
  const scans = campaign.scans || [];
  const stats = campaign.stats || {};

  // Calculate statistics
  const totalScans = stats.total_scans !== undefined ? stats.total_scans : scans.length;
  const submitted = stats.submitted !== undefined ? stats.submitted : scans.filter(s => s.submitted_credentials).length;
  const submitRate = totalScans > 0 ? ((submitted / totalScans) * 100).toFixed(1) : 0;
  const notScanned = stats.total_generated ? stats.total_generated - totalScans : 0;

  return (
    <div className={`border rounded-lg p-6 ${isDarkMode ? 'border-gray-700 bg-gray-900/50' : 'border-gray-200 bg-gray-50'}`}>
      <div className="flex items-center mb-4">
        <span className="text-3xl mr-3">{vectorIcon}</span>
        <div>
          <h3 className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            {vectorName}
          </h3>
          <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Campaign: {campaign.name}
          </p>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Total Scans</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{totalScans}</div>
          <div className="text-sm text-blue-500">QR code scanned {totalScans} {totalScans === 1 ? 'time' : 'times'}</div>
        </div>
        <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Submitted Credentials</div>
          <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{submitted}</div>
          <div className="text-sm text-red-500">{submitRate}% submit rate</div>
        </div>
      </div>

      {/* Scan Details Table */}
      {totalScans > 0 && (
        <div className={`rounded-lg overflow-hidden border ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <table className="w-full">
            <thead className={isDarkMode ? 'bg-gray-800' : 'bg-gray-100'}>
              <tr>
                <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Email</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Department</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Scanned At</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Submitted</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Device</th>
              </tr>
            </thead>
            <tbody className={isDarkMode ? 'bg-gray-900' : 'bg-white'}>
              {scans.filter(scan => scan.scanned_at).map((scan, index) => (
                <tr key={scan.id || index} className={`border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
                  <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-900'}`}>
                    {scan.email || scan.user_email || '-'}
                  </td>
                  <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {scan.department || '-'}
                  </td>
                  <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-900'}`}>
                    {new Date(scan.scanned_at).toLocaleDateString('en-US')}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {scan.submitted_at ? (
                      <span className="text-red-500">✓ {new Date(scan.submitted_at).toLocaleDateString('en-US')}</span>
                    ) : (
                      <span className={isDarkMode ? 'text-gray-500' : 'text-gray-400'}>-</span>
                    )}
                  </td>
                  <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {scan.device_type || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

function ProfilingProgramManager() {
  const { isDarkMode } = useTheme();
  const navigate = useNavigate();
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [selectedProgramForReport, setSelectedProgramForReport] = useState(null);

  useEffect(() => {
    loadPrograms();
  }, []);

  const loadPrograms = async () => {
    try {
      setLoading(true);
      const response = await getPrograms();
      // Handle both array and object with programs property
      const programsData = Array.isArray(response.data)
        ? response.data
        : (response.data?.programs || []);
      setPrograms(programsData);
    } catch (error) {
      console.error('Error loading programs:', error);
      setPrograms([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProgram = () => {
    setSelectedProgram(null);
    setShowCreateModal(true);
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
    setSelectedProgram(null);
  };

  const handleCloseDetailsModal = () => {
    setShowDetailsModal(false);
    setSelectedProgram(null);
  };

  const handleProgramCreated = () => {
    loadPrograms();
    handleCloseModal();
  };

  const handleViewDetails = (program) => {
    setSelectedProgram(program);
    setShowDetailsModal(true);
  };

  const handleViewReport = (program) => {
    setSelectedProgramForReport(program);
    setShowReportModal(true);
  };

  const handleCloseReportModal = () => {
    setShowReportModal(false);
    setSelectedProgramForReport(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className={isDarkMode ? 'text-gray-400' : 'text-gray-600'}>Loading programs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header and Action Bar */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex-1">
          <h2 className="text-2xl font-semibold text-white" style={{ color: '#ffffff' }}>
            Multi-vector security awareness testing programs
          </h2>
        </div>
        <button
          onClick={handleCreateProgram}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2"
        >
          <span className="text-xl">+</span>
          Create Program
        </button>
      </div>
      
      {/* Title Section */}
      <div className="mb-6">
        <h1 className={`text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          Profiling Programs
        </h1>
      </div>

      {programs.length === 0 ? (
        <div className={`text-center py-12 border-2 border-dashed rounded-lg ${
          isDarkMode ? 'border-gray-700 text-gray-400' : 'border-gray-300 text-gray-500'
        }`}>
          <span className="text-6xl mb-4 block">📊</span>
          <p className="text-lg font-medium mb-2">No profiling programs yet</p>
          <p className="text-sm mb-4">Create your first multi-vector testing program</p>
          <button
            onClick={handleCreateProgram}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium"
          >
            Create Program
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {programs.map((program) => (
            <ProgramCard
              key={program.id}
              program={program}
              isDarkMode={isDarkMode}
              onRefresh={loadPrograms}
              onViewDetails={handleViewDetails}
              onViewReport={handleViewReport}
            />
          ))}
        </div>
      )}

      {showCreateModal && (
        <CreateProgramModal
          onClose={handleCloseModal}
          onSuccess={handleProgramCreated}
          isDarkMode={isDarkMode}
        />
      )}

      {showDetailsModal && selectedProgram && (
        <ProgramDetailsModal
          program={selectedProgram}
          onClose={handleCloseDetailsModal}
          isDarkMode={isDarkMode}
        />
      )}

      {showReportModal && selectedProgramForReport && (
        <ProgramReportModal
          program={selectedProgramForReport}
          onClose={handleCloseReportModal}
          isDarkMode={isDarkMode}
        />
      )}
    </div>
  );
}

// Program Report Modal Component
const ProgramReportModal = ({ program, onClose, isDarkMode }) => {
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [activeSection, setActiveSection] = useState('overview');

  useEffect(() => {
    loadReport();
  }, [program.id]);

  const loadReport = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getProgramReport(program.id);
      setReport(response.data);
    } catch (error) {
      console.error('Error loading program report:', error);
      setError(error.response?.data?.error || 'Failed to load program report');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = () => {
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    const url = `${API_BASE_URL}/api/programs/${program.id}/report/export?format=pdf`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `program-report-${program.id}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getRiskLevelColor = (level) => {
    const colors = {
      critical: isDarkMode ? 'bg-red-900/30 text-red-400 border-red-900/50' : 'bg-red-100 text-red-700 border-red-200',
      high: isDarkMode ? 'bg-orange-900/30 text-orange-400 border-orange-900/50' : 'bg-orange-100 text-orange-700 border-orange-200',
      medium: isDarkMode ? 'bg-yellow-900/30 text-yellow-400 border-yellow-900/50' : 'bg-yellow-100 text-yellow-700 border-yellow-200',
      low: isDarkMode ? 'bg-green-900/30 text-green-400 border-green-900/50' : 'bg-green-100 text-green-700 border-green-200',
      positive: isDarkMode ? 'bg-blue-900/30 text-blue-400 border-blue-900/50' : 'bg-blue-100 text-blue-700 border-blue-200'
    };
    return colors[level] || colors.medium;
  };

  const getAwarenessColor = (level) => {
    const colors = {
      'Excellent': isDarkMode ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-700',
      'Good': isDarkMode ? 'bg-blue-900/30 text-blue-400' : 'bg-blue-100 text-blue-700',
      'Fair': isDarkMode ? 'bg-yellow-900/30 text-yellow-400' : 'bg-yellow-100 text-yellow-700',
      'Poor': isDarkMode ? 'bg-orange-900/30 text-orange-400' : 'bg-orange-100 text-orange-700',
      'Critical': isDarkMode ? 'bg-red-900/30 text-red-400' : 'bg-red-100 text-red-700'
    };
    return colors[level] || colors.Fair;
  };

  const bgPrimary = isDarkMode ? 'bg-slate-900' : 'bg-slate-50';
  const bgCard = isDarkMode ? 'bg-slate-800' : 'bg-white';
  const borderColor = isDarkMode ? 'border-slate-700' : 'border-slate-200';
  const textPrimary = isDarkMode ? 'text-slate-50' : 'text-slate-900';
  const textSecondary = isDarkMode ? 'text-slate-400' : 'text-slate-600';

  const sections = [
    { id: 'overview', label: 'Overview' },
    { id: 'awareness', label: 'Awareness Summary' },
    { id: 'campaigns', label: 'Campaign Breakdown' },
    { id: 'employees', label: 'Employee Results' },
    { id: 'departments', label: 'Department Breakdown' },
    { id: 'gaps', label: 'Security Gaps' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
      <div className={`${bgCard} rounded-xl shadow-2xl max-w-7xl w-full max-h-[90vh] overflow-y-auto`}>
        {/* Header */}
        <div className={`sticky top-0 ${bgCard} border-b ${borderColor} p-6 z-10`}>
          <div className="flex items-center justify-between">
            <div>
              <h2 className={`text-2xl font-semibold ${textPrimary}`}>Program Awareness Report</h2>
              <p className={`text-sm mt-1 ${textSecondary}`}>{program.name}</p>
            </div>
            <div className="flex gap-2">
              {!loading && !error && (
                <button
                  onClick={handleExportPDF}
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  Export PDF
                </button>
              )}
              <button
                onClick={onClose}
                className={`p-2 rounded-lg transition ${isDarkMode ? 'hover:bg-slate-700' : 'hover:bg-slate-100'}`}
              >
                <svg className={`w-6 h-6 ${textPrimary}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-8 text-center">
            <svg className={`w-16 h-16 mx-auto mb-4 ${textSecondary}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className={`text-xl font-semibold mb-2 ${textPrimary}`}>Error Loading Report</h3>
            <p className={`mb-6 ${textSecondary}`}>{error}</p>
            <button
              onClick={loadReport}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Report Content */}
        {!loading && !error && report && (
          <>
            {/* Section Navigation */}
            <div className={`sticky top-[89px] ${bgCard} border-b ${borderColor} p-4 z-10`}>
              <div className="flex gap-2 overflow-x-auto">
                {sections.map(section => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition ${
                      activeSection === section.id
                        ? 'bg-blue-600 text-white'
                        : isDarkMode
                          ? 'text-slate-400 hover:text-white hover:bg-slate-700'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    {section.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Content Sections */}
            <div className="p-6 space-y-6">
              {/* 1. Overview */}
              {activeSection === 'overview' && report.overview && (
                <div className={`${bgCard} border ${borderColor} rounded-xl p-6`}>
                  <h3 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Program Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div>
                      <p className={`text-sm ${textSecondary} mb-1`}>Program Name</p>
                      <p className={`font-medium ${textPrimary}`}>{report.overview.program_name}</p>
                    </div>
                    <div>
                      <p className={`text-sm ${textSecondary} mb-1`}>Total Employees</p>
                      <p className={`font-medium ${textPrimary}`}>{report.overview.total_employees || 0}</p>
                    </div>
                    <div>
                      <p className={`text-sm ${textSecondary} mb-1`}>Total Campaigns</p>
                      <p className={`font-medium ${textPrimary}`}>{report.overview.total_campaigns}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* 2. Awareness Summary */}
              {activeSection === 'awareness' && report.awareness_summary && (
                <div>
                  <div className={`${bgCard} border ${borderColor} rounded-xl p-6 mb-6`}>
                    <div className="text-center">
                      <h3 className={`text-sm font-medium mb-2 ${textSecondary}`}>Overall Awareness Score</h3>
                      <div className="flex items-center justify-center gap-4 mb-4">
                        <div className={`text-6xl font-bold ${textPrimary}`}>{report.awareness_summary.awareness_score}</div>
                        <div className="text-left">
                          <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${getAwarenessColor(report.awareness_summary.awareness_level)}`}>
                            {report.awareness_summary.awareness_level}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className={`${bgCard} border ${borderColor} rounded-xl p-6`}>
                    <h3 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Employee Behavior Breakdown</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className={`p-4 rounded-lg border ${isDarkMode ? 'bg-green-900/10 border-green-900/30' : 'bg-green-50 border-green-200'}`}>
                        <p className={`text-sm ${textSecondary} mb-1`}>No Interaction</p>
                        <p className={`text-2xl font-bold ${isDarkMode ? 'text-green-400' : 'text-green-700'}`}>
                          {report.awareness_summary.no_interaction_percent}%
                        </p>
                        <p className={`text-xs ${textSecondary}`}>{report.awareness_summary.no_interaction_count} employees</p>
                      </div>
                      <div className={`p-4 rounded-lg border ${isDarkMode ? 'bg-orange-900/10 border-orange-900/30' : 'bg-orange-50 border-orange-200'}`}>
                        <p className={`text-sm ${textSecondary} mb-1`}>Clicked/Interacted</p>
                        <p className={`text-2xl font-bold ${isDarkMode ? 'text-orange-400' : 'text-orange-700'}`}>
                          {report.awareness_summary.clicked_percent}%
                        </p>
                        <p className={`text-xs ${textSecondary}`}>{report.awareness_summary.clicked_count} employees</p>
                      </div>
                      <div className={`p-4 rounded-lg border ${isDarkMode ? 'bg-red-900/10 border-red-900/30' : 'bg-red-50 border-red-200'}`}>
                        <p className={`text-sm ${textSecondary} mb-1`}>Submitted Credentials</p>
                        <p className={`text-2xl font-bold ${isDarkMode ? 'text-red-400' : 'text-red-700'}`}>
                          {report.awareness_summary.submitted_credentials_percent}%
                        </p>
                        <p className={`text-xs ${textSecondary}`}>{report.awareness_summary.submitted_credentials_count} employees</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 3. Campaign Breakdown */}
              {activeSection === 'campaigns' && report.campaign_breakdown && (
                <div className={`${bgCard} border ${borderColor} rounded-xl p-6`}>
                  <h3 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Campaign Breakdown by Vector</h3>
                  {console.log('[REPORT DEBUG] Campaign Breakdown:', report.campaign_breakdown)}
                  {console.log('[REPORT DEBUG] QR Campaigns:', report.campaign_breakdown.qr_campaigns)}
                  <div className="space-y-6">
                    {/* Email Campaigns */}
                    {report.campaign_breakdown.email_campaigns && report.campaign_breakdown.email_campaigns.length > 0 && (
                      <div>
                        <h4 className={`font-semibold mb-3 ${textPrimary} flex items-center gap-2`}>
                          <span>📧</span> Email Campaigns ({report.campaign_breakdown.email_campaigns.length})
                        </h4>
                        <div className="space-y-2">
                          {report.campaign_breakdown.email_campaigns.map((camp, idx) => (
                            <div key={idx} className={`p-4 rounded-lg border ${borderColor}`}>
                              <div className="flex justify-between items-start mb-3">
                                <div className={`font-medium ${textPrimary}`}>{camp.name}</div>
                                <span className={`text-sm ${textSecondary}`}>{camp.click_rate}% click rate</span>
                              </div>
                              <div className="flex items-center gap-6 text-sm">
                                <div className="flex items-center gap-2">
                                  <span className={textSecondary}>Targets:</span>
                                  <span className={`font-medium ${textPrimary}`}>{camp.total_targets}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={textSecondary}>Opened:</span>
                                  <span className={`font-medium ${textPrimary}`}>{camp.opened_count}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={textSecondary}>Clicked:</span>
                                  <span className={`font-medium ${textPrimary}`}>{camp.clicked_count}</span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* SMS Campaigns */}
                    {report.campaign_breakdown.sms_campaigns && report.campaign_breakdown.sms_campaigns.length > 0 && (
                      <div>
                        <h4 className={`font-semibold mb-3 ${textPrimary} flex items-center gap-2`}>
                          <span>💬</span> SMS Campaigns ({report.campaign_breakdown.sms_campaigns.length})
                        </h4>
                        <div className="space-y-2">
                          {report.campaign_breakdown.sms_campaigns.map((camp, idx) => (
                            <div key={idx} className={`p-4 rounded-lg border ${borderColor}`}>
                              <div className="flex justify-between items-start mb-3">
                                <div className={`font-medium ${textPrimary}`}>{camp.name}</div>
                                <span className={`text-sm ${textSecondary}`}>{camp.click_rate}% click rate</span>
                              </div>
                              <div className="flex items-center gap-6 text-sm">
                                <div className="flex items-center gap-2">
                                  <span className={textSecondary}>Targets:</span>
                                  <span className={`font-medium ${textPrimary}`}>{camp.total_targets}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={textSecondary}>Clicked:</span>
                                  <span className={`font-medium ${textPrimary}`}>{camp.clicked_count}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={textSecondary}>Not Clicked:</span>
                                  <span className={`font-medium ${textPrimary}`}>{camp.total_targets - camp.clicked_count}</span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* QR Campaigns */}
                    {report.campaign_breakdown.qr_campaigns && report.campaign_breakdown.qr_campaigns.length > 0 && (
                      <div>
                        <h4 className={`font-semibold mb-3 ${textPrimary} flex items-center gap-2`}>
                          <span>📱</span> QR Code Campaigns ({report.campaign_breakdown.qr_campaigns.length})
                        </h4>
                        <div className="space-y-2">
                          {report.campaign_breakdown.qr_campaigns.map((camp, idx) => (
                            <div key={idx} className={`p-4 rounded-lg border ${borderColor}`}>
                              <div className="flex justify-between items-start mb-3">
                                <div className={`font-medium ${textPrimary}`}>{camp.campaign_name}</div>
                                <span className={`text-sm ${textSecondary}`}>{camp.clicked_rate}% scan rate</span>
                              </div>
                              <div className="flex items-center gap-6 text-sm">
                                <div className="flex items-center gap-2">
                                  <span className={textSecondary}>Total Targets:</span>
                                  <span className={`font-medium ${textPrimary}`}>{camp.total_targets}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={textSecondary}>Scanned:</span>
                                  <span className={`font-medium ${textPrimary}`}>{camp.clicked}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={textSecondary}>Not Scanned:</span>
                                  <span className={`font-medium ${textPrimary}`}>{camp.total_targets - camp.clicked}</span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 4. Employee Results */}
              {activeSection === 'employees' && report.employee_results && (
                <div className={`${bgCard} border ${borderColor} rounded-xl overflow-hidden`}>
                  <div className="p-6">
                    <h3 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Individual Employee Results</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className={isDarkMode ? 'bg-slate-700/50' : 'bg-slate-50'}>
                        <tr>
                          <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Employee</th>
                          <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Department</th>
                          <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Failed Vectors</th>
                          <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Risk Level</th>
                          <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Training</th>
                        </tr>
                      </thead>
                      <tbody className={`divide-y ${borderColor}`}>
                        {report.employee_results.map((employee, index) => (
                          <tr key={index} className={isDarkMode ? 'hover:bg-slate-700/30' : 'hover:bg-slate-50'}>
                            <td className="px-6 py-4">
                              <div className={`font-medium ${textPrimary}`}>{employee.name}</div>
                              <div className={`text-sm ${textSecondary}`}>
                                {employee.email || employee.phone || 'No contact info'}
                              </div>
                            </td>
                            <td className={`px-6 py-4 ${textSecondary}`}>{employee.department || 'N/A'}</td>
                            <td className="px-6 py-4">
                              <div className="flex flex-wrap gap-1">
                                {employee.failed_vectors && employee.failed_vectors.length > 0 ? (
                                  employee.failed_vectors.map((vector, idx) => {
                                    const getVectorIcon = (v) => {
                                      if (v === 'Email') return '📧';
                                      if (v === 'SMS') return '💬';
                                      if (v === 'QR') return '📱';
                                      return '';
                                    };
                                    const getVectorColor = (v) => {
                                      if (v === 'Email') return isDarkMode ? 'bg-blue-900/30 text-blue-300 border border-blue-700' : 'bg-blue-100 text-blue-700 border border-blue-300';
                                      if (v === 'SMS') return isDarkMode ? 'bg-purple-900/30 text-purple-300 border border-purple-700' : 'bg-purple-100 text-purple-700 border border-purple-300';
                                      if (v === 'QR') return isDarkMode ? 'bg-orange-900/30 text-orange-300 border border-orange-700' : 'bg-orange-100 text-orange-700 border border-orange-300';
                                      return isDarkMode ? 'bg-slate-700 text-slate-300' : 'bg-slate-200 text-slate-700';
                                    };
                                    return (
                                      <span key={idx} className={`px-2 py-1 rounded text-xs font-medium ${getVectorColor(vector)}`}>
                                        {getVectorIcon(vector)} {vector}
                                      </span>
                                    );
                                  })
                                ) : (
                                  <span className={`text-xs ${textSecondary}`}>None</span>
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <span className={`px-2 py-1 rounded-md text-xs font-semibold ${getRiskLevelColor(employee.risk_level)}`}>
                                {employee.risk_level.toUpperCase()}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              {employee.training_completed ? (
                                <span className={`text-xs font-medium ${isDarkMode ? 'text-green-400' : 'text-green-600'}`}>✓ Completed</span>
                              ) : employee.training_recommended ? (
                                <span className={`text-xs ${isDarkMode ? 'text-orange-400' : 'text-orange-600'}`}>Recommended</span>
                              ) : (
                                <span className={`text-xs ${textSecondary}`}>-</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* 5. Department Breakdown */}
              {activeSection === 'departments' && report.department_breakdown && (
                <div className={`${bgCard} border ${borderColor} rounded-xl p-6`}>
                  <h3 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Department Risk Breakdown</h3>
                  <div className="space-y-4">
                    {report.department_breakdown.map((dept, index) => (
                      <div key={index} className={`p-4 rounded-lg border ${borderColor}`}>
                        <div className="flex items-center justify-between mb-3">
                          <h4 className={`font-semibold ${textPrimary}`}>{dept.department}</h4>
                          <span className={`px-3 py-1 rounded-lg text-xs font-semibold ${getRiskLevelColor(dept.risk_level)}`}>
                            {dept.risk_level.toUpperCase()} RISK
                          </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                          <div>
                            <p className={`text-xs ${textSecondary}`}>Employees</p>
                            <p className={`text-lg font-semibold ${textPrimary}`}>{dept.total_employees}</p>
                          </div>
                          <div>
                            <p className={`text-xs ${textSecondary}`}>Failed</p>
                            <p className={`text-lg font-semibold ${textPrimary}`}>{dept.failed_count}</p>
                          </div>
                          <div>
                            <p className={`text-xs ${textSecondary}`}>Failure Rate</p>
                            <p className={`text-lg font-semibold ${textPrimary}`}>{dept.failure_rate}%</p>
                          </div>
                          <div>
                            <p className={`text-xs ${textSecondary}`}>Need Training</p>
                            <p className={`text-lg font-semibold ${textPrimary}`}>{dept.training_needed}</p>
                          </div>
                        </div>
                        <div className="w-full bg-slate-600/20 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              dept.risk_level === 'critical' ? 'bg-red-500' :
                              dept.risk_level === 'high' ? 'bg-orange-500' :
                              dept.risk_level === 'medium' ? 'bg-yellow-500' :
                              'bg-green-500'
                            }`}
                            style={{ width: `${dept.failure_rate}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 6. Security Gaps */}
              {activeSection === 'gaps' && report.security_gaps && (
                <div>
                  <div className={`${bgCard} border ${borderColor} rounded-xl p-6 mb-6`}>
                    <h3 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Executive Summary</h3>
                    <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-slate-50'}`}>
                      <p className={textPrimary}>{report.security_gaps.summary}</p>
                    </div>
                  </div>

                  <div className={`${bgCard} border ${borderColor} rounded-xl p-6`}>
                    <h3 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Identified Security Gaps</h3>
                    <div className="space-y-4">
                      {report.security_gaps.gaps.map((gap, index) => (
                        <div key={index} className={`p-4 rounded-lg border ${getRiskLevelColor(gap.severity)}`}>
                          <div className="flex items-start gap-3">
                            <div className="flex-shrink-0">
                              {(gap.severity === 'critical' || gap.severity === 'high') && (
                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                              )}
                              {gap.severity === 'positive' && (
                                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                              )}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="text-xs font-semibold uppercase">{gap.category}</span>
                                <span className="text-xs opacity-75">•</span>
                                <span className="text-xs font-semibold uppercase">{gap.severity}</span>
                              </div>
                              <p className="font-medium mb-2">{gap.finding}</p>
                              <p className="text-sm opacity-90">{gap.recommendation}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// Program Card Component
const ProgramCard = ({ program, isDarkMode, onRefresh, onViewDetails, onDelete, onViewReport }) => {
  const getStatusColor = (status) => {
    const colors = {
      draft: 'bg-gray-500',
      scheduled: 'bg-yellow-500',
      active: 'bg-green-500',
      paused: 'bg-orange-500',
      completed: 'bg-blue-500'
    };
    return colors[status] || 'bg-gray-500';
  };

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete "${program.name}"?`)) {
      try {
        const response = await deleteProgram(program.id);
        console.log('Delete response:', response);
        onRefresh();
      } catch (error) {
        console.error('Error deleting program:', error);
        console.error('Error response:', error.response);
        const errorMsg = error.response?.data?.error || 'Failed to delete program';
        alert(errorMsg);
      }
    }
  };

  return (
    <div className={`rounded-lg p-6 border ${
      isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
    }`}>
      <div className="mb-4">
        <h3 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          {program.name}
        </h3>
      </div>
      <p className={`text-sm mb-4 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
        {program.description}
      </p>
      <div className="flex gap-2 flex-wrap mb-4">
        {program.vectors_to_test?.map((vector) => {
          const vectorInfo = VECTORS.find(v => v.id === vector);
          return (
            <span
              key={vector}
              className={`px-2 py-1 rounded text-xs ${
                isDarkMode ? 'bg-blue-900 text-blue-200' : 'bg-blue-100 text-blue-800'
              }`}
            >
              {vectorInfo?.icon} {vectorInfo?.name || vector}
            </span>
          );
        })}
      </div>
      <div className="flex flex-col gap-2">
        <button
          onClick={() => onViewDetails(program)}
          className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
            isDarkMode
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          }`}
        >
          View Details
        </button>
        <button
          onClick={() => onViewReport && onViewReport(program)}
          className={`w-full px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
            isDarkMode
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-green-500 hover:bg-green-600 text-white'
          }`}
        >
          <span>📊</span>
          Awareness Report
        </button>
        <button
          onClick={handleDelete}
          className={`w-full px-4 py-2 rounded-lg font-medium transition-colors ${
            isDarkMode
              ? 'bg-red-600 hover:bg-red-700 text-white'
              : 'bg-red-500 hover:bg-red-600 text-white'
          }`}
        >
          Delete
        </button>
      </div>
    </div>
  );
};

// Create Program Modal Component
const CreateProgramModal = ({ onClose, onSuccess, isDarkMode }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    vectors_to_test: [],
    email_config: null,
    qr_config: null,
    sms_config: null
  });

  const handleVectorToggle = (vectorId) => {
    setFormData(prev => {
      const isEnabled = prev.vectors_to_test.includes(vectorId);
      if (isEnabled) {
        // Disable vector
        return {
          ...prev,
          vectors_to_test: prev.vectors_to_test.filter(v => v !== vectorId),
          [`${vectorId}_config`]: null
        };
      } else {
        // Enable vector with initial config
        return {
          ...prev,
          vectors_to_test: [...prev.vectors_to_test, vectorId],
          [`${vectorId}_config`]: {}
        };
      }
    });
  };

  const handleVectorConfigChange = (vectorId, config) => {
    console.log(`[VECTOR CONFIG] Updating ${vectorId}_config with:`, config);
    setFormData(prev => {
      const newFormData = {
        ...prev,
        [`${vectorId}_config`]: config
      };
      console.log('[VECTOR CONFIG] New formData:', newFormData);
      return newFormData;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createProgram(formData);
      onSuccess();
    } catch (error) {
      console.error('Error creating program:', error);
      alert('Failed to create program');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className={`rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto ${
        isDarkMode ? 'bg-gray-800' : 'bg-white'
      }`}>
        <div className={`sticky top-0 p-6 border-b ${
          isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
        } z-10`}>
          <div className="flex justify-between items-center">
            <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Create Profiling Program
            </h2>
            <button
              onClick={onClose}
              className={`p-2 rounded-lg ${isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100'}`}
            >
              <span className="text-2xl">&times;</span>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Program Name */}
          <div>
            <label className={`block text-sm font-medium mb-2 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
              Program Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className={`w-full px-4 py-2 rounded-lg border ${
                isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
              placeholder="Q4 2024 Security Awareness Testing"
            />
          </div>

          {/* Program Description */}
          <div>
            <label className={`block text-sm font-medium mb-2 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
              Program Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className={`w-full px-4 py-2 rounded-lg border ${
                isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
              rows="3"
              placeholder="Comprehensive security awareness assessment across email, QR, and SMS vectors"
            />
          </div>

          {/* Attack Vectors */}
          <div>
            <label className={`block text-sm font-medium mb-3 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
              Attack Vectors *
            </label>
            <p className={`text-sm mb-4 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              Select and configure attack vectors for this program. Each vector can target different employees.
            </p>

            <div className="space-y-4">
              {VECTORS.map((vector) => (
                <VectorConfigSection
                  key={vector.id}
                  vector={vector}
                  enabled={formData.vectors_to_test.includes(vector.id)}
                  onToggle={() => handleVectorToggle(vector.id)}
                  config={formData[`${vector.id}_config`]}
                  onConfigChange={(config) => handleVectorConfigChange(vector.id, config)}
                  isDarkMode={isDarkMode}
                />
              ))}
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className={`px-6 py-2 rounded-lg ${
                isDarkMode ? 'bg-gray-700 text-white hover:bg-gray-600' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
              }`}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={formData.vectors_to_test.length === 0}
              className="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Program
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Vector Configuration Section
const VectorConfigSection = ({ vector, enabled, onToggle, config, onConfigChange, isDarkMode }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className={`border rounded-lg ${isDarkMode ? 'border-gray-700' : 'border-gray-300'} ${
      enabled ? 'bg-blue-50 dark:bg-blue-900/20' : ''
    }`}>
      <div className="p-4">
        <div className="flex items-center justify-between">
          <label className="flex items-center cursor-pointer flex-1">
            <input
              type="checkbox"
              checked={enabled}
              onChange={onToggle}
              className="rounded mr-3"
            />
            <div className="flex-1">
              <div className="flex items-center">
                <span className="text-2xl mr-2">{vector.icon}</span>
                <div>
                  <div className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{vector.name}</div>
                  <div className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>{vector.description}</div>
                </div>
              </div>
            </div>
          </label>

          {/* Collapse/Expand Button - Only show when enabled */}
          {enabled && (
            <button
              type="button"
              onClick={() => setIsExpanded(!isExpanded)}
              className={`ml-2 p-2 rounded-lg transition-colors ${
                isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-200'
              }`}
              aria-label={isExpanded ? 'Collapse' : 'Expand'}
            >
              <svg
                className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''} ${
                  isDarkMode ? 'text-gray-400' : 'text-gray-600'
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          )}
        </div>

        {/* Configuration Section - Only show when enabled AND expanded */}
        {enabled && isExpanded && (
          <div className={`mt-4 pt-4 border-t ${isDarkMode ? 'border-gray-700' : 'border-gray-300'}`}>
            {vector.id === 'email' && (
              <EmailVectorConfig config={config} onChange={onConfigChange} isDarkMode={isDarkMode} />
            )}
            {vector.id === 'qr' && (
              <QRVectorConfig config={config} onChange={onConfigChange} isDarkMode={isDarkMode} />
            )}
            {vector.id === 'sms' && (
              <SMSVectorConfig config={config} onChange={onConfigChange} isDarkMode={isDarkMode} />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Email Vector Configuration Component
const EmailVectorConfig = ({ config, onChange, isDarkMode }) => {
  const [templates, setTemplates] = useState([]);
  const [landingPages, setLandingPages] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [uploadMethod, setUploadMethod] = useState('employees');
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [employeeFilter, setEmployeeFilter] = useState({ department: '', search: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [templatesRes, landingPagesRes, employeesRes, deptsRes] = await Promise.all([
        getTemplates(),
        getLandingPages(),
        getEmployees(),
        getEmployeeDepartments()
      ]);
      setTemplates(templatesRes.data || []);
      setLandingPages(landingPagesRes.data?.filter(p => p.is_active) || []);
      setEmployees(employeesRes.data.employees || employeesRes.data || []);
      setDepartments(deptsRes.data.departments || deptsRes.data || []);
    } catch (error) {
      console.error('Error loading email config data:', error);
    }
  };

  useEffect(() => {
    // Update config when uploadMethod or filters change (for employees mode)
    if (uploadMethod === 'employees') {
      onChange({
        ...config,
        target_selection: 'employees',
        search_query: employeeFilter.search,
        selected_department: employeeFilter.department
      });
    }
  }, [uploadMethod, employeeFilter]);

  const toggleEmployee = (employee) => {
    setSelectedEmployees(prev => {
      const exists = prev.find(e => e.id === employee.id);
      if (exists) {
        return prev.filter(e => e.id !== employee.id);
      } else {
        return [...prev, employee];
      }
    });
  };

  const selectAllFiltered = () => {
    const filtered = getFilteredEmployees();
    setSelectedEmployees(prev => {
      const newSelected = [...prev];
      filtered.forEach(emp => {
        if (!newSelected.find(e => e.id === emp.id)) {
          newSelected.push(emp);
        }
      });
      return newSelected;
    });
  };

  const deselectAll = () => {
    setSelectedEmployees([]);
  };

  const getFilteredEmployees = () => {
    return employees.filter(emp => {
      const matchesDept = !employeeFilter.department || emp.department === employeeFilter.department;
      const matchesSearch = !employeeFilter.search ||
        emp.email?.toLowerCase().includes(employeeFilter.search.toLowerCase()) ||
        emp.full_name?.toLowerCase().includes(employeeFilter.search.toLowerCase()) ||
        emp.name?.toLowerCase().includes(employeeFilter.search.toLowerCase());
      return matchesDept && matchesSearch;
    });
  };

  return (
    <div className="space-y-4">
      <div>
        <label className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
          Email Template *
        </label>
        <select
          required
          value={config?.template_id || ''}
          onChange={(e) => onChange({ ...config, template_id: e.target.value })}
          className={`w-full px-3 py-2 rounded-lg border ${
            isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
          }`}
        >
          <option value="" className={isDarkMode ? 'text-gray-400' : 'text-gray-500'}>Select template...</option>
          {templates.map((template) => (
            <option key={template.id} value={template.id} className={isDarkMode ? 'text-white bg-gray-700' : 'text-gray-900 bg-white'}>
              {template.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
          Landing Page (Optional)
        </label>
        <select
          value={config?.landing_page_id || ''}
          onChange={(e) => onChange({ ...config, landing_page_id: e.target.value })}
          className={`w-full px-3 py-2 rounded-lg border ${
            isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
          }`}
        >
          <option value="" className={isDarkMode ? 'text-gray-400' : 'text-gray-500'}>None</option>
          {landingPages.map((page) => (
            <option key={page.id} value={page.id} className={isDarkMode ? 'text-white bg-gray-700' : 'text-gray-900 bg-white'}>
              {page.name}
            </option>
          ))}
        </select>
      </div>

      {/* Target Employees */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
          Target Employees *
        </label>

        {/* Upload Method Tabs */}
        <div className="flex gap-2 mb-3">
          {['employees', 'manual', 'csv'].map((method) => (
            <button
              key={method}
              type="button"
              onClick={() => setUploadMethod(method)}
              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                uploadMethod === method
                  ? 'bg-blue-600 text-white'
                  : isDarkMode
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {method === 'employees' ? 'Select Employees' : method === 'manual' ? 'Manual Entry' : 'Upload CSV'}
            </button>
          ))}
        </div>

        {uploadMethod === 'employees' && (
          <>
            {/* Filters and Actions */}
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                placeholder="Search employees..."
                value={employeeFilter.search}
                onChange={(e) => setEmployeeFilter({ ...employeeFilter, search: e.target.value })}
                className={`flex-1 px-3 py-2 rounded-lg border ${
                  isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
                }`}
              />
              <select
                value={employeeFilter.department}
                onChange={(e) => setEmployeeFilter({ ...employeeFilter, department: e.target.value })}
                className={`px-3 py-2 rounded-lg border ${
                  isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
                }`}
              >
                <option value="">All Departments</option>
                {departments.map((dept) => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={selectAllFiltered}
                className={`px-4 py-2 rounded-lg text-sm ${
                  isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'
                }`}
              >
                Select All
              </button>
            </div>

            {/* Employee List */}
            <div className={`border rounded-lg max-h-64 overflow-y-auto ${
              isDarkMode ? 'border-gray-600' : 'border-gray-300'
            }`}>
              {getFilteredEmployees().map((emp) => {
                const isSelected = selectedEmployees.find(e => e.id === emp.id);
                return (
                  <div
                    key={emp.id}
                    onClick={() => toggleEmployee(emp)}
                    className={`flex items-center p-3 cursor-pointer transition-colors ${
                      isSelected
                        ? isDarkMode ? 'bg-blue-900/30' : 'bg-blue-50'
                        : isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'
                    } border-b last:border-b-0 ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}
                  >
                    <div className={`w-5 h-5 rounded border-2 mr-3 flex items-center justify-center ${
                      isSelected ? 'bg-blue-600 border-blue-600' : 'border-gray-400'
                    }`}>
                      {isSelected && (
                        <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`font-medium text-sm truncate ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                        {emp.full_name || emp.name}
                      </p>
                      <p className={`text-xs truncate ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        {emp.email}
                      </p>
                    </div>
                    {emp.department && (
                      <span className={`ml-2 px-2 py-1 rounded text-xs ${
                        isDarkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-700'
                      }`}>
                        {emp.department}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>

            {selectedEmployees.length > 0 && (
              <div className="mt-3 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                <div className="flex justify-between items-center">
                  <span className="text-blue-600 text-sm font-medium">
                    {selectedEmployees.length} employee(s) selected
                  </span>
                  <button
                    type="button"
                    onClick={deselectAll}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    Clear
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {uploadMethod === 'manual' && (
          <div>
            <textarea
              placeholder="Enter name, email, and department, one per line (format: Name, email@example.com, Department):&#10;John Doe, john@example.com, IT&#10;Jane Smith, jane@example.com, HR&#10;Bob Wilson, bob@example.com, Finance"
              value={config?.manual_emails || ''}
              onChange={(e) => {
                onChange({
                  ...config,
                  target_selection: 'manual',
                  manual_emails: e.target.value
                });
              }}
              className={`w-full px-3 py-2 rounded-lg border min-h-[150px] ${
                isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
            />
            <p className={`text-xs mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Enter name, email, and department, one per line (format: Name, email@example.com, Department)
            </p>
          </div>
        )}

        {uploadMethod === 'csv' && (
          <div>
            <div className={`border-2 border-dashed rounded-lg p-6 text-center ${
              isDarkMode ? 'border-gray-600 bg-gray-700/50' : 'border-gray-300 bg-gray-50'
            }`}>
              <input
                type="file"
                id="csv-upload-email"
                accept=".csv,.txt"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      const csvContent = event.target.result;
                      onChange({
                        ...config,
                        target_selection: 'csv',
                        csv_content: csvContent,
                        csv_filename: file.name
                      });
                    };
                    reader.readAsText(file);
                  }
                }}
                className="hidden"
              />
              <label
                htmlFor="csv-upload-email"
                className={`cursor-pointer inline-flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                  isDarkMode
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Choose CSV File
              </label>
              {config?.csv_filename && (
                <div className="mt-3">
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-green-400' : 'text-green-600'}`}>
                    ✓ {config.csv_filename}
                  </p>
                  <button
                    type="button"
                    onClick={() => onChange({ ...config, csv_content: '', csv_filename: '', target_selection: 'employees' })}
                    className={`text-xs mt-1 ${isDarkMode ? 'text-red-400 hover:text-red-300' : 'text-red-600 hover:text-red-700'}`}
                  >
                    Remove file
                  </button>
                </div>
              )}
            </div>
            <p className={`text-xs mt-2 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              CSV format: email,first_name,last_name (optional)
              <br />
              Example: user@example.com,John,Doe
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// QR Vector Configuration Component
const QRVectorConfig = ({ config, onChange, isDarkMode }) => {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [qrCampaigns, setQrCampaigns] = useState([]);
  const [uploadMethod, setUploadMethod] = useState('employees');
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [employeeFilter, setEmployeeFilter] = useState({ department: '', search: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [employeesRes, deptsRes, qrRes] = await Promise.all([
        getEmployees(),
        getEmployeeDepartments(),
        getQRCampaigns()
      ]);
      setEmployees(employeesRes.data.employees || employeesRes.data || []);
      setDepartments(deptsRes.data.departments || deptsRes.data || []);
      setQrCampaigns(qrRes.data || []);
    } catch (error) {
      console.error('Error loading QR config data:', error);
    }
  };

  useEffect(() => {
    if (uploadMethod === 'employees' && selectedEmployees.length > 0) {
      onChange({
        ...config,
        target_selection: 'employees',
        target_employees: selectedEmployees.map(e => e.id)
      });
    }
  }, [selectedEmployees, uploadMethod]);

  const toggleEmployee = (employee) => {
    setSelectedEmployees(prev => {
      const exists = prev.find(e => e.id === employee.id);
      if (exists) {
        return prev.filter(e => e.id !== employee.id);
      } else {
        return [...prev, employee];
      }
    });
  };

  const selectAllFiltered = () => {
    const filtered = getFilteredEmployees();
    setSelectedEmployees(prev => {
      const newSelected = [...prev];
      filtered.forEach(emp => {
        if (!newSelected.find(e => e.id === emp.id)) {
          newSelected.push(emp);
        }
      });
      return newSelected;
    });
  };

  const deselectAll = () => {
    setSelectedEmployees([]);
  };

  const getFilteredEmployees = () => {
    return employees.filter(emp => {
      const matchesDept = !employeeFilter.department || emp.department === employeeFilter.department;
      const matchesSearch = !employeeFilter.search ||
        emp.email?.toLowerCase().includes(employeeFilter.search.toLowerCase()) ||
        emp.full_name?.toLowerCase().includes(employeeFilter.search.toLowerCase()) ||
        emp.name?.toLowerCase().includes(employeeFilter.search.toLowerCase());
      return matchesDept && matchesSearch;
    });
  };

  return (
    <div className="space-y-4">
      {/* Select Existing QR Poster */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
          Select QR Code Poster *
        </label>
        <select
          value={config?.qr_campaign_id || ''}
          onChange={(e) => onChange({ ...config, qr_campaign_id: e.target.value })}
          className={`w-full px-3 py-2 rounded-lg border ${
            isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
          }`}
          required
        >
          <option value="">-- Select a QR Code Poster --</option>
          {qrCampaigns.map((qr) => (
            <option key={qr.id} value={qr.id}>
              {qr.name} {qr.description ? `- ${qr.description}` : ''}
            </option>
          ))}
        </select>
        <p className={`mt-1 text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          Choose from posters created in Campaigns → QR Phishing menu
        </p>
      </div>

      {/* Target Employees - Same structure as Email */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
          Target Employees *
        </label>

        <div className="flex gap-2 mb-3">
          {['employees', 'manual', 'csv'].map((method) => (
            <button
              key={method}
              type="button"
              onClick={() => setUploadMethod(method)}
              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                uploadMethod === method
                  ? 'bg-blue-600 text-white'
                  : isDarkMode
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {method === 'employees' ? 'Select Employees' : method === 'manual' ? 'Manual Entry' : 'Upload CSV'}
            </button>
          ))}
        </div>

        {uploadMethod === 'employees' && (
          <>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                placeholder="Search employees..."
                value={employeeFilter.search}
                onChange={(e) => setEmployeeFilter({ ...employeeFilter, search: e.target.value })}
                className={`flex-1 px-3 py-2 rounded-lg border ${
                  isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
                }`}
              />
              <select
                value={employeeFilter.department}
                onChange={(e) => setEmployeeFilter({ ...employeeFilter, department: e.target.value })}
                className={`px-3 py-2 rounded-lg border ${
                  isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
                }`}
              >
                <option value="">All Departments</option>
                {departments.map((dept) => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={selectAllFiltered}
                className={`px-4 py-2 rounded-lg text-sm ${
                  isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'
                }`}
              >
                Select All
              </button>
            </div>

            <div className={`border rounded-lg max-h-64 overflow-y-auto ${
              isDarkMode ? 'border-gray-600' : 'border-gray-300'
            }`}>
              {getFilteredEmployees().map((emp) => {
                const isSelected = selectedEmployees.find(e => e.id === emp.id);
                return (
                  <div
                    key={emp.id}
                    onClick={() => toggleEmployee(emp)}
                    className={`flex items-center p-3 cursor-pointer transition-colors ${
                      isSelected
                        ? isDarkMode ? 'bg-blue-900/30' : 'bg-blue-50'
                        : isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'
                    } border-b last:border-b-0 ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}
                  >
                    <div className={`w-5 h-5 rounded border-2 mr-3 flex items-center justify-center ${
                      isSelected ? 'bg-blue-600 border-blue-600' : 'border-gray-400'
                    }`}>
                      {isSelected && (
                        <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`font-medium text-sm truncate ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                        {emp.full_name || emp.name}
                      </p>
                      <p className={`text-xs truncate ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        {emp.email}
                      </p>
                    </div>
                    {emp.department && (
                      <span className={`ml-2 px-2 py-1 rounded text-xs ${
                        isDarkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-700'
                      }`}>
                        {emp.department}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>

            {selectedEmployees.length > 0 && (
              <div className="mt-3 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                <div className="flex justify-between items-center">
                  <span className="text-blue-600 text-sm font-medium">
                    {selectedEmployees.length} employee(s) selected
                  </span>
                  <button
                    type="button"
                    onClick={deselectAll}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    Clear
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {uploadMethod === 'manual' && (
          <div>
            <textarea
              placeholder="Enter name, email, and department, one per line (format: Name, email@example.com, Department):&#10;John Doe, john@example.com, IT&#10;Jane Smith, jane@example.com, HR&#10;Bob Wilson, bob@example.com, Finance"
              value={config?.manual_emails || ''}
              onChange={(e) => {
                console.log('[QR MANUAL] Text changed:', e.target.value);
                onChange({
                  ...config,
                  manual_emails: e.target.value,
                  target_selection: 'manual'
                });
              }}
              rows={6}
              className={`w-full px-3 py-2 rounded-lg border font-mono text-sm ${
                isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
            />
            <p className={`mt-2 text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Enter one employee per line in the format: Name, email@example.com, Department
            </p>
          </div>
        )}

        {uploadMethod === 'csv' && (
          <div>
            <div className={`border-2 border-dashed rounded-lg p-6 text-center ${
              isDarkMode ? 'border-gray-600' : 'border-gray-300'
            }`}>
              <input
                type="file"
                accept=".csv,.txt"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      const csvContent = event.target.result;
                      onChange({
                        ...config,
                        target_selection: 'csv',
                        csv_data: csvContent,
                        csv_filename: file.name
                      });
                    };
                    reader.readAsText(file);
                  }
                }}
                className="hidden"
                id="qr-csv-upload"
              />
              <label
                htmlFor="qr-csv-upload"
                className={`cursor-pointer inline-flex items-center px-4 py-2 rounded-lg ${
                  isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'
                }`}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Choose CSV File
              </label>
              {config?.csv_filename && (
                <p className={`mt-2 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                  Selected: {config.csv_filename}
                </p>
              )}
            </div>
            <p className={`mt-2 text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              CSV should have columns: name, email, department
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// SMS Vector Configuration Component
const SMSVectorConfig = ({ config, onChange, isDarkMode }) => {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [smsTemplates, setSmsTemplates] = useState([]);
  const [uploadMethod, setUploadMethod] = useState('employees');
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [employeeFilter, setEmployeeFilter] = useState({ department: '', search: '' });
  const [senderType, setSenderType] = useState('none');

  // Ensure config is always an object
  const safeConfig = config || {};

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [employeesRes, deptsRes, templatesRes] = await Promise.all([
        getEmployees(),
        getEmployeeDepartments(),
        getSMSTemplates()
      ]);
      setEmployees(employeesRes.data.employees || employeesRes.data || []);
      setDepartments(deptsRes.data.departments || deptsRes.data || []);

      // SMS templates come directly as an array
      const templates = Array.isArray(templatesRes.data) ? templatesRes.data : (templatesRes.data?.templates || []);
      console.log('Loaded SMS templates:', templates);
      setSmsTemplates(templates);
    } catch (error) {
      console.error('Error loading SMS config data:', error);
    }
  };

  useEffect(() => {
    if (selectedEmployees.length > 0) {
      onChange({
        ...config,
        target_employees: selectedEmployees.map(e => e.id)
      });
    }
  }, [selectedEmployees]);

  // Update config when uploadMethod or filters change (for employees mode)
  useEffect(() => {
    if (uploadMethod === 'employees') {
      onChange({
        ...safeConfig,
        target_selection: 'employees',
        search_query: employeeFilter.search,
        selected_department: employeeFilter.department
      });
    }
  }, [uploadMethod, employeeFilter]);

  const toggleEmployee = (employee) => {
    setSelectedEmployees(prev => {
      const exists = prev.find(e => e.id === employee.id);
      if (exists) {
        return prev.filter(e => e.id !== employee.id);
      } else {
        return [...prev, employee];
      }
    });
  };

  const selectAllFiltered = () => {
    const filtered = getFilteredEmployees();
    setSelectedEmployees(prev => {
      const newSelected = [...prev];
      filtered.forEach(emp => {
        if (!newSelected.find(e => e.id === emp.id)) {
          newSelected.push(emp);
        }
      });
      return newSelected;
    });
  };

  const deselectAll = () => {
    setSelectedEmployees([]);
  };

  const getFilteredEmployees = () => {
    return employees.filter(emp => {
      const matchesDept = !employeeFilter.department || emp.department === employeeFilter.department;
      const matchesSearch = !employeeFilter.search ||
        emp.email?.toLowerCase().includes(employeeFilter.search.toLowerCase()) ||
        emp.full_name?.toLowerCase().includes(employeeFilter.search.toLowerCase()) ||
        emp.name?.toLowerCase().includes(employeeFilter.search.toLowerCase());
      return matchesDept && matchesSearch;
    });
  };

  const applyTemplate = (template) => {
    const templateMessage = template.message || template.content || template.text || '';
    console.log('[SMS TEMPLATE] Applying template:', template.name, 'Message:', templateMessage);

    // Directly update parent config
    if (typeof onChange === 'function') {
      onChange({
        ...safeConfig,
        message_template: templateMessage
      });
    }
  };

  return (
    <div className="space-y-4">
      {/* Sender Type */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
          Sender Display Name (Optional)
        </label>
        <p className={`text-xs mb-3 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          Leave blank to use your Twilio phone number. Or choose a company name or custom sender ID.
        </p>
        <div className="flex gap-4 mb-3">
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              checked={senderType === 'none'}
              onChange={() => {
                setSenderType('none');
                onChange({ ...safeConfig, sender_id: '' });
              }}
              className="mr-2"
            />
            <span className={isDarkMode ? 'text-gray-200' : 'text-gray-700'}>Use Twilio Number</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              checked={senderType === 'company'}
              onChange={() => {
                setSenderType('company');
                onChange({ ...safeConfig, sender_id: 'Birbank' });
              }}
              className="mr-2"
            />
            <span className={isDarkMode ? 'text-gray-200' : 'text-gray-700'}>Company Name</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              checked={senderType === 'custom'}
              onChange={() => {
                setSenderType('custom');
                onChange({ ...safeConfig, sender_id: '' });
              }}
              className="mr-2"
            />
            <span className={isDarkMode ? 'text-gray-200' : 'text-gray-700'}>Custom</span>
          </label>
        </div>

        {senderType === 'company' && (
          <div>
            <label className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
              Azerbaijan Company
            </label>
            <select
              value={safeConfig.sender_id || 'Birbank'}
              onChange={(e) => onChange({ ...safeConfig, sender_id: e.target.value })}
              className={`w-full px-3 py-2 rounded-lg border ${
                isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              {AZERBAIJAN_COMPANIES.map((company) => (
                <option key={company} value={company} className={isDarkMode ? 'text-white bg-gray-700' : 'text-gray-900 bg-white'}>
                  {company}
                </option>
              ))}
            </select>
            <p className={`text-xs mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              SMS will appear from this company name
            </p>
          </div>
        )}

        {senderType === 'custom' && (
          <input
            type="text"
            placeholder="Custom sender (max 11 chars)"
            maxLength={11}
            value={safeConfig.sender_id || ''}
            onChange={(e) => onChange({ ...safeConfig, sender_id: e.target.value })}
            className={`w-full px-3 py-2 rounded-lg border ${
              isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
            }`}
          />
        )}
      </div>

      {/* Quick Templates */}
      {smsTemplates.length > 0 && (
        <div>
          <label className={`block text-sm font-medium mb-2 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
            Quick Templates
          </label>
          <div className="flex flex-wrap gap-2">
            {smsTemplates.slice(0, 4).map((template) => (
              <button
                key={template.id}
                type="button"
                onClick={() => applyTemplate(template)}
                className={`px-3 py-1 rounded text-sm ${
                  isDarkMode
                    ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                }`}
              >
                {template.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Message Template */}
      <div>
        <label className={`block text-sm font-medium mb-1 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
          Message Template *
        </label>
        <textarea
          required
          value={safeConfig.message_template || ''}
          onChange={(e) => {
            console.log('[SMS TEXTAREA] onChange triggered, value:', e.target.value);
            if (typeof onChange === 'function') {
              onChange({ ...safeConfig, message_template: e.target.value });
            } else {
              console.error('[SMS TEXTAREA] onChange is not a function!');
            }
          }}
          className={`w-full px-3 py-2 rounded-lg border min-h-[100px] ${
            isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
          }`}
          placeholder="Your account has been suspended. Verify now: {{link}}"
        />
        <p className={`text-xs mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          Use <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">{'{{link}}'}</code> for the tracking link and <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">{'{{name}}'}</code> for recipient name
        </p>
      </div>

      {/* Target Employees */}
      <div>
        <label className={`block text-sm font-medium mb-2 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
          Target Employees *
        </label>

        <div className="flex gap-2 mb-3">
          {['employees', 'manual', 'csv'].map((method) => (
            <button
              key={method}
              type="button"
              onClick={() => setUploadMethod(method)}
              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                uploadMethod === method
                  ? 'bg-blue-600 text-white'
                  : isDarkMode
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {method === 'employees' ? 'Select Employees' : method === 'manual' ? 'Manual Entry' : 'Upload CSV'}
            </button>
          ))}
        </div>

        {uploadMethod === 'employees' && (
          <>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                placeholder="Search employees..."
                value={employeeFilter.search}
                onChange={(e) => setEmployeeFilter({ ...employeeFilter, search: e.target.value })}
                className={`flex-1 px-3 py-2 rounded-lg border ${
                  isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
                }`}
              />
              <select
                value={employeeFilter.department}
                onChange={(e) => setEmployeeFilter({ ...employeeFilter, department: e.target.value })}
                className={`px-3 py-2 rounded-lg border ${
                  isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
                }`}
              >
                <option value="">All Departments</option>
                {departments.map((dept) => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={selectAllFiltered}
                className={`px-4 py-2 rounded-lg text-sm ${
                  isDarkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'
                }`}
              >
                Select All
              </button>
            </div>

            <div className={`border rounded-lg max-h-64 overflow-y-auto ${
              isDarkMode ? 'border-gray-600' : 'border-gray-300'
            }`}>
              {getFilteredEmployees().map((emp) => {
                const isSelected = selectedEmployees.find(e => e.id === emp.id);
                return (
                  <div
                    key={emp.id}
                    onClick={() => toggleEmployee(emp)}
                    className={`flex items-center p-3 cursor-pointer transition-colors ${
                      isSelected
                        ? isDarkMode ? 'bg-blue-900/30' : 'bg-blue-50'
                        : isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'
                    } border-b last:border-b-0 ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}
                  >
                    <div className={`w-5 h-5 rounded border-2 mr-3 flex items-center justify-center ${
                      isSelected ? 'bg-blue-600 border-blue-600' : 'border-gray-400'
                    }`}>
                      {isSelected && (
                        <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`font-medium text-sm truncate ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                        {emp.full_name || emp.name}
                      </p>
                      <p className={`text-xs truncate ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        {emp.email}
                      </p>
                    </div>
                    {emp.department && (
                      <span className={`ml-2 px-2 py-1 rounded text-xs ${
                        isDarkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-700'
                      }`}>
                        {emp.department}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>

            {selectedEmployees.length > 0 && (
              <div className="mt-3 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                <div className="flex justify-between items-center">
                  <span className="text-blue-600 text-sm font-medium">
                    {selectedEmployees.length} employee(s) selected
                  </span>
                  <button
                    type="button"
                    onClick={deselectAll}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    Clear
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {uploadMethod === 'manual' && (
          <div>
            <textarea
              placeholder="Enter name, phone number, and department, one per line (format: Name, +994501234567, Department):&#10;John Doe, +994501234567, IT&#10;Jane Smith, +994551234568, HR&#10;Bob Wilson, +994701234569, Finance"
              value={safeConfig.manual_numbers || ''}
              onChange={(e) => {
                const numbers = e.target.value;
                onChange({
                  ...safeConfig,
                  target_selection: 'manual',
                  manual_numbers: numbers
                });
              }}
              className={`w-full px-3 py-2 rounded-lg border min-h-[150px] ${
                isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900'
              }`}
            />
            <p className={`text-xs mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              Enter name, phone number, and department in international format, one per line (format: Name, +994501234567, Department)
            </p>
          </div>
        )}

        {uploadMethod === 'csv' && (
          <div>
            <div className={`border-2 border-dashed rounded-lg p-6 text-center ${
              isDarkMode ? 'border-gray-600 bg-gray-700/50' : 'border-gray-300 bg-gray-50'
            }`}>
              <input
                type="file"
                id="csv-upload-sms"
                accept=".csv,.txt"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      const csvContent = event.target.result;
                      onChange({
                        ...safeConfig,
                        target_selection: 'csv',
                        csv_content: csvContent,
                        csv_filename: file.name
                      });
                    };
                    reader.readAsText(file);
                  }
                }}
                className="hidden"
              />
              <label
                htmlFor="csv-upload-sms"
                className={`cursor-pointer inline-flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                  isDarkMode
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Choose CSV File
              </label>
              {safeConfig.csv_filename && (
                <div className="mt-3">
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-green-400' : 'text-green-600'}`}>
                    ✓ {safeConfig.csv_filename}
                  </p>
                  <button
                    type="button"
                    onClick={() => onChange({ ...safeConfig, target_selection: 'employees', csv_content: '', csv_filename: '' })}
                    className={`text-xs mt-1 ${isDarkMode ? 'text-red-400 hover:text-red-300' : 'text-red-600 hover:text-red-700'}`}
                  >
                    Remove file
                  </button>
                </div>
              )}
            </div>
            <p className={`text-xs mt-2 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              CSV format: phone,name (optional)
              <br />
              Example: +994501234567,John Doe
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilingProgramManager;
