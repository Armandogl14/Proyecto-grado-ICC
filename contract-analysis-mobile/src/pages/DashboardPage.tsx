import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonGrid, IonRow, IonCol, IonButton, IonIcon, IonSpinner, IonButtons, IonItem, IonLabel } from '@ionic/react';
import { useDashboardStats, useContracts } from '../hooks/useContracts';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { arrowForwardOutline, addOutline, fileTrayFullOutline, timeOutline, checkmarkCircleOutline, shieldOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import './DashboardPage.css';

const StatCard: React.FC<{title: string, value: number | string, icon: string, color: string}> = ({ title, value, icon, color }) => (
  <IonCol size="6" size-md="3">
    <IonCard className="ion-text-center">
      <IonCardContent>
        <IonIcon icon={icon} className={`text-4xl ${color}`} />
        <h2 className="text-2xl font-bold mt-2">{value}</h2>
        <p className="text-sm text-gray-400">{title}</p>
      </IonCardContent>
    </IonCard>
  </IonCol>
);

const DashboardPage: React.FC = () => {
  const { data: stats, isLoading: isLoadingStats } = useDashboardStats();
  const { data: contractsData, isLoading: isLoadingContracts } = useContracts({ page_size: 5 });
  const history = useHistory();

  if (isLoadingStats || isLoadingContracts) {
    return (
      <IonPage>
        <IonHeader>
          <IonToolbar>
            <IonTitle>Dashboard</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonContent className="ion-padding" fullscreen>
          <div className="ion-text-center">
            <IonSpinner name="crescent" />
            <p>Cargando dashboard...</p>
          </div>
        </IonContent>
      </IonPage>
    );
  }

  const riskData = [
    { name: 'Bajo', value: stats?.low_risk || 0, color: '#2dd36f' },
    { name: 'Medio', value: stats?.medium_risk || 0, color: '#ffc409' },
    { name: 'Alto', value: stats?.high_risk || 0, color: '#eb445a' },
  ];
  
  const totalRiskContracts = riskData.reduce((acc, item) => acc + item.value, 0);

  const statsCards = [
    { title: "Total", value: stats?.total_contracts || 0, icon: fileTrayFullOutline, color: "text-blue-400" },
    { title: "Pendientes", value: stats?.pending_analysis || 0, icon: timeOutline, color: "text-yellow-400" },
    { title: "Completados", value: stats?.completed || 0, icon: checkmarkCircleOutline, color: "text-green-400" },
    { title: "Alto Riesgo", value: stats?.high_risk || 0, icon: shieldOutline, color: "text-red-400" },
  ];

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Dashboard</IonTitle>
          <IonButtons slot="end">
            <IonButton routerLink="/new">
              <IonIcon slot="icon-only" icon={addOutline} />
            </IonButton>
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen className="ion-padding">
        <IonGrid>
          <IonRow>
            {statsCards.map(stat => <StatCard key={stat.title} {...stat} />)}
          </IonRow>

          <IonRow>
            <IonCol size="12" size-lg="6">
              <IonCard>
                <IonCardHeader><IonCardTitle>Distribución de Riesgo</IonCardTitle></IonCardHeader>
                <IonCardContent style={{ height: '250px' }}>
                  {totalRiskContracts > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} innerRadius={50}>
                          {riskData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : <p className="ion-text-center">No hay datos de riesgo.</p>}
                </IonCardContent>
              </IonCard>
            </IonCol>
            
            <IonCol size="12" size-lg="6">
              <IonCard>
                <IonCardHeader>
                  <IonCardTitle>Contratos Recientes</IonCardTitle>
                </IonCardHeader>
                <IonCardContent>
                  {contractsData?.results?.map(contract => (
                    <IonItem key={contract.id} button detail={true} onClick={() => history.push(`/contracts/${contract.id}`)}>
                      <IonLabel>
                        <h2>{contract.title}</h2>
                        <p>{contract.contract_type.name}</p>
                      </IonLabel>
                    </IonItem>
                  ))}
                  <IonButton expand="full" fill="clear" routerLink="/contracts">
                    Ver todos
                    <IonIcon icon={arrowForwardOutline} slot="end" />
                  </IonButton>
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
