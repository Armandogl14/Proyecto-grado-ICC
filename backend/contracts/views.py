from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from celery import shared_task

from .models import Contract, ContractType, Clause, AnalysisResult
from .serializers import (
    ContractListSerializer, ContractDetailSerializer, ContractCreateSerializer,
    ContractTypeSerializer, ClauseSerializer, ContractAnalysisSerializer,
    BulkAnalysisSerializer
)
from ml_analysis.ml_service import ml_service


class ContractTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de contratos (solo lectura)"""
    queryset = ContractType.objects.all()
    serializer_class = ContractTypeSerializer
    permission_classes = [IsAuthenticated]


class ContractViewSet(viewsets.ModelViewSet):
    """ViewSet principal para contratos con funcionalidades completas"""
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'contract_type', 'risk_score']
    
    def get_queryset(self):
        """Filtrar contratos por usuario"""
        return Contract.objects.filter(uploaded_by=self.request.user)
    
    def get_serializer_class(self):
        """Usar diferentes serializers según la acción"""
        if self.action == 'list':
            return ContractListSerializer
        elif self.action == 'create':
            return ContractCreateSerializer
        else:
            return ContractDetailSerializer
    
    def perform_create(self, serializer):
        """Asignar usuario al crear contrato"""
        contract = serializer.save(uploaded_by=self.request.user)
        
        # Iniciar análisis automáticamente si es texto
        if contract.original_text:
            self.trigger_analysis(contract.id)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Endpoint para analizar un contrato específico"""
        contract = self.get_object()
        serializer = ContractAnalysisSerializer(data={'contract_id': contract.id})
        
        if serializer.is_valid():
            force_reanalysis = serializer.validated_data.get('force_reanalysis', False)
            
            # Verificar si ya fue analizado
            if contract.status == 'completed' and not force_reanalysis:
                return Response({
                    'message': 'El contrato ya fue analizado',
                    'contract_id': contract.id,
                    'status': contract.status
                }, status=status.HTTP_200_OK)
            
            # Iniciar análisis
            task_result = analyze_contract_task.delay(str(contract.id))
            
            # Actualizar estado
            contract.status = 'analyzing'
            contract.save()
            
            return Response({
                'message': 'Análisis iniciado',
                'contract_id': contract.id,
                'task_id': task_result.id,
                'status': 'analyzing'
            }, status=status.HTTP_202_ACCEPTED)
        
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
            
            # Iniciar análisis para cada contrato
            task_results = []
            for contract in contracts:
                if contract.status != 'completed' or force_reanalysis:
                    task_result = analyze_contract_task.delay(str(contract.id))
                    task_results.append({
                        'contract_id': contract.id,
                        'task_id': task_result.id
                    })
                    
                    contract.status = 'analyzing'
                    contract.save()
            
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
        """Método auxiliar para iniciar análisis"""
        analyze_contract_task.delay(str(contract_id))


class ClauseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para cláusulas (solo lectura)"""
    serializer_class = ClauseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_abusive', 'clause_type']
    
    def get_queryset(self):
        """Filtrar cláusulas por contratos del usuario"""
        return Clause.objects.filter(
            contract__uploaded_by=self.request.user
        )
    
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


# Tareas asíncronas con Celery
@shared_task
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