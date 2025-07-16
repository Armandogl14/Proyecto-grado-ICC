from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
# from celery import shared_task  # Commented out to avoid Redis dependency

from .models import Contract, ContractType, Clause, AnalysisResult
from .serializers import (
    ContractListSerializer, ContractDetailSerializer, ContractCreateSerializer,
    ContractTypeSerializer, ClauseSerializer, ContractAnalysisSerializer,
    BulkAnalysisSerializer
)
from ml_analysis.ml_service import ml_service
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class ContractTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de contratos (solo lectura)"""
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer
    permission_classes = [AllowAny]  # Permitir acceso sin autenticación


class ContractViewSet(viewsets.ModelViewSet):
    """ViewSet principal para contratos con funcionalidades completas"""
    
    # La autenticación y los permisos ahora se controlan globalmente en settings.py
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'contract_type', 'risk_score']
    
    def get_queryset(self):
        """Devuelve todos los contratos al no haber autenticación."""
        return Contract.objects.all()
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'list':
            return ContractListSerializer
        elif self.action == 'create':
            return ContractCreateSerializer
        else:
            return ContractDetailSerializer
    
    def perform_create(self, serializer):
        """Asigna un usuario por defecto al crear el contrato."""
        # Se asigna el primer superusuario que exista como autor por defecto.
        # Esto es necesario porque la creación de contratos requiere un autor.
        default_user = get_user_model().objects.filter(is_superuser=True).order_by('pk').first()
        if not default_user:
            raise Exception("No hay un superusuario en el sistema para asignar el contrato. Por favor, cree uno con 'python manage.py createsuperuser'.")
        
        contract = serializer.save(uploaded_by=default_user)
        
        # Iniciar análisis automáticamente si es texto (modo síncrono para desarrollo)
        if contract.original_text:
            self.trigger_analysis_sync(contract.id)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Endpoint para analizar un contrato específico"""
        contract = self.get_object()
        
        # Combinar datos del request con el contract_id
        request_data = request.data.copy()
        request_data['contract_id'] = contract.id
        
        serializer = ContractAnalysisSerializer(data=request_data)
        
        if serializer.is_valid():
            force_reanalysis = serializer.validated_data.get('force_reanalysis', False)
            
            # Verificar si ya fue analizado
            if contract.status == 'completed' and not force_reanalysis:
                return Response({
                    'message': 'El contrato ya fue analizado',
                    'contract_id': contract.id,
                    'status': contract.status
                }, status=status.HTTP_200_OK)
            
            # Iniciar análisis (modo síncrono para desarrollo)
            self.trigger_analysis_sync(contract.id)
            
            # Refrescar el contrato para obtener el estado actualizado
            contract.refresh_from_db()
            
            return Response({
                'message': 'Análisis completado',
                'contract_id': contract.id,
                'status': contract.status,
                'risk_score': contract.risk_score
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_analyze(self, request):
        """Endpoint para análisis masivo de contratos"""
        serializer = BulkAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            contract_ids = serializer.validated_data['contract_ids']
            force_reanalysis = serializer.validated_data.get('force_reanalysis', False)
            
            # Verificar que todos los contratos pertenezcan al usuario
            contracts = Contract.objects.filter(
                id__in=contract_ids,
                uploaded_by=request.user
            )
            
            if contracts.count() != len(contract_ids):
                return Response({
                    'error': 'Algunos contratos no fueron encontrados o no tienes permisos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Iniciar análisis para cada contrato (modo síncrono)
            task_results = []
            for contract in contracts:
                if contract.status != 'completed' or force_reanalysis:
                    # Usar análisis síncrono en lugar de Celery
                    self.trigger_analysis_sync(contract.id)
                    task_results.append({
                        'contract_id': contract.id,
                        'task_id': 'sync_analysis'
                    })
            
            return Response({
                'message': f'Análisis iniciado para {len(task_results)} contratos',
                'tasks': task_results
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Endpoint para estadísticas del dashboard"""
        user_contracts = self.get_queryset()
        
        stats = {
            'total_contracts': user_contracts.count(),
            'pending_analysis': user_contracts.filter(status='pending').count(),
            'analyzing': user_contracts.filter(status='analyzing').count(),
            'completed': user_contracts.filter(status='completed').count(),
            'high_risk': user_contracts.filter(risk_score__gte=0.7).count(),
            'medium_risk': user_contracts.filter(
                risk_score__gte=0.3, 
                risk_score__lt=0.7
            ).count(),
            'low_risk': user_contracts.filter(risk_score__lt=0.3).count(),
        }
        
        # Contratos recientes
        recent_contracts = user_contracts.order_by('-created_at')[:5]
        stats['recent_contracts'] = ContractListSerializer(
            recent_contracts, many=True
        ).data
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def export_report(self, request, pk=None):
        """Endpoint para exportar reporte del análisis"""
        contract = self.get_object()
        
        if contract.status != 'completed':
            return Response({
                'error': 'El contrato no ha sido analizado completamente'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar reporte detallado
        report_data = {
            'contract': ContractDetailSerializer(contract).data,
            'generated_at': timezone.now().isoformat(),
            'summary': contract.analysis_result.executive_summary if hasattr(contract, 'analysis_result') else None,
            'recommendations': contract.analysis_result.recommendations if hasattr(contract, 'analysis_result') else None,
        }
        
        return Response(report_data)
    
    def trigger_analysis(self, contract_id):
        """Método auxiliar para iniciar análisis (modo síncrono por ahora)"""
        # analyze_contract_task.delay(str(contract_id))  # Commented out due to Redis dependency
        self.trigger_analysis_sync(contract_id)
    
    def trigger_analysis_sync(self, contract_id):
        """Método auxiliar para iniciar análisis (síncrono)"""
        # Importar aquí para evitar dependencias circulares
        from ml_analysis.ml_service import ml_service
        from django.utils import timezone
        
        try:
            contract = Contract.objects.get(id=contract_id)
            
            # --- INICIO: Limpiar resultados de análisis anteriores ---
            contract.clauses.all().delete()  # Borra cláusulas y entidades en cascada
            if hasattr(contract, 'analysis_result'):
                contract.analysis_result.delete()

            # Reiniciar campos del contrato y marcar como 'analizando'
            contract.status = 'analyzing'
            contract.analyzed_at = None
            contract.total_clauses = 0
            contract.abusive_clauses_count = 0
            contract.risk_score = None
            contract.save()
            # --- FIN: Limpieza ---
            
            # Realizar análisis usando el servicio ML
            analysis_result = ml_service.analyze_contract(contract.original_text)
            
            # Contar cláusulas abusivas considerando ambos análisis
            abusive_count = 0
            total_risk_score = 0
            
            # Guardar cláusulas y entidades
            for clause_result in analysis_result['clause_results']:
                # Determinar si es abusiva basado en ML Y GPT
                ml_is_abusive = clause_result['ml_analysis']['is_abusive']
                gpt_is_abusive = clause_result['gpt_analysis'].get('is_abusive', False)
                is_abusive = ml_is_abusive or gpt_is_abusive  # Abusiva si cualquiera la detecta
                
                if is_abusive:
                    abusive_count += 1
                
                # Usar la probabilidad de ML como confidence_score
                confidence_score = clause_result['ml_analysis']['abuse_probability']
                
                # Calcular risk_score considerando ambos análisis
                risk_score = confidence_score
                if gpt_is_abusive:
                    risk_score = max(risk_score, 0.8)  # Si GPT dice que es abusiva, mínimo 80%
                
                total_risk_score += risk_score
                
                # Extraer datos del análisis GPT
                gpt_analysis = clause_result['gpt_analysis']
                
                Clause.objects.create(
                    contract=contract,
                    text=clause_result['text'],
                    clause_number=str(clause_result.get('clause_number', '')),
                    is_abusive=is_abusive,
                    confidence_score=confidence_score,
                    clause_type=gpt_analysis.get('clause_type', 'general'),
                    # --- INICIO: Limpieza de datos GPT ---
                    gpt_is_valid_clause=gpt_analysis.get('is_valid_clause', True),
                    gpt_is_abusive=gpt_is_abusive,
                    gpt_explanation=gpt_analysis.get('explanation') or '',
                    gpt_suggested_fix=gpt_analysis.get('abusive_reason') or ''
                    # --- FIN: Limpieza de datos GPT ---
                )
            
            # Actualizar el contrato con los resultados corregidos
            total_clauses = len(analysis_result['clause_results'])
            contract.total_clauses = total_clauses
            contract.abusive_clauses_count = abusive_count
            contract.risk_score = total_risk_score / total_clauses if total_clauses > 0 else 0
            contract.status = 'completed'
            contract.analyzed_at = timezone.now()
            contract.save()
                
        except Exception as e:
            import traceback
            contract.status = 'error'
            contract.save()
            error_msg = f"Error en análisis síncrono: {e}\n{traceback.format_exc()}"
            print(error_msg)
            logger.error(error_msg)


class ClauseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para cláusulas (solo lectura)"""
    serializer_class = ClauseSerializer
    # permission_classes = [IsAuthenticated] # Comentado para deshabilitar la autenticación
    filter_backends = [DjangoFilterBackend]
    # Se añade 'contract' a los campos de filtrado para poder buscar por contrato desde el frontend
    filterset_fields = ['is_abusive', 'clause_type', 'contract'] 
    
    def get_queryset(self):
        """Devuelve todas las cláusulas al no haber autenticación."""
        return Clause.objects.all()
    
    @action(detail=False, methods=['get'])
    def abusive_patterns(self, request):
        """Endpoint para obtener patrones de cláusulas abusivas"""
        abusive_clauses = self.get_queryset().filter(is_abusive=True)
        
        # Agrupar por tipo de cláusula
        patterns = {}
        for clause in abusive_clauses:
            clause_type = clause.clause_type
            if clause_type not in patterns:
                patterns[clause_type] = {
                    'count': 0,
                    'examples': []
                }
            
            patterns[clause_type]['count'] += 1
            if len(patterns[clause_type]['examples']) < 3:
                patterns[clause_type]['examples'].append({
                    'text': clause.text[:200] + '...' if len(clause.text) > 200 else clause.text,
                    'confidence': clause.confidence_score
                })
        
        return Response(patterns)


# Tareas asíncronas con Celery (temporalmente deshabilitado)
# @shared_task
def analyze_contract_task(contract_id: str):
    """Tarea asíncrona para analizar contratos"""
    try:
        contract = Contract.objects.get(id=contract_id)
        contract.status = 'analyzing'
        contract.save()
        
        # Determinar texto a analizar
        text_to_analyze = contract.original_text
        if contract.file_upload and not text_to_analyze:
            # TODO: Implementar extracción de texto de archivos
            # text_to_analyze = extract_text_from_file(contract.file_upload)
            pass
        
        if not text_to_analyze:
            contract.status = 'error'
            contract.save()
            return {'error': 'No text to analyze'}
        
        # Realizar análisis
        analysis_results = ml_service.analyze_contract(text_to_analyze)
        
        # Guardar resultados
        contract.total_clauses = analysis_results['total_clauses']
        contract.abusive_clauses_count = analysis_results['abusive_clauses_count']
        contract.risk_score = analysis_results['risk_score']
        contract.status = 'completed'
        contract.analyzed_at = timezone.now()
        contract.save()
        
        # Crear registro de análisis
        analysis_result, created = AnalysisResult.objects.get_or_create(
            contract=contract,
            defaults={
                'processing_time': analysis_results['processing_time'],
                'executive_summary': analysis_results['executive_summary'],
                'recommendations': analysis_results['recommendations'],
                'features_extracted': {
                    'entities_count': len(analysis_results['entities']),
                    'entities': analysis_results['entities'][:10]  # Limitamos para no sobrecargar
                }
            }
        )
        
        # Guardar cláusulas
        for clause_data in analysis_results['clause_results']:
            clause, created = Clause.objects.get_or_create(
                contract=contract,
                text=clause_data['text'],
                defaults={
                    'clause_number': str(clause_data.get('clause_number', '')),
                    'is_abusive': clause_data['is_abusive'],
                    'confidence_score': clause_data['confidence_score']
                }
            )
            
            # Guardar entidades de la cláusula
            from .models import Entity
            for entity_data in clause_data.get('entities', []):
                Entity.objects.get_or_create(
                    clause=clause,
                    text=entity_data['text'],
                    entity_type=entity_data['label'],
                    defaults={
                        'start_char': entity_data.get('start_char', 0),
                        'end_char': entity_data.get('end_char', 0),
                        'confidence': entity_data.get('confidence', 1.0)
                    }
                )
        
        return {
            'contract_id': contract_id,
            'status': 'completed',
            'results': analysis_results
        }
        
    except Contract.DoesNotExist:
        return {'error': f'Contract {contract_id} not found'}
    except Exception as e:
        # Marcar contrato como error
        try:
            contract = Contract.objects.get(id=contract_id)
            contract.status = 'error'
            contract.save()
        except:
            pass
        
        return {'error': str(e)} 