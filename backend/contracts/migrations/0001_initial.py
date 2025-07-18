# Generated by Django 5.2.3 on 2025-06-25 02:12

import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ContractType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "code",
                    models.CharField(
                        choices=[
                            ("ALC", "Contrato de Alquiler"),
                            ("VM", "Venta de Vehículo"),
                            ("HIP", "Hipoteca"),
                            ("CSP", "Sociedad en Participación"),
                            ("RC", "Rescisión de Contrato"),
                            ("VTAF", "Venta y Traspaso de Arma de Fuego"),
                            ("VV", "Venta de Vivienda"),
                            ("OTR", "Otro"),
                        ],
                        max_length=10,
                        unique=True,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Tipo de Contrato",
                "verbose_name_plural": "Tipos de Contratos",
            },
        ),
        migrations.CreateModel(
            name="Contract",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                (
                    "original_text",
                    models.TextField(help_text="Texto completo del contrato"),
                ),
                (
                    "file_upload",
                    models.FileField(blank=True, null=True, upload_to="contracts/"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendiente de Análisis"),
                            ("analyzing", "Analizando"),
                            ("completed", "Análisis Completado"),
                            ("error", "Error en Análisis"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("analyzed_at", models.DateTimeField(blank=True, null=True)),
                ("total_clauses", models.IntegerField(default=0)),
                ("abusive_clauses_count", models.IntegerField(default=0)),
                (
                    "risk_score",
                    models.FloatField(
                        blank=True,
                        help_text="Puntuación de riesgo entre 0 y 1",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(1.0),
                        ],
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "contract_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contracts.contracttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Contrato",
                "verbose_name_plural": "Contratos",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Clause",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("text", models.TextField(help_text="Texto de la cláusula")),
                ("clause_number", models.CharField(blank=True, max_length=20)),
                (
                    "clause_type",
                    models.CharField(
                        choices=[
                            ("general", "General"),
                            ("payment", "Pago"),
                            ("duration", "Duración"),
                            ("obligations", "Obligaciones"),
                            ("termination", "Terminación"),
                            ("dispute_resolution", "Resolución de Disputas"),
                            ("other", "Otro"),
                        ],
                        default="general",
                        max_length=20,
                    ),
                ),
                ("is_abusive", models.BooleanField(default=False)),
                (
                    "confidence_score",
                    models.FloatField(
                        help_text="Confianza del modelo ML (0-1)",
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(1.0),
                        ],
                    ),
                ),
                ("start_position", models.IntegerField(blank=True, null=True)),
                ("end_position", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "contract",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="clauses",
                        to="contracts.contract",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cláusula",
                "verbose_name_plural": "Cláusulas",
                "ordering": ["contract", "clause_number"],
            },
        ),
        migrations.CreateModel(
            name="AnalysisResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "processing_time",
                    models.FloatField(help_text="Tiempo de procesamiento en segundos"),
                ),
                ("model_version", models.CharField(default="1.0", max_length=50)),
                ("executive_summary", models.TextField(blank=True)),
                ("recommendations", models.TextField(blank=True)),
                ("ml_model_accuracy", models.FloatField(blank=True, null=True)),
                ("features_extracted", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "contract",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analysis_result",
                        to="contracts.contract",
                    ),
                ),
            ],
            options={
                "verbose_name": "Resultado de Análisis",
                "verbose_name_plural": "Resultados de Análisis",
            },
        ),
        migrations.CreateModel(
            name="Entity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=500)),
                (
                    "entity_type",
                    models.CharField(
                        choices=[
                            ("PER", "Persona"),
                            ("ORG", "Organización"),
                            ("LOC", "Ubicación"),
                            ("MONEY", "Dinero"),
                            ("DATE", "Fecha"),
                            ("MISC", "Misceláneo"),
                            ("PARTES_CONTRATO", "Partes del Contrato"),
                        ],
                        max_length=20,
                    ),
                ),
                ("start_char", models.IntegerField()),
                ("end_char", models.IntegerField()),
                ("confidence", models.FloatField(default=1.0)),
                (
                    "clause",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entities",
                        to="contracts.clause",
                    ),
                ),
            ],
            options={
                "verbose_name": "Entidad",
                "verbose_name_plural": "Entidades",
            },
        ),
    ]
