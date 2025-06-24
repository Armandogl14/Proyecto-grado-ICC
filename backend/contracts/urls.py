from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'contracts', views.ContractViewSet, basename='contracts')
router.register(r'contract-types', views.ContractTypeViewSet, basename='contract-types')
router.register(r'clauses', views.ClauseViewSet, basename='clauses')

app_name = 'contracts'

urlpatterns = [
    path('api/', include(router.urls)),
] 