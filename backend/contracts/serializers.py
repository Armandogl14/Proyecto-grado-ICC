from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Contract, ContractType, Clause, Entity, AnalysisResult


class ClauseAnalysisSerializer(serializers.Serializer):
    text = serializers.CharField()
    ml_analysis = serializers.DictField()
    gpt_analysis = serializers.DictField()
    entities = serializers.ListField()
    risk_score = serializers.FloatField()
    clause_number = serializers.IntegerField(required=False)

class ContractAnalysisSerializer(serializers.Serializer):
    total_clauses = serializers.IntegerField()
    abusive_clauses_count = serializers.IntegerField()
    risk_score = serializers.FloatField()
    processing_time = serializers.FloatField()
    clause_results = ClauseAnalysisSerializer(many=True)
    entities = serializers.ListField()
    executive_summary = serializers.CharField()
    recommendations = serializers.CharField()

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
    ml_analysis = serializers.SerializerMethodField()
    gpt_analysis = serializers.SerializerMethodField()
    risk_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Clause
        fields = [
            'id', 'text', 'clause_number', 'clause_type',
            'is_abusive', 'confidence_score', 'start_position',
            'end_position', 'entities', 'created_at',
            'ml_analysis', 'gpt_analysis', 'risk_score'
        ]
    
    def get_ml_analysis(self, obj):
        """Transform clause data into ML analysis format expected by frontend"""
        return {
            'is_abusive': obj.is_abusive,
            'abuse_probability': obj.confidence_score if obj.confidence_score is not None else 0.0
        }
    
    def get_gpt_analysis(self, obj):
        """Transform clause data into GPT analysis format expected by frontend"""
        return {
            'is_valid_clause': obj.gpt_is_valid_clause,
            'is_abusive': obj.gpt_is_abusive,
            'explanation': obj.gpt_explanation or f"Cláusula {'abusiva' if obj.gpt_is_abusive else 'no abusiva'} según análisis GPT.",
            'suggested_fix': obj.gpt_suggested_fix or ("Consulte con un abogado para revisar esta cláusula." if obj.gpt_is_abusive else "")
        }
    
    def get_risk_score(self, obj):
        """Return risk score, ensuring it's never NaN"""
        if obj.confidence_score is None:
            return 0.0
        
        # Calcular risk score considerando ambos análisis
        risk_score = obj.confidence_score
        
        # Si GPT detecta como abusiva, aumentar el risk score
        if obj.gpt_is_abusive:
            risk_score = max(risk_score, 0.8)  # Mínimo 80% si GPT dice que es abusiva
        
        return risk_score


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
    
    # Se elimina el método `create` para que no asigne automáticamente el usuario de la petición.
    # La asignación del usuario se hará explícitamente en la vista.


class ContractSerializer(serializers.ModelSerializer):
    contract_type = ContractTypeSerializer(read_only=True)
    contract_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ContractType.objects.all(),
        source='contract_type',
        write_only=True
    )
    analysis_result = ContractAnalysisSerializer(read_only=True)

    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'status', 'analysis_result')


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