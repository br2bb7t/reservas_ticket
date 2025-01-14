from django.db import models

class Evento(models.Model):
    nombre = models.CharField(max_length=255)
    total_tickets = models.PositiveIntegerField()  # Total de tickets disponibles
    reserved_tickets = models.PositiveIntegerField(default=0)  # Tickets reservados

    def __str__(self):
        return f"{self.nombre} - {self.total_tickets} tickets disponibles"
        
class Reserva(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('procesando', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    )

    nombre_cliente = models.CharField(max_length=255)
    cantidad_tickets = models.PositiveIntegerField()
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)  # Relación con Evento

    def __str__(self):
        return f"Reservation for {self.nombre_cliente} ({self.cantidad_tickets} tickets)"



