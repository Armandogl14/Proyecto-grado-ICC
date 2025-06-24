from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class ContractType(models.Model):
    """Tipos de contratos (Alquiler, Venta, Hipoteca, etc.)"""
    
    ALQUILER = 'ALC'
    VENTA_VEHICULO = 'VM'
    HIPOTECA = 'HIP'
    SOCIEDAD = 'CSP'
    RESCISION = 'RC'
    ARMA_FUEGO = 'VTAF'
    VENTA_VIVIENDA = 'VV'
    OTRO = 'OTR'
    
    CONTRACT_TYPES = [
        (ALQUILER, 'Contrato de Alquiler'),
        (VENTA_VEHICULO, 'Venta de Vehículo'),
        (HIPOTECA, 'Hipoteca'),
        (SOCIEDAD, 'Sociedad en Participación'),
        (RESCISION, 'Rescisión de Contrato'),
        (ARMA_FUEGO, 'Venta y Traspaso de Arma de Fuego'),
        (VENTA_VIVIENDA, 'Venta de Vivienda'),
        (OTRO, 'Otro'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, choices=CONTRACT_TYPES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tipo de Contrato"
        verbose_name_plural = "Tipos de Contratos"
    
    def __str__(self):
        return self.name


class Contract(models.Model):
    """Modelo principal para contratos"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente de Análisis'),
        ('analyzing', 'Analizando'),
        ('completed', 'Análisis Completado'),
        ('error', 'Error en Análisis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    contract_type = models.ForeignKey(ContractType, on_delete=models.CASCADE)
    original_text = models.TextField(help_text="Texto completo del contrato")
    file_upload = models.FileField(upload_to='contracts/', blank=True, null=True)
    
    # Metadatos
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    # Resultados del análisis
    total_clauses = models.IntegerField(default=0)
    abusive_clauses_count = models.IntegerField(default=0)
    risk_score = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Puntuación de riesgo entre 0 y 1"
    )
    
    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.contract_type.name}"
    
    @property
    def risk_level(self):
        """Devuelve el nivel de riesgo basado en el score"""
        if self.risk_score is None:
            return "No Analizado"
        elif self.risk_score < 0.3:
            return "Bajo"
        elif self.risk_score < 0.7:
            return "Medio"
        else:
            return "Alto"


class Clause(models.Model):
    """Cláusulas individuales extraídas de los contratos"""
    
    CLAUSE_TYPES = [
        ('general', 'General'),
        ('payment', 'Pago'),
        ('duration', 'Duración'),
        ('obligations', 'Obligaciones'),
        ('termination', 'Terminación'),
        ('dispute_resolution', 'Resolución de Disputas'),
        ('other', 'Otro'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='clauses')
    text = models.TextField(help_text="Texto de la cláusula")
    clause_number = models.CharField(max_length=20, blank=True)
    clause_type = models.CharField(max_length=20, choices=CLAUSE_TYPES, default='general')
    
    # Análisis ML
    is_abusive = models.BooleanField(default=False)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confianza del modelo ML (0-1)"
    )
    
    # Posición en el documento
    start_position = models.IntegerField(null=True, blank=True)
    end_position = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cláusula"
        verbose_name_plural = "Cláusulas"
        ordering = ['contract', 'clause_number']
    
    def __str__(self):
        return f"{self.contract.title} - Cláusula {self.clause_number}"


class Entity(models.Model):
    """Entidades extraídas por NER (spaCy)"""
    
    ENTITY_TYPES = [
        ('PER', 'Persona'),
        ('ORG', 'Organización'),
        ('LOC', 'Ubicación'),
        ('MONEY', 'Dinero'),
        ('DATE', 'Fecha'),
        ('MISC', 'Misceláneo'),
        ('PARTES_CONTRATO', 'Partes del Contrato'),
    ]
    
    clause = models.ForeignKey(Clause, on_delete=models.CASCADE, related_name='entities')
    text = models.CharField(max_length=500)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    start_char = models.IntegerField()
    end_char = models.IntegerField()
    confidence = models.FloatField(default=1.0)
    
    class Meta:
        verbose_name = "Entidad"
        verbose_name_plural = "Entidades"
    
    def __str__(self):
        return f"{self.text} ({self.entity_type})"


class AnalysisResult(models.Model):
    """Resultados detallados del análisis"""
    
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='analysis_result')
    
    # Métricas generales
    processing_time = models.FloatField(help_text="Tiempo de procesamiento en segundos")
    model_version = models.CharField(max_length=50, default="1.0")
    
    # Resumen ejecutivo
    executive_summary = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Datos técnicos
    ml_model_accuracy = models.FloatField(null=True, blank=True)
    features_extracted = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Resultado de Análisis"
        verbose_name_plural = "Resultados de Análisis"
    
    def __str__(self):
        return f"Análisis de {self.contract.title}" 