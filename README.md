# Reservations API - Proyecto Django

## Descripción

Este proyecto implementa una API de reservas de tickets para eventos utilizando Django y Django REST Framework, con la gestión de concurrencia a través de Celery y Redis. La API permite a los usuarios realizar reservas de tickets, procesarlas de manera asíncrona y gestionar la liberación de tickets cuando se cancelan las reservas.

<p align="center">
  ![Diagrama-C4](https://github.com/user-attachments/assets/069a9c6f-e9a2-4023-899a-1d5644fd268f)
</p>

---

![Diagrama-Secuencia](https://github.com/user-attachments/assets/6b263610-df11-45af-ae3f-893d8de904d5)


# Flujo de la API
## Reserva de Tickets

Cuando un usuario realiza una solicitud para reservar tickets, la API:

1. Valida los datos de la solicitud: Verifica si los datos enviados en la solicitud son correctos.
2. Crea una nueva reserva: Si los datos son válidos, se crea una nueva reserva en la base de datos con el estado inicial de `pendiente`.
3. Envía una tarea a Celery: La reserva se procesa de manera asíncrona en segundo plano, lo que asegura que el sistema pueda manejar múltiples solicitudes concurrentes sin bloqueo.
4. Actualiza el estado de la reserva: Al final del procesamiento, el estado de la reserva se actualiza a `completada` o, si hay un error, se cambia a `cancelada`.
5. Cancelación de Reservas

Si un usuario desea cancelar su reserva, la API:

1. Verifica el estado de la reserva: Si la reserva está en un estado `completada` o `cancelada`, no puede ser cancelada nuevamente.
2. Libera los tickets reservados: La cantidad de tickets reservados en el evento se actualiza, liberando los tickets que previamente fueron reservados.
3. Actualiza el estado de la reserva: Una vez liberados los tickets, la reserva pasa a tener el estado `cancelada`.

## Tareas Asíncronas con Celery
# procesar_reserva (Celery Task)

Esta tarea asíncrona procesa la reserva de tickets. Al ser llamada por Celery, realiza lo siguiente:

1. Bloquea la reserva y el evento con `select_for_update()`: Garantiza que la reserva y los eventos sean modificados de manera exclusiva.
2. Verifica la disponibilidad de tickets: Si no hay suficientes tickets, lanza una excepción.
3. Actualiza los tickets reservados: Si la reserva es exitosa, actualiza los tickets reservados en el evento y cambia el estado de la reserva a `completada`.
4. Manejo de errores: Si se produce un error de validación, el estado de la reserva se cambia a `cancelada`.

---

## Requisitos

- **Python 3.8+**
- **SQLite**
- **Poetry** (para la gestión de dependencias)
- **Django** y **Django REST Framework**
- **Celery** (para el manejo de tareas asíncronas)
- **Redis** (como broker de Celery)

---

## Pasos para la Instalación

### 1. Clonar el Repositorio

Primero, clona el repositorio del proyecto en tu máquina local:

```bash
git clone https://github.com/tu_usuario/reservas-ticket.git
cd reservas-ticket
```

### 2. Instalar Poetry
Si no tienes Poetry instalado, puedes hacerlo de la siguiente forma:

En macOS/Linux:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

En Windows:

Sigue las instrucciones oficiales en Poetry Docs.


### 3. Crear y Activar un Entorno Virtual con Poetry

Dentro del directorio de tu proyecto, ejecuta:

```bash
poetry install
poetry shell
```

### 4. Construir y Levantar los Contenedores
Para construir las imagenes y levantar los contenedores, ejecuta:

```bash
docker-compose up --build
```

El servidor estará disponible en http://localhost:8000/.

## Uso de la API
### Documentación de la API (Swagger)
Accede a la documentación interactiva de la API usando Swagger en:

```bash
http://localhost:8000/swagger/
```
