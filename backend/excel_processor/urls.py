from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExcelUploadViewSet,
    HeaderMappingTemplateViewSet,
    ValidationRuleViewSet,
    ValidationReportViewSet,
    QueueJobViewSet
)

router = DefaultRouter()
router.register(r'excel-uploads', ExcelUploadViewSet, basename='excel-upload')
router.register(r'mapping-templates', HeaderMappingTemplateViewSet, basename='mapping-template')
router.register(r'validation-rules', ValidationRuleViewSet, basename='validation-rule')
router.register(r'validation-reports', ValidationReportViewSet, basename='validation-report')
router.register(r'queue-jobs', QueueJobViewSet, basename='queue-job')

urlpatterns = [
    path('', include(router.urls)),
]
