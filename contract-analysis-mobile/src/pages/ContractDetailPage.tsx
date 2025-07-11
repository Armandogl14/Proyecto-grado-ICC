import {
  IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonButtons, IonBackButton,
  IonCard, IonCardContent, IonCardHeader, IonCardTitle, IonButton, IonIcon,
  IonSpinner, IonAlert, IonGrid, IonRow, IonCol, IonChip, IonLabel, IonText
} from '@ionic/react';
import { useParams, useHistory } from 'react-router-dom';
import { useRealTimeAnalysis, useAnalyzeContract, useDeleteContract, useClausesByContract } from '../hooks/useContracts';
import { refreshOutline, trashOutline, playOutline, documentTextOutline, shieldCheckmarkOutline, informationCircleOutline } from 'ionicons/icons';
import RiskIndicator from '../components/RiskIndicator';
import ClauseCard from '../components/ClauseCard';
import { ContractStatusBadge } from './ContractsPage';
import { useState } from 'react';

const ContractDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const history = useHistory();
  
  const { data: contract, isLoading: isLoadingContract, error } = useRealTimeAnalysis(id);
  const { data: clausesData, isLoading: isLoadingClauses } = useClausesByContract(id);
  const analyzeContractMutation = useAnalyzeContract();
  const deleteContractMutation = useDeleteContract();

  const [showAlert, setShowAlert] = useState(false);

  const handleAnalyze = () => analyzeContractMutation.mutate({ id });
  const handleReanalyze = () => analyzeContractMutation.mutate({ id, forceReanalysis: true });
  const handleDelete = () => {
    deleteContractMutation.mutate(id, {
      onSuccess: () => history.push('/contracts'),
    });
  };

  if (isLoadingContract) {
    return (
      <IonPage>
        <IonHeader><IonToolbar><IonTitle>Cargando...</IonTitle></IonToolbar></IonHeader>
        <IonContent className="ion-text-center ion-padding"><IonSpinner /></IonContent>
      </IonPage>
    );
  }

  if (error || !contract) {
     return (
      <IonPage>
        <IonHeader><IonToolbar><IonTitle>Error</IonTitle></IonToolbar></IonHeader>
        <IonContent className="ion-text-center ion-padding">
          <p>Error al cargar el contrato o no se encontró.</p>
          <IonButton routerLink="/contracts">Volver a la lista</IonButton>
        </IonContent>
      </IonPage>
    );
  }

  const isAnalyzed = contract.status === 'completed' || contract.status === 'error';

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/contracts" />
          </IonButtons>
          <IonTitle>{contract.title}</IonTitle>
          <IonButtons slot="end">
            <IonButton onClick={() => setShowAlert(true)} color="danger" disabled={deleteContractMutation.isPending}>
              <IonIcon icon={trashOutline} />
            </IonButton>
            <IonButton onClick={handleReanalyze} disabled={analyzeContractMutation.isPending}>
              <IonIcon icon={refreshOutline} />
            </IonButton>
            {contract.status === 'pending' && (
              <IonButton onClick={handleAnalyze} disabled={analyzeContractMutation.isPending}>
                <IonIcon icon={playOutline} />
              </IonButton>
            )}
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen className="ion-padding">
        <IonAlert
          isOpen={showAlert}
          onDidDismiss={() => setShowAlert(false)}
          header={'Confirmar Eliminación'}
          message={'¿Estás seguro de que quieres eliminar este contrato? Esta acción no se puede deshacer.'}
          buttons={[
            { text: 'Cancelar', role: 'cancel' },
            { text: 'Eliminar', handler: handleDelete, cssClass: 'danger' }
          ]}
        />

        <IonGrid>
          <IonRow>
            <IonCol size="12" size-md="4">
                <RiskIndicator score={contract.risk_score} />
            </IonCol>
            <IonCol size="12" size-md="8">
              <IonCard>
                <IonCardHeader>
                  <IonCardTitle>Información General</IonCardTitle>
                </IonCardHeader>
                <IonCardContent>
                  <p><strong>Tipo:</strong> {contract.contract_type.name}</p>
                  <p><strong>Estado:</strong> <ContractStatusBadge status={contract.status} /></p>
                  <p><strong>Cláusulas Totales:</strong> {contract.total_clauses}</p>
                   {isAnalyzed && <p><strong>Cláusulas Abusivas:</strong> {contract.abusive_clauses_count}</p>}
                </IonCardContent>
              </IonCard>
            </IonCol>
          </IonRow>
        </IonGrid>
        
        {isAnalyzed && contract.executive_summary && (
          <IonCard>
            <IonCardHeader><IonCardTitle><IonIcon icon={informationCircleOutline} /> Resumen Ejecutivo</IonCardTitle></IonCardHeader>
            <IonCardContent>{contract.executive_summary}</IonCardContent>
          </IonCard>
        )}
        
        {isAnalyzed && contract.recommendations && (
          <IonCard>
            <IonCardHeader><IonCardTitle><IonIcon icon={shieldCheckmarkOutline} /> Recomendaciones</IonCardTitle></IonCardHeader>
            <IonCardContent>{contract.recommendations}</IonCardContent>
          </IonCard>
        )}

        <IonCard>
          <IonCardHeader>
            <IonCardTitle><IonIcon icon={documentTextOutline} /> Cláusulas Analizadas</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            {isLoadingClauses ? <IonSpinner /> : 
              clausesData && clausesData.results.length > 0 ? (
                clausesData.results.map((clause) => (
                  <ClauseCard key={clause.id} clause={clause} />
                ))
              ) : (
                <p>No se encontraron cláusulas o el contrato aún no ha sido analizado.</p>
              )
            }
          </IonCardContent>
        </IonCard>
      </IonContent>
    </IonPage>
  );
};

export default ContractDetailPage;
