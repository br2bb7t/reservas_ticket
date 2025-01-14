from celery import shared_task
from .models import Reserva, Evento
from django.db import transaction
from django.core.exceptions import ValidationError

@shared_task
def procesar_reserva(reserva_id):
    try:
        with transaction.atomic():
            # Obtener la reserva
            reserva = Reserva.objects.select_for_update().get(id=reserva.id)
            
            evento = Evento.objects.get(id=reserva.evento_id)

            # Verificar si hay suficiente disponibilidad de tickets
            if evento.total_tickets - evento.reserved_tickets < reserva.cantidad_tickets:
                raise ValidationError(f"No hay suficientes tickets disponibles. Solo hay {evento.total_tickets - evento.reserved_tickets} tickets disponibles.")
            
            # Si hay suficientes tickets, actualizar los valores de tickets reservados
            evento.reserved_tickets += reserva.cantidad_tickets
            evento.save()

            # Actualizar el estado de la reserva a 'completada'
            reserva.estado = 'completada'
            reserva.save()
    
    except Reserva.DoesNotExist:
        raise ValidationError("La reserva no existe.")
    except Evento.DoesNotExist:
        raise ValidationError("El evento relacionado con la reserva no existe.")
    except ValidationError as e:
        # En caso de error de validación, actualizar el estado de la reserva a 'cancelada'
        reserva.estado = 'cancelada'
        reserva.save()
        raise e
