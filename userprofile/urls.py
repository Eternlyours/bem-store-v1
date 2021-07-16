from django.urls import path
from .views import UserProfile


urlpatterns = [
    path('user/', UserProfile.as_view(), name='profile'),
]
