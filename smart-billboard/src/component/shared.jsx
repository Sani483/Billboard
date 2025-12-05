import React from 'react';
import { AlertTriangle, CheckCircle } from 'lucide-react';

// Navigation Tab Button
export const TabButton = ({ active, onClick, icon, label }) => (
  <button
    onClick={onClick}
    className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
      active 
        ? 'bg-gray-100 text-gray-900 shadow-sm' 
        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
    }`}
  >
    {icon}
    {label}
  </button>
);

// Feature Info Card (Overview)
export const FeatureCard = ({ icon, title, desc }) => (
  <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center text-center hover:shadow-md transition-shadow">
    <div className="mb-3 p-3 bg-gray-50 rounded-full">{icon}</div>
    <h3 className="font-bold text-gray-800 mb-2">{title}</h3>
    <p className="text-gray-500 text-sm leading-relaxed">{desc}</p>
  </div>
);

// Dashboard Statistic Card
export const StatCard = ({ icon, label, value, bg }) => (
  <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col gap-3">
    <div className={`self-start p-2 rounded-lg ${bg}`}>{icon}</div>
    <div>
      <div className="text-gray-500 text-xs font-medium uppercase tracking-wide">{label}</div>
      <div className="text-2xl font-bold text-gray-800">{value}</div>
    </div>
  </div>
);

// List Items
export const ChallengeItem = ({ text }) => (
  <li className="flex items-start gap-3 text-sm text-gray-700">
    <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
    <span>{text}</span>
  </li>
);

export const BenefitItem = ({ text }) => (
  <li className="flex items-start gap-3 text-sm text-gray-700">
    <CheckCircle className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
    <span>{text}</span>
  </li>
);