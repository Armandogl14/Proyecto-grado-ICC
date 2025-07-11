import {
  IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonList, IonItem,
  IonLabel, IonInput, IonTextarea, IonButton, IonSelect, IonSelectOption,
  IonSpinner, IonNote, IonGrid, IonRow, IonCol
} from '@ionic/react';
import { useForm, Controller } from 'react-hook-form';
import { useCreateContract, useContractTypes } from '../hooks/useContracts';
import { CreateContractData, ContractType } from '../types/contracts';
import { useHistory } from 'react-router-dom';

const NewAnalysisPage: React.FC = () => {
  const { control, handleSubmit, formState: { errors }, reset } = useForm<CreateContractData>({
    defaultValues: {
      title: '',
      contract_type: undefined,
      original_text: '',
    },
  });

  const history = useHistory();
  const createContractMutation = useCreateContract();
  const { data: contractTypesData, isLoading: isLoadingTypes } = useContractTypes();

  const onSubmit = (data: CreateContractData) => {
    const submissionData = {
      ...data,
      contract_type: Number(data.contract_type),
    };
    createContractMutation.mutate(submissionData, {
      onSuccess: (createdContract) => {
        reset();
        if (createdContract) {
          history.push(`/contracts/${createdContract.id}`);
        }
      },
    });
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Nuevo Análisis de Contrato</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen className="ion-padding">
        <form onSubmit={handleSubmit(onSubmit)}>
          <IonList>
            <IonItem>
              <IonLabel position="floating">Título del Contrato</IonLabel>
              <Controller
                name="title"
                control={control}
                rules={{ required: 'El título es requerido.' }}
                render={({ field }) => <IonInput {...field} />}
              />
            </IonItem>
            {errors.title && <IonNote color="danger" className="ion-padding-start">{errors.title.message}</IonNote>}

            <IonItem>
              <IonLabel position="floating">Tipo de Contrato</IonLabel>
              <Controller
                name="contract_type"
                control={control}
                rules={{ required: 'Debe seleccionar un tipo de contrato.' }}
                render={({ field }) => (
                  <IonSelect {...field} placeholder="Seleccione un tipo">
                    {isLoadingTypes ? <IonSpinner /> :
                      contractTypesData?.results?.map((type: ContractType) => (
                        <IonSelectOption key={type.id} value={type.id}>
                          {type.name}
                        </IonSelectOption>
                      ))
                    }
                  </IonSelect>
                )}
              />
            </IonItem>
            {errors.contract_type && <IonNote color="danger" className="ion-padding-start">{errors.contract_type.message}</IonNote>}

            <IonItem>
              <IonLabel position="floating">Pegue el texto del contrato aquí</IonLabel>
              <Controller
                name="original_text"
                control={control}
                rules={{ required: 'El texto del contrato no puede estar vacío.' }}
                render={({ field }) => <IonTextarea {...field} rows={20} />}
              />
            </IonItem>
            {errors.original_text && <IonNote color="danger" className="ion-padding-start">{errors.original_text.message}</IonNote>}
          </IonList>

          <IonGrid>
            <IonRow>
              <IonCol>
                <IonButton expand="full" type="submit" disabled={createContractMutation.isPending}>
                  {createContractMutation.isPending ? <IonSpinner name="dots" /> : 'Analizar Contrato'}
                </IonButton>
              </IonCol>
            </IonRow>
          </IonGrid>
        </form>
      </IonContent>
    </IonPage>
  );
};

export default NewAnalysisPage;
