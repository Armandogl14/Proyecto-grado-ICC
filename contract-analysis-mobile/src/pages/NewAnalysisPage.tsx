import {
  IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonItem,
  IonLabel, IonInput, IonTextarea, IonButton, IonSelect, IonSelectOption,
  IonSpinner, IonNote, IonGrid, IonRow, IonCol, IonButtons, IonBackButton,
  IonIcon, useIonToast
} from '@ionic/react';
import { useForm, Controller } from 'react-hook-form';
import { useCreateContract, useContractTypes } from '../hooks/useContracts';
import { CreateContractData, ContractType } from '../types/contracts';
import { useHistory } from 'react-router-dom';
import { attachOutline } from 'ionicons/icons';
import { useRef } from 'react';

const NewAnalysisPage: React.FC = () => {
  const { control, handleSubmit, formState: { errors }, reset, setValue } = useForm<CreateContractData>({
    defaultValues: {
      title: '',
      contract_type: undefined,
      original_text: '',
      file: undefined,
    },
  });

  const history = useHistory();
  const createContractMutation = useCreateContract();
  const { data: contractTypesData, isLoading: isLoadingTypes } = useContractTypes();
  const [presentToast] = useIonToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const onSubmit = (data: CreateContractData) => {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('contract_type', String(data.contract_type));

    if (data.original_text) {
      formData.append('original_text', data.original_text);
    } else if (data.file) {
      formData.append('file', data.file);
    }

    createContractMutation.mutate(formData, {
      onSuccess: (createdContract) => {
        presentToast({
          message: 'Contrato creado y análisis en proceso.',
          duration: 3000,
          color: 'success',
          position: 'top',
        });
        reset();
        if (createdContract) {
          history.push(`/contracts/${createdContract.id}`);
        } else {
          history.push('/contracts');
        }
      },
      onError: () => {
        presentToast({
          message: 'Error al crear el contrato. Inténtelo de nuevo.',
          duration: 3000,
          color: 'danger',
          position: 'top',
        });
      },
    });
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      setValue('file', file);
      setValue('original_text', '');
      presentToast({
        message: `Archivo seleccionado: ${file.name}`,
        duration: 2000,
        color: 'primary',
        position: 'top',
      });
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start">
            <IonBackButton defaultHref="/contracts" />
          </IonButtons>
          <IonTitle>Nuevo Análisis</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen className="ion-padding">
        <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <div style={{ flexGrow: 1, overflowY: 'auto' }}>
            <IonItem lines="none" style={{ marginBottom: '2rem', '--inner-padding-top': '2rem', '--inner-padding-bottom': '2rem', '--background': 'transparent' }}>
              <Controller
                name="title"
                control={control}
                rules={{ required: 'El título es requerido.' }}
                render={({ field }) => (
                  <IonInput
                    {...field}
                    label="Título del Contrato"
                    labelPlacement="floating"
                    fill="outline"
                    shape="round"
                    placeholder="Ej: Contrato de Alquiler"
                  />
                )}
              />
            </IonItem>
            {errors.title && <IonNote color="danger" className="ion-padding-start" style={{ marginTop: '1rem', display: 'block', color: '#ff5252' }}>{errors.title.message}</IonNote>}

            <IonItem lines="none" style={{ marginBottom: '2rem', '--inner-padding-top': '2rem', '--inner-padding-bottom': '2rem', '--background': 'transparent' }}>
              <Controller
                name="contract_type"
                control={control}
                rules={{ required: 'Debe seleccionar un tipo de contrato.' }}
                render={({ field: { onChange, value } }) => (
                  <IonSelect
                    value={value}
                    onIonChange={e => onChange(e.detail.value)}
                    placeholder="Seleccione un tipo"
                    label="Tipo de Contrato"
                    labelPlacement="floating"
                    fill="outline"
                    shape="round"
                  >
                    {isLoadingTypes ? (
                      <IonSelectOption disabled>
                        <IonSpinner name="dots" />
                      </IonSelectOption>
                    ) : (
                      contractTypesData?.results?.map((type: ContractType) => (
                        <IonSelectOption key={type.id} value={type.id}>
                          {type.name}
                        </IonSelectOption>
                      ))
                    )}
                  </IonSelect>
                )}
              />
            </IonItem>
            {errors.contract_type && <IonNote color="danger" className="ion-padding-start" style={{ marginTop: '1rem', display: 'block', color: '#ff5252' }}>{errors.contract_type.message}</IonNote>}

            <IonItem lines="none" style={{ textAlign: 'center', marginBottom: '1rem' }}>
              <IonLabel color="medium">Pegue el texto o suba un archivo</IonLabel>
            </IonItem>

            <IonItem lines="none" style={{ marginBottom: '2rem', '--inner-padding-top': '2rem', '--inner-padding-bottom': '2rem', '--background': 'transparent' }}>
              <Controller
                name="original_text"
                control={control}
                rules={{
                  validate: (value, formValues) =>
                    !!value || !!formValues.file || 'Debe pegar el texto o subir un archivo.',
                }}
                render={({ field }) => (
                  <IonTextarea
                    {...field}
                    label="Texto del Contrato"
                    labelPlacement="floating"
                    fill="outline"
                    shape="round"
                    placeholder="Pegue el texto del contrato aquí..."
                    rows={12}
                    onIonChange={(e) => {
                      field.onChange(e);
                      if (e.detail.value) setValue('file', undefined);
                    }}
                  />
                )}
              />
            </IonItem>
            {errors.original_text && <IonNote color="danger" className="ion-padding-start" style={{ marginTop: '1rem', display: 'block', color: '#ff5252' }}>{errors.original_text.message}</IonNote>}
          </div>

          <input
            type="file"
            hidden
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.doc,.docx,.txt"
          />

          <IonGrid className="ion-padding-top">
            <IonRow>
              <IonCol>
                <IonButton expand="full" fill="outline" onClick={triggerFileSelect} shape="round">
                  <IonIcon slot="start" icon={attachOutline} />
                  Subir Archivo
                </IonButton>
              </IonCol>
            </IonRow>
            <IonRow>
              <IonCol>
                <IonButton expand="full" type="submit" disabled={createContractMutation.isPending} shape="round">
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
