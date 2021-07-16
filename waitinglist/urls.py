from django.urls import path
from .views import WaitingListView

urlpatterns = [
    path('waitinglist/delete', WaitingListView.as_view(), name='waitinglist-delete'),
]