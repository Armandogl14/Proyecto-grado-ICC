from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Contract, ContractType, Clause, Entity, AnalysisResult


class ContractTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractType
        fields = '__all__'


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'


class ClauseSerializer(serializers.ModelSerializer):
    entities = EntitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Clause
        fields = [
            'id', 'text', 'clause_number', 'clause_type',
            'is_abusive', 'confidence_score', 'start_position',
            'end_position', 'entities', 'created_at'
        ]


class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = '__all__'


class ContractListSerializer(serializers.ModelSerializer):
    """Serializer para listado de contratos (información básica)"""
    contract_type_name = serializers.CharField(source='contract_type.name', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id', 'title', 'contract_type', 'contract_type_name',
            'status', 'created_at', 'analyzed_at', 'total_clauses',
            'abusive_clauses_count', 'risk_score', 'risk_level',
            'uploaded_by_username'
        ]


class ContractDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle completo del contrato"""
    contract_type = ContractTypeSerializer(read_only=True)
    clauses = ClauseSerializer(many=True, read_only=True)
    analysis_result = AnalysisResultSerializer(read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id', 'title', 'contract_type', 'original_text',
            'uploaded_by_username', 'status', 'created_at',
            'updated_at', 'analyzed_at', 'total_clauses',
            'abusive_clauses_count', 'risk_score', 'risk_level',
            'clauses', 'analysis_result'
        ]


class ContractCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevos contratos"""
    
    class Meta:
        model = Contract
        fields = [
            'id', 'title', 'contract_type', 'original_text', 'file_upload'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        # El usuario se asigna automáticamente desde la vista
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class ContractAnalysisSerializer(serializers.Serializer):
    """Serializer para iniciar análisis de contrato"""
    contract_id = serializers.UUIDField()
    force_reanalysis = serializers.BooleanField(default=False)


class BulkAnalysisSerializer(serializers.Serializer):
    """Serializer para análisis masivo de contratos"""
    contract_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False
    )
    force_reanalysis = serializers.BooleanField(default=False) 