import React from 'react';
import { IonCard, IonCardContent, IonCardHeader, IonCardTitle, IonGrid, IonRow, IonCol, IonIcon, IonChip, IonLabel } from '@ionic/react';
import { checkmarkCircleOutline, closeCircleOutline, warningOutline } from 'ionicons/icons';
import { Clause } from '../types/contracts';
import './ClauseCard.css';

interface ClauseCardProps {
  clause: Clause;
}

const ClauseCard: React.FC<ClauseCardProps> = ({ clause }) => {

  const isGptAbusive = clause.gpt_analysis?.is_abusive;
  const gptExplanation = clause.gpt_analysis?.explanation;

  const getRiskColor = (score: number) => {
    if (score < 0.4) return 'success';
    if (score < 0.7) return 'warning';
    return 'danger';
  };

  return (
    <IonCard className="clause-card" color={isGptAbusive ? 'danger' : 'light'}>
      <IonCardHeader>
        <IonGrid>
          <IonRow className="ion-align-items-center">
            <IonCol>
              <IonCardTitle className="clause-title">Cláusula #{clause.clause_number}</IonCardTitle>
            </IonCol>
            <IonCol size="auto">
              <IonChip color={getRiskColor(clause.risk_score)}>
                <IonLabel>Riesgo: {(clause.risk_score * 100).toFixed(0)}%</IonLabel>
              </IonChip>
            </IonCol>
          </IonRow>
        </IonGrid>
      </IonCardHeader>

      <IonCardContent>
        <p className="clause-text">{clause.text}</p>
        
        {isGptAbusive && gptExplanation && (
          <div className="gpt-explanation">
            <IonIcon icon={warningOutline} color="danger" slot="start" />
            <p><strong>Explicación de Abusividad:</strong> {gptExplanation}</p>
          </div>
        )}

        <IonGrid className="analysis-grid">
          <IonRow>
            <IonCol>
              <strong>Análisis ML</strong>
              <p>
                <IonIcon icon={clause.ml_analysis.is_abusive ? closeCircleOutline : checkmarkCircleOutline} color={clause.ml_analysis.is_abusive ? 'danger' : 'success'} />
                {clause.ml_analysis.is_abusive ? ' Abusiva' : ' No Abusiva'} ({(clause.ml_analysis.abuse_probability * 100).toFixed(0)}%)
              </p>
            </IonCol>
            <IonCol>
              <strong>Análisis GPT</strong>
              <p>
                <IonIcon icon={isGptAbusive ? closeCircleOutline : checkmarkCircleOutline} color={isGptAbusive ? 'danger' : 'success'} />
                {isGptAbusive ? ' Abusiva' : ' No Abusiva'}
              </p>
            </IonCol>
          </IonRow>
        </IonGrid>
      </IonCardContent>
    </IonCard>
  );
};

export default ClauseCard; 