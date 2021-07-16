from django.urls import path
from .views import ConsultationView


urlpatterns = [
    path('diagnostic/', ConsultationView.as_view(), name='diagnostic'),
]