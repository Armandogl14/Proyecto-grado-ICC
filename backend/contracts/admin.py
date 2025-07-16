from django.contrib import admin
from .models import Contract, ContractType, Clause, Entity, AnalysisResult

@admin.register(ContractType)
class ContractTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')

class ClauseInline(admin.TabularInline):
    model = Clause
    extra = 0
    fields = ('clause_number', 'text', 'is_abusive', 'confidence_score', 'gpt_is_abusive')
    readonly_fields = ('clause_number', 'text', 'is_abusive', 'confidence_score', 'gpt_is_abusive')
    can_delete = False
    show_change_link = True

class AnalysisResultInline(admin.StackedInline):
    model = AnalysisResult
    extra = 0
    readonly_fields = ('processing_time', 'model_version', 'executive_summary', 'recommendations')
    can_delete = False

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('title', 'contract_type', 'status', 'risk_level', 'uploaded_by', 'created_at')
    list_filter = ('status', 'contract_type', 'risk_score')
    search_fields = ('title', 'original_text')
    readonly_fields = ('id', 'created_at', 'updated_at', 'analyzed_at', 'risk_level')
    
    fieldsets = (
        ('Información General', {
            'fields': ('title', 'contract_type', 'uploaded_by', 'status')
        }),
        ('Contenido del Contrato', {
            'fields': ('original_text', 'file_upload'),
            'classes': ('collapse',)
        }),
        ('Resultados del Análisis', {
            'fields': ('total_clauses', 'abusive_clauses_count', 'risk_score')
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at', 'analyzed_at')
        }),
    )
    
    inlines = [ClauseInline, AnalysisResultInline]

    def risk_level(self, obj):
        return obj.risk_level
    risk_level.short_description = 'Nivel de Riesgo'

@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'contract', 'is_abusive', 'confidence_score', 'gpt_is_abusive')
    list_filter = ('is_abusive', 'gpt_is_abusive', 'clause_type')
    search_fields = ('text', 'contract__title')
    readonly_fields = ('id', 'contract', 'text')

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('text', 'entity_type', 'clause')
    list_filter = ('entity_type',)
    search_fields = ('text',) 