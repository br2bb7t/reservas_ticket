from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from .serializers import ReservaSerializer
from .tasks import procesar_reserva
from .models import Reserva, Evento

class ReservaAPIView(APIView):
    def post(self, request):
        serializer = ReservaSerializer(data=request.data)
        
        if serializer.is_valid():       
            reserva = Reserva.objects.create(
                nombre_cliente=serializer.validated_data['nombre_cliente'],
                cantidad_tickets=serializer.validated_data['cantidad_tickets'],
                estado='pendiente',
                evento=serializer.validated_data.get('evento') 
            )
            
            # Cambiar el estado a 'procesando' y guardar
            reserva.estado = 'procesando'
            reserva.save()
            
            # Enviar tarea a Celery
            procesar_reserva.delay(reserva.id)
            
            return Response({"message": "Reservation is being processed", "reserva_id": reserva.id}, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelarReservaAPIView(APIView):
    def delete(self, request, reserva_id):
        try:
            reserva = Reserva.objects.get(id=reserva_id)

            if reserva.estado in ['completada', 'cancelada']:
                return Response({"error": "Reservation cannot be canceled as it is already completed or canceled"},
                                status=status.HTTP_400_BAD_REQUEST)

            # Obtener el evento relacionado
            evento = reserva.evento

            # Liberar los tickets reservados
            evento.reserved_tickets -= reserva.cantidad_tickets
            evento.save()

            # Cancelar la reserva (cambiar su estado)
            reserva.estado = 'cancelada'
            reserva.save()

            return Response({"message": "Reservation canceled successfully and tickets released"}, 
                            status=status.HTTP_204_NO_CONTENT)

        except Reserva.DoesNotExist:
            return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)
        except Evento.DoesNotExist:
            return Response({"error": "Event related to the reservation not found"}, status=status.HTTP_404_NOT_FOUND)
