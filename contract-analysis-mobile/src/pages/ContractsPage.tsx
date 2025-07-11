import {
  IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonList, IonItem, IonLabel,
  IonButton, IonIcon, IonButtons, IonInfiniteScroll, IonInfiniteScrollContent,
  IonSpinner, IonBadge, IonGrid, IonRow, IonCol, type InfiniteScrollCustomEvent
} from '@ionic/react';
import { useInfiniteContracts } from '../hooks/useContracts';
import { useHistory } from 'react-router-dom';
import { addOutline } from 'ionicons/icons';
import { Contract, PaginatedResponse } from '../types/contracts';
import RiskIndicator from '../components/RiskIndicator';
import React from 'react';

export const ContractStatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const statusMap: { [key: string]: { label: string; color: string } } = {
    pending: { label: 'Pendiente', color: 'medium' },
    analyzing: { label: 'Analizando', color: 'warning' },
    completed: { label: 'Completado', color: 'success' },
    error: { label: 'Error', color: 'danger' },
  };
  const { label, color } = statusMap[status] || { label: 'Desconocido', color: 'dark' };
  return <IonBadge color={color}>{label}</IonBadge>;
};


const ContractsPage: React.FC = () => {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isLoading,
    isFetchingNextPage,
  } = useInfiniteContracts();
  
  const history = useHistory();

  const loadMore = (event: InfiniteScrollCustomEvent) => {
    if (hasNextPage) {
      fetchNextPage().then(() => event.target.complete());
    } else {
      event.target.disabled = true;
    }
  };

  const navigateToDetail = (id: string) => {
    history.push(`/contracts/${id}`);
  };
  
  if (isLoading && !data) {
    return (
      <IonPage>
        <IonHeader>
          <IonToolbar><IonTitle>Mis Contratos</IonTitle></IonToolbar>
        </IonHeader>
        <IonContent className="ion-text-center ion-padding">
          <IonSpinner name="crescent" />
          <p>Cargando contratos...</p>
        </IonContent>
      </IonPage>
    );
  }

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Mis Contratos</IonTitle>
          <IonButtons slot="end">
            <IonButton routerLink="/new">
              <IonIcon slot="icon-only" icon={addOutline} />
            </IonButton>
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonList>
          {data?.pages.map((page: PaginatedResponse<Contract>, i: number) => (
            <React.Fragment key={i}>
              {page.results.map((contract: Contract) => (
                <IonItem key={contract.id} button onClick={() => navigateToDetail(contract.id)} detail={false}>
                   <IonGrid>
                    <IonRow className="ion-align-items-center">
                      <IonCol size="auto">
                        <RiskIndicator score={contract.risk_score} />
                      </IonCol>
                      <IonCol>
                        <IonLabel>
                          <h2 style={{ fontWeight: 'bold' }}>{contract.title}</h2>
                          <p>{contract.contract_type.name}</p>
                        </IonLabel>
                      </IonCol>
                      <IonCol size="auto">
                        <ContractStatusBadge status={contract.status} />
                      </IonCol>
                    </IonRow>
                  </IonGrid>
                </IonItem>
              ))}
            </React.Fragment>
          ))}
        </IonList>

        <IonInfiniteScroll
          onIonInfinite={loadMore}
          disabled={!hasNextPage || isFetchingNextPage}
        >
          <IonInfiniteScrollContent
            loadingSpinner="bubbles"
            loadingText="Cargando más contratos..."
          />
        </IonInfiniteScroll>
      </IonContent>
    </IonPage>
  );
};

export default ContractsPage;
