import React from 'react';

export const DisclaimerBanner: React.FC = () => {
  return (
    <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2.5 text-center text-xs font-medium text-amber-200 flex items-center justify-center space-x-2">
      <span className="text-sm">⚠️</span>
      <span>
        <strong>Safety Disclaimer:</strong> AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only.
      </span>
    </div>
  );
};
