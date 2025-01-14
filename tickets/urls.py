from django.urls import path
from .views import ReservaAPIView, CancelarReservaAPIView

urlpatterns = [
    path('', ReservaAPIView.as_view(), name='create_reserva'),
    path('cancelar/<int:reserva_id>/', CancelarReservaAPIView.as_view(), name='cancel_reserva'),
]
