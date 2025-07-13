import React from 'react';
import './RiskIndicator.css';

interface RiskIndicatorProps {
  score: number;
}

const RiskIndicator: React.FC<RiskIndicatorProps> = ({ score }) => {
  const getRiskColor = () => {
    if (score < 40) return 'risk-low';
    if (score < 70) return 'risk-medium';
    return 'risk-high';
  };

  const riskLevelText = () => {
    if (score < 40) return 'Bajo';
    if (score < 70) return 'Medio';
    return 'Alto';
  }

  return (
    <div className={`risk-indicator ${getRiskColor()}`}>
      <span className="risk-score">{score.toFixed(0)}</span>
      <span className="risk-label">{riskLevelText()}</span>
    </div>
  );
};

export default RiskIndicator; 