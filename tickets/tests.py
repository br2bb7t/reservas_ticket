from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Reserva, Evento

class ReservaAPITestCase(APITestCase):

    def test_create_reserva(self):
        """
        Prueba la creación de una nueva reserva.
        """
        evento = Evento.objects.create(nombre="Concierto de Rock", total_tickets=100)

        url = reverse('create_reserva')
        data = {
            "nombre_cliente": "Juan Pérez",
            "cantidad_tickets": 3,
            "evento": evento.id
        }
        
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["message"], "Reservation is being processed")
        
        reserva = Reserva.objects.get(nombre_cliente="Juan Pérez")
        self.assertEqual(reserva.estado, "pendiente")
        self.assertEqual(reserva.evento.id, evento.id)

    def test_cancel_reserva(self):
        """
        Prueba la cancelación de una reserva existente.
        """
        evento = Evento.objects.create(nombre="Concierto de Rock", total_tickets=100)
        reserva = Reserva.objects.create(nombre_cliente="Juan Pérez", cantidad_tickets=2, estado="pendiente", evento=evento)
        
        url = reverse('cancel_reserva', args=[reserva.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["message"], "Reservation canceled successfully and tickets released")
        
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, "cancelada")
        
        evento.refresh_from_db()
        self.assertEqual(evento.reserved_tickets, 0)

    def test_cancel_reserva_not_found(self):
        """
        Prueba la cancelación de una reserva que no existe.
        """
        url = reverse('cancel_reserva', args=[9999])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Reservation not found")
    
    def test_create_reserva_not_enough_tickets(self):
        """
        Prueba la creación de una reserva cuando no hay suficientes tickets disponibles.
        """
        evento = Evento.objects.create(nombre="Concierto de Rock", total_tickets=3)
        
        url = reverse('create_reserva')
        data = {
            "nombre_cliente": "Juan Pérez",
            "cantidad_tickets": 5,
            "evento": evento.id
        }
        
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Not enough tickets available.")

    def test_cancel_reserva_release_tickets(self):
        """
        Verifica que los tickets se liberen al cancelar una reserva.
        """
        evento = Evento.objects.create(nombre="Concierto de Rock", total_tickets=100, reserved_tickets=20)
        reserva = Reserva.objects.create(nombre_cliente="Juan Pérez", cantidad_tickets=2, estado="pendiente", evento=evento)

        evento.refresh_from_db()
        self.assertEqual(evento.reserved_tickets, 20)

        url = reverse('cancel_reserva', args=[reserva.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["message"], "Reservation canceled successfully and tickets released")
        
        evento.refresh_from_db()
        self.assertEqual(evento.reserved_tickets, 18)
