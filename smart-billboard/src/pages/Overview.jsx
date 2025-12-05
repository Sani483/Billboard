import React from 'react';
import { Camera, Shield, MapPin, Users } from 'lucide-react';
import { FeatureCard, ChallengeItem, BenefitItem } from '../component/shared';

const Overview = () => {
  return (
    <div className="space-y-6 pb-20">
      {/* Features Grid */}
      <div className="grid grid-cols-1 gap-4">
        <FeatureCard 
          icon={<Camera className="w-8 h-8 text-blue-600" />}
          title="AI-Powered Detection"
          desc="Advanced computer vision to detect billboard violations in real-time"
        />
        <FeatureCard 
          icon={<Shield className="w-8 h-8 text-green-600" />}
          title="Compliance Monitoring"
          desc="Automated checks against city zoning laws and permitted billboard database"
        />
        <FeatureCard 
          icon={<MapPin className="w-8 h-8 text-orange-500" />}
          title="Geolocation Tracking"
          desc="Precise location data with timestamp for accurate violation reporting"
        />
        <FeatureCard 
          icon={<Users className="w-8 h-8 text-indigo-500" />}
          title="Citizen Engagement"
          desc="Empowers citizens to report violations and participate in city governance"
        />
      </div>

      {/* The Challenge Section */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-lg font-bold text-blue-900 mb-3">The Challenge</h3>
        <p className="text-gray-600 text-sm mb-4">
          Cities struggle with unauthorized billboards and compliance violations that impact:
        </p>
        <ul className="space-y-3">
          <ChallengeItem text="Public safety through structural hazards" />
          <ChallengeItem text="Urban aesthetics and city planning" />
          <ChallengeItem text="Revenue loss from unpermitted advertising" />
          <ChallengeItem text="Manual inspection inefficiencies" />
        </ul>
      </div>

      {/* Solution Benefits Section */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-lg font-bold text-green-700 mb-3">Our Solution Benefits</h3>
        <ul className="space-y-3">
          <BenefitItem text="Reduce manual inspection efforts by 80%" />
          <BenefitItem text="Real-time violation detection and alerts" />
          <BenefitItem text="Improved regulatory compliance rates" />
        </ul>
      </div>
    </div>
  );
};

export default Overview;