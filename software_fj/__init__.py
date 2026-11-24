"""Interfaz pública del paquete Software FJ.

Las importaciones de este módulo permiten utilizar las clases principales
sin tener que conocer la ubicación interna de cada definición.
"""

from .modelos import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    Entidad,
    EstadoReserva,
    Reserva,
    ReservaSala,
    Servicio,
)
from .sistema import SistemaGestion

# __all__ delimita los elementos que se consideran parte de la API del paquete.
__all__ = [
    "AlquilerEquipo", "AsesoriaEspecializada", "Cliente", "Entidad",
    "EstadoReserva", "Reserva", "ReservaSala", "Servicio", "SistemaGestion",
]
