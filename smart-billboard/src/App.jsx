import React, { useState } from 'react';
import { 
  Home, 
  Smartphone, 
  LayoutDashboard, 
  Camera, 
  Shield, 
  MapPin, 
  Users, 
  AlertTriangle, 
  CheckCircle,
  ChevronRight 
} from 'lucide-react';
import { TabButton } from './component/shared';
import DashboardPage from './pages/Dashboard';
import DetectPage from './pages/Detect';
import OverviewPage from './pages/Overview';

// --- Internal Components for Content ---

const Overview = () => {
  return (
    <div className="space-y-16 py-8 animate-in fade-in duration-500">
      {/* Features Grid (4 Columns) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            icon: <Camera className="w-8 h-8 text-green-600" />,
            title: "AI-Powered Detection",
            desc: "Advanced computer vision to detect billboard violations in real-time"
          },
          {
            icon: <Shield className="w-8 h-8 text-green-600" />,
            title: "Compliance Monitoring",
            desc: "Automated checks against city zoning laws and permitted billboard database"
          },
          {
            icon: <MapPin className="w-8 h-8 text-green-600" />,
            title: "Geolocation Tracking",
            desc: "Precise location data with timestamp for accurate violation reporting"
          },
          {
            icon: <Users className="w-8 h-8 text-green-600" />,
            title: "Citizen Engagement",
            desc: "Empower citizens to report violations and participate in city governance"
          }
        ].map((feature, idx) => (
          <div key={idx} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
            <div className="mb-4 p-3 bg-green-50 w-fit rounded-lg">
              {feature.icon}
            </div>
            <h3 className="font-bold text-gray-900 mb-2">{feature.title}</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              {feature.desc}
            </p>
          </div>
        ))}
      </div>

      {/* The Challenge Section */}
      <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">The Challenge</h3>
        <p className="text-gray-500 mb-8">Cities struggle with unauthorized billboards and compliance violations that impact:</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-12">
          {[
            "Public safety through structural hazards",
            "Revenue loss from unpermitted advertising",
            "Urban aesthetics and city planning",
            "Manual inspection inefficiencies"
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" />
              <span className="text-gray-700 font-medium">{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Our Solution Benefits Section */}
      <div className="bg-green-50 rounded-2xl p-8 border border-green-100">
        <h3 className="text-2xl font-bold text-gray-900 mb-8">Our Solution Benefits</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-12">
          {[
            "Reduce manual inspection efforts by 80%",
            "Real-time violation detection and alerts",
            "Improved regulatory compliance rates",
            "Enhanced citizen participation in governance"
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 shrink-0" />
              <span className="text-gray-800 font-medium">{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Placeholder components for other tabs
const Detect = () => (
  <div className="text-center py-20 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
    <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
    <h3 className="text-xl font-medium text-gray-600">Detection Camera Interface</h3>
    <p className="text-gray-400">Camera feed and analysis tools would appear here.</p>
  </div>
);

const Dashboard = () => (
  <div className="text-center py-20 bg-gray-50 rounded-xl border-2 border-dashed border-gray-300">
    <LayoutDashboard className="w-12 h-12 text-gray-400 mx-auto mb-4" />
    <h3 className="text-xl font-medium text-gray-600">Analytics Dashboard</h3>
    <p className="text-gray-400">Charts and violation reports would appear here.</p>
  </div>
);

// --- Main App Component ---

const App = () => {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-white font-sans text-gray-900">
      
      {/* 1. HERO SECTION */}
      <div className="relative h-[500px] w-full bg-gray-900 flex flex-col items-center justify-center text-center px-4 overflow-hidden">
        {/* Background Image with Overlay */}
        <div 
          className="absolute inset-0 z-0 opacity-40 bg-cover bg-center"
          style={{ 
            backgroundImage: "url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=2070&auto=format&fit=crop')" 
          }}
        />
        <div className="absolute inset-0 bg-linear-to-b from-gray-900/50 to-gray-900/90 z-0" />

        {/* Hero Content */}
        <div className="relative z-10 max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-white leading-tight">
            Smart Billboard <br />
            <span className="text-green-400">Compliance Detection</span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-200 max-w-2xl mx-auto leading-relaxed">
            AI-powered solution for detecting unauthorized billboards and ensuring 
            regulatory compliance through smart detection and citizen engagement.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <button 
              onClick={() => setActiveTab('detect')}
              className="px-8 py-3 bg-white text-green-900 font-bold rounded-lg shadow-lg hover:bg-gray-100 transform hover:-translate-y-1 transition-all flex items-center justify-center gap-2"
            >
              <Camera className="w-5 h-5" />
              Start Detection
            </button>
            <button 
              onClick={() => setActiveTab('dashboard')}
              className="px-8 py-3 bg-transparent border-2 border-white text-white font-bold rounded-lg hover:bg-white/10 transform hover:-translate-y-1 transition-all flex items-center justify-center gap-2"
            >
              <LayoutDashboard className="w-5 h-5" />
              View Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* 2. NAVIGATION TABS */}
      <div className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-center md:justify-start gap-8">
            {[
              { id: 'overview', label: 'Overview', icon: <Home className="w-4 h-4" /> },
              { id: 'detect', label: 'Detect', icon: <Smartphone className="w-4 h-4" /> },
              { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 py-4 px-2 text-sm font-semibold border-b-2 transition-colors
                  ${activeTab === tab.id 
                    ? 'border-green-600 text-green-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                `}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 3. MAIN CONTENT AREA */}
      <main className="max-w-6xl mx-auto px-4 py-8 min-h-[60vh]">
        {activeTab === 'overview' && <OverviewPage />}
        {activeTab === 'detect' && <DetectPage />}
        {activeTab === 'dashboard' && <DashboardPage />}
      </main>

      {/* Footer (Optional addition for completeness) */}
      <footer className="bg-gray-50 border-t border-gray-200 py-8 text-center text-gray-400 text-sm">
        © 2025 Smart Billboard Compliance System
      </footer>

    </div>
  );
};

export default App;