import React, { useState, useEffect } from 'react';
import { AlertTriangle, Clock, CheckCircle, TrendingUp, List, Map as MapIcon, Loader2 } from 'lucide-react';
import { StatCard } from '../component/shared';

const API_URL = 'http://localhost:8000/api';

const Dashboard = () => {
  const [statistics, setStatistics] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
    // Refresh data every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Fetch statistics
      const statsRes = await fetch(`${API_URL}/statistics`);
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStatistics(statsData.statistics);
      } else {
        console.warn('Statistics endpoint returned:', statsRes.status);
      }

      // Fetch reports
      const reportsRes = await fetch(`${API_URL}/reports?limit=10`);
      if (reportsRes.ok) {
        const reportsData = await reportsRes.json();
        // Backend returns 'data' field, not 'reports'
        setReports(reportsData.data || reportsData.reports || []);
      } else {
        console.warn('Reports endpoint returned:', reportsRes.status);
      }

      setError(null);
    } catch (err) {
      setError(`Failed to fetch data: ${err.message}`);
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !statistics) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20">
      {/* Error Message */}
      {error && (
        <div className="w-full bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-red-700 font-semibold text-sm">{error}</p>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        <StatCard 
          icon={<AlertTriangle className="w-5 h-5 text-red-500" />} 
          label="Total Reports" 
          value={statistics?.total_reports || "0"}
          bg="bg-red-50"
        />
        <StatCard 
          icon={<Clock className="w-5 h-5 text-orange-500" />} 
          label="Pending" 
          value={statistics?.pending || "0"}
          bg="bg-orange-50"
        />
        <StatCard 
          icon={<CheckCircle className="w-5 h-5 text-green-500" />} 
          label="Resolved" 
          value={statistics?.resolved || "0"}
          bg="bg-green-50"
        />
        <StatCard 
          icon={<TrendingUp className="w-5 h-5 text-blue-500" />} 
          label="This Week" 
          value={statistics?.this_week || "0"}
          bg="bg-blue-50"
        />
      </div>

      {/* Reports Management Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-bold text-blue-900">Recent Reports</h3>
        <button onClick={fetchData} className="px-3 py-1 bg-green-100 text-green-800 rounded-lg text-sm font-semibold hover:bg-green-200 transition">
          Refresh
        </button>
      </div>

      {/* Reports List */}
      {reports.length > 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="divide-y divide-gray-100">
            {reports.map((report) => (
              <div key={report.id} className="p-4 hover:bg-gray-50 transition">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900 text-sm">
                      {report.is_compliant ? '✓ Compliant' : '⚠ Violation Found'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(report.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    report.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    report.status === 'resolved' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {report.status}
                  </span>
                </div>
                {report.violation_count > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-red-600 mb-1">
                      Violations: {report.violations_found.join(', ')}
                    </p>
                  </div>
                )}
                <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                  {report.extracted_text || 'No text extracted'}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-10 text-gray-400 bg-gray-50 rounded-xl border border-dashed border-gray-200">
          <p>No reports found. Start by uploading a billboard image.</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;