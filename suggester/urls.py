from django.urls import path
from .views import AnalyzeView

urlpatterns = [
    path('api/analyze/', AnalyzeView.as_view(), name='analyze'),
]