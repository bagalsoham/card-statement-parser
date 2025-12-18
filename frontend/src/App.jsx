import React, { useState, useEffect } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Clock, CreditCard, Calendar, DollarSign, Server, Loader } from 'lucide-react';

export default function CreditCardParser() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [backendStatus, setBackendStatus] = useState(null);
  const [supportedIssuers, setSupportedIssuers] = useState([]);

  const API_BASE_URL = 'http://localhost:8000';

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
    fetchSupportedIssuers();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      setBackendStatus(data);
    } catch (err) {
      setBackendStatus({ status: 'offline' });
    }
  };

  const fetchSupportedIssuers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/supported-issuers`);
      const data = await response.json();
      setSupportedIssuers(data.issuers || []);
    } catch (err) {
      console.error('Failed to fetch supported issuers');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Please select a valid PDF file');
      setFile(null);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    if (backendStatus?.status === 'offline') {
      setError('Backend server is offline. Please start the backend first.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/parse-statement`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setResult(data);
      } else {
        setError(data.errors?.join(', ') || 'Failed to parse statement');
      }
    } catch (err) {
      setError('Network error. Please ensure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusColor = () => {
    if (!backendStatus) return 'bg-gray-400';
    if (backendStatus.status === 'healthy') return 'bg-green-500';
    return 'bg-red-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header with Backend Status */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CreditCard className="w-8 h-8 text-indigo-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Credit Card Statement Parser</h1>
                <p className="text-sm text-gray-500">AI-powered extraction with multi-strategy parsing</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${getStatusColor()} animate-pulse`}></div>
              <span className="text-sm text-gray-600">
                {backendStatus ? (backendStatus.status === 'healthy' ? 'Backend Online' : 'Backend Offline') : 'Checking...'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
        {/* Supported Issuers Info */}
        {supportedIssuers.length > 0 && (
          <div className="mb-6 bg-white rounded-lg shadow-sm border border-indigo-100 p-4">
            <div className="flex items-start">
              <Server className="w-5 h-5 text-indigo-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Supported Issuers ({supportedIssuers.length})</h3>
                <div className="flex flex-wrap gap-2">
                  {supportedIssuers.map((issuer) => (
                    <span key={issuer} className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-medium">
                      {issuer}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Upload Section */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-1">Upload Statement</h2>
            <p className="text-sm text-gray-500">Upload your credit card statement PDF for automatic data extraction</p>
          </div>

          <div
            className={`border-2 border-dashed rounded-xl p-10 text-center transition-all duration-200 ${
              dragActive 
                ? 'border-indigo-500 bg-indigo-50 scale-105' 
                : 'border-gray-300 hover:border-indigo-400 hover:bg-gray-50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="flex flex-col items-center">
              {dragActive ? (
                <Upload className="w-16 h-16 text-indigo-500 mb-4 animate-bounce" />
              ) : (
                <Upload className="w-16 h-16 text-gray-400 mb-4" />
              )}
              
              <p className="text-lg font-medium text-gray-700 mb-2">
                {file ? (
                  <span className="text-indigo-600">{file.name}</span>
                ) : (
                  'Drag and drop your PDF here'
                )}
              </p>
              
              <p className="text-sm text-gray-500 mb-4">
                {file ? `${(file.size / 1024).toFixed(2)} KB` : 'or click to browse'}
              </p>
              
              <label className="inline-block cursor-pointer">
                <span className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-md hover:shadow-lg inline-flex items-center space-x-2">
                  <FileText className="w-5 h-5" />
                  <span>{file ? 'Change File' : 'Browse Files'}</span>
                </span>
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf"
                  onChange={handleFileInput}
                />
              </label>
            </div>
          </div>

          {file && (
            <div className="mt-6 p-4 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg border border-indigo-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-white rounded-lg">
                    <FileText className="w-6 h-6 text-indigo-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{file.name}</p>
                    <p className="text-sm text-gray-600">{(file.size / 1024).toFixed(2)} KB • PDF Document</p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setFile(null);
                    setResult(null);
                    setError(null);
                  }}
                  className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors"
                >
                  Remove
                </button>
              </div>
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={!file || loading || backendStatus?.status !== 'healthy'}
            className="w-full mt-6 py-4 px-6 bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-none flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Parsing Statement...</span>
              </>
            ) : (
              <>
                <CreditCard className="w-5 h-5" />
                <span>Parse Statement</span>
              </>
            )}
          </button>

          {error && (
            <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg">
              <div className="flex items-start">
                <AlertCircle className="w-5 h-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-900">Error</p>
                  <p className="text-red-700 text-sm mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Section */}
        {result && result.success && (
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 animate-fadeIn">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <CheckCircle className="w-7 h-7 text-green-600" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Parsing Results</h2>
                  <p className="text-sm text-gray-500">Extraction completed successfully</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Overall Confidence</p>
                <div className="flex items-center justify-end space-x-2">
                  <div className={`text-3xl font-bold ${getConfidenceColor(result.data.overall_confidence)}`}>
                    {(result.data.overall_confidence * 100).toFixed(0)}%
                  </div>
                  <div className="w-12 h-12 rounded-full border-4 flex items-center justify-center" style={{
                    borderColor: result.data.overall_confidence >= 0.8 ? '#16a34a' : result.data.overall_confidence >= 0.5 ? '#eab308' : '#dc2626'
                  }}>
                    <span className="text-xs font-semibold" style={{
                      color: result.data.overall_confidence >= 0.8 ? '#16a34a' : result.data.overall_confidence >= 0.5 ? '#eab308' : '#dc2626'
                    }}>
                      {result.data.overall_confidence >= 0.8 ? 'High' : result.data.overall_confidence >= 0.5 ? 'Med' : 'Low'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {result.data.fallback_used && (
              <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start">
                <AlertCircle className="w-5 h-5 text-yellow-600 mr-3 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-yellow-900">LLM Fallback Used</p>
                  <p className="text-sm text-yellow-700 mt-1">AI-powered extraction was used for better accuracy</p>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <DataField
                icon={<Server className="w-5 h-5" />}
                label="Card Issuer"
                field={result.data.issuer}
              />
              <DataField
                icon={<CreditCard className="w-5 h-5" />}
                label="Card Last 4 Digits"
                field={result.data.card_last_4}
              />
              <DataField
                icon={<Calendar className="w-5 h-5" />}
                label="Statement Period"
                field={result.data.statement_period}
                fullWidth
              />
              <DataField
                icon={<Calendar className="w-5 h-5" />}
                label="Payment Due Date"
                field={result.data.due_date}
              />
              <DataField
                icon={<DollarSign className="w-5 h-5" />}
                label="Total Amount Due"
                field={result.data.total_amount_due}
                highlight
              />
            </div>

            {result.data.parsing_errors && result.data.parsing_errors.length > 0 && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="font-semibold text-yellow-900 mb-2 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  Parsing Warnings
                </p>
                <ul className="space-y-1">
                  {result.data.parsing_errors.map((err, idx) => (
                    <li key={idx} className="text-sm text-yellow-800 flex items-start">
                      <span className="mr-2">•</span>
                      <span>{err}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between">
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  <span>{result.processing_time_ms.toFixed(0)}ms</span>
                </div>
                <div className="flex items-center">
                  <Server className="w-4 h-4 mr-1" />
                  <span>v{backendStatus?.version || '2.0.0'}</span>
                </div>
              </div>
              <button
                onClick={() => {
                  setResult(null);
                  setFile(null);
                  setError(null);
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
              >
                Parse Another
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}

function DataField({ icon, label, field, highlight = false, fullWidth = false }) {
  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-700 border-green-200';
    if (confidence >= 0.5) return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    return 'bg-red-100 text-red-700 border-red-200';
  };

  const getMethodBadge = (method) => {
    const badges = {
      regex: 'bg-blue-100 text-blue-700',
      table: 'bg-purple-100 text-purple-700',
      layout: 'bg-pink-100 text-pink-700',
      llm: 'bg-indigo-100 text-indigo-700'
    };
    return badges[method] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className={`p-5 rounded-lg border transition-all duration-200 hover:shadow-md ${
      highlight 
        ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-200' 
        : 'bg-gray-50 border-gray-200'
    } ${fullWidth ? 'md:col-span-2' : ''}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center text-gray-700">
          <div className={`p-1.5 rounded-lg mr-2 ${highlight ? 'bg-green-200' : 'bg-white'}`}>
            {icon}
          </div>
          <span className="font-semibold text-sm">{label}</span>
        </div>
        <span className={`px-2 py-1 rounded-md text-xs font-semibold border ${getConfidenceBadge(field.confidence)}`}>
          {(field.confidence * 100).toFixed(0)}%
        </span>
      </div>
      <p className={`text-lg font-bold mb-2 ${highlight ? 'text-green-900' : 'text-gray-900'}`}>
        {field.value || 'Not Found'}
      </p>
      <div className="flex items-center space-x-2 text-xs">
        <span className={`px-2 py-1 rounded ${getMethodBadge(field.extraction_method)}`}>
          {field.extraction_method.toUpperCase()}
        </span>
        {field.raw_value && field.raw_value !== field.value && (
          <span className="text-gray-500">Raw: {field.raw_value}</span>
        )}
      </div>
    </div>
  );
}