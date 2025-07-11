import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonGrid, IonRow, IonCol, IonButton, IonIcon } from '@ionic/react';
import { useDashboardStats, useContracts } from '../hooks/useContracts';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { arrowForwardOutline, addOutline } from 'ionicons/icons';
import './DashboardPage.css';

const DashboardPage: React.FC = () => {
  const { data: stats, isLoading: isLoadingStats } = useDashboardStats();
  const { data: contractsData, isLoading: isLoadingContracts } = useContracts({ page_size: 5 });

  if (isLoadingStats || isLoadingContracts) {
    return (
      <IonPage>
        <IonHeader>
          <IonToolbar>
            <IonTitle>Dashboard</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonContent fullscreen>
          {/* Add Skeleton/Loading UI */}
          <p>Cargando...</p>
        </IonContent>
      </IonPage>
    );
  }

  const riskData = [
    { name: 'Bajo', value: stats?.low_risk || 0, color: '#34d399' },
    { name: 'Medio', value: stats?.medium_risk || 0, color: '#f59e0b' },
    { name: 'Alto', value: stats?.high_risk || 0, color: '#f87171' },
  ];

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Dashboard</IonTitle>
          <IonButton routerLink="/tab3" slot="end" fill="clear">
            <IonIcon icon={addOutline} />
          </IonButton>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <IonHeader collapse="condense">
          <IonToolbar>
            <IonTitle size="large">Dashboard</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonGrid>
          {/* Stats Cards */}
          <IonRow>
            <IonCol size="6" size-md="3">
              <IonCard>
                <IonCardHeader>
                  <IonCardTitle>{stats?.total_contracts || 0}</IonCardTitle>
                </IonCardHeader>
                <IonCardContent>Total Contratos</IonCardContent>
              </IonCard>
            </IonCol>
            {/* ... other stat cards ... */}
          </IonRow>

          {/* Chart and Recent Contracts */}
          <IonRow>
            <IonCol size="12" size-md="6">
              <IonCard>
                <IonCardHeader><IonCardTitle>Distribución de Riesgo</IonCardTitle></IonCardHeader>
                <IonCardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                        {riskData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </IonCardContent>
              </IonCard>
            </IonCol>
            <IonCol size="12" size-md="6">
              <IonCard>
                <IonCardHeader><IonCardTitle>Contratos Recientes</IonCardTitle></IonCardHeader>
                <IonCardContent>
                  {contractsData?.results?.map(contract => (
                    <IonButton key={contract.id} expand="block" fill="clear" routerLink={`/contracts/${contract.id}`}>
                      {contract.title}
                      <IonIcon icon={arrowForwardOutline} slot="end" />
                    </IonButton>
                  ))}
                </IonCardContent>
              </IonCard>
            </IonCol>
          </IonRow>
        </IonGrid>
      </IonContent>
    </IonPage>
  );
};

export default DashboardPage;
