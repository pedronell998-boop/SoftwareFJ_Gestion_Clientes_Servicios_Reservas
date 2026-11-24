"""Demostración reproducible de catorce operaciones del sistema."""

from datetime import datetime
from decimal import Decimal
from typing import Callable

from software_fj import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    ReservaSala,
    SistemaGestion,
)
from software_fj.excepciones import ErrorSoftwareFJ


def ejecutar_demostracion() -> None:
    """Ejecuta operaciones válidas e inválidas sin interrumpir la demostración."""
    sistema = SistemaGestion()
    print("=" * 72)
    print("SOFTWARE FJ | DEMOSTRACIÓN DE GESTIÓN Y MANEJO DE EXCEPCIONES")
    print("=" * 72)

    operaciones = 0

    def ejecutar(titulo: str, accion: Callable[[], object]) -> None:
        """Ejecuta un caso, informa el resultado y registra los errores controlados."""
        nonlocal operaciones
        operaciones += 1
        print(f"\nOPERACIÓN {operaciones:02d}: {titulo}")
        try:
            resultado = accion()
            if resultado is not None:
                print(f"OK: {resultado}")
        except (ErrorSoftwareFJ, ValueError) as error:
            # Algunos errores nacen al construir objetos, antes de llamar al sistema.
            # Por eso la demostración también los registra en el mismo archivo de logs.
            sistema.logger.exception(
                "Operación demostrativa %02d rechazada (%s): %s",
                operaciones,
                titulo,
                error,
            )
            print(f"ERROR CONTROLADO: {type(error).__name__}: {error}")
            causa = error.__cause__
            if causa:
                print(f"CAUSA ORIGINAL: {type(causa).__name__}: {causa}")

    try:
        # 1. Registro válido de cliente.
        cliente = Cliente("C-001", "Laura Méndez", "laura@example.com", "3001234567")
        ejecutar("Registrar cliente válido", lambda: sistema.registrar_cliente(cliente).describir())

        # 2. El constructor rechaza un correo que no cumple el patrón definido.
        ejecutar(
            "Rechazar cliente con correo inválido",
            lambda: Cliente("C-002", "Carlos Pérez", "correo-invalido", "3007654321"),
        )

        # 3. Se intenta reutilizar un identificador que ya pertenece a otro cliente.
        ejecutar(
            "Rechazar identificador de cliente duplicado",
            lambda: sistema.registrar_cliente(
                Cliente("C-001", "Laura Méndez II", "laura2@example.com", "3009876543")
            ),
        )

        # 4, 5 y 6. Se registran las tres especializaciones de Servicio.
        sala = ReservaSala("S-001", "Sala Ejecutiva", "80000", 12)
        equipo = AlquilerEquipo("S-002", "Proyector HD", "25000", 4)
        asesoria = AsesoriaEspecializada("S-003", "Consultoría TI", "120000", "Tecnología")
        ejecutar("Crear servicio de reserva de sala", lambda: sistema.registrar_servicio(sala).describir())
        ejecutar("Crear servicio de alquiler de equipo", lambda: sistema.registrar_servicio(equipo).describir())
        ejecutar("Crear servicio de asesoría especializada", lambda: sistema.registrar_servicio(asesoria).describir())

        # 7. Se comprueba que una tarifa igual a cero no sea aceptada.
        ejecutar(
            "Rechazar servicio con tarifa igual a cero",
            lambda: ReservaSala("S-004", "Sala inválida", 0, 10),
        )

        # 8. Una solicitud que cumple las reglas genera una reserva confirmada.
        fecha = datetime(2026, 11, 10, 9, 0)
        ejecutar(
            "Crear y confirmar reserva válida",
            lambda: sistema.crear_reserva(
                "R-001", "C-001", "S-001", fecha, 2, personas=8
            ).describir(),
        )

        # 9. La búsqueda del cliente inexistente genera una excepción de dominio.
        ejecutar(
            "Rechazar reserva asociada a cliente inexistente",
            lambda: sistema.crear_reserva("R-002", "C-999", "S-001", fecha, 1, personas=2),
        )

        # 10. El estado inactivo impide utilizar temporalmente el equipo.
        equipo.desactivar()
        ejecutar(
            "Rechazar reserva de un servicio inactivo",
            lambda: sistema.crear_reserva("R-003", "C-001", "S-002", fecha, 1, cantidad=1),
        )
        equipo.activar()  # Se restablece el servicio para las operaciones posteriores.

        # 11. Se intenta reservar una sala en un periodo que se superpone con otro.
        ejecutar(
            "Rechazar cruce de horario en la misma sala",
            lambda: sistema.crear_reserva(
                "R-004", "C-001", "S-001", datetime(2026, 11, 10, 10, 0), 1, personas=4
            ),
        )

        # 12. Se calcula el valor aplicando descuento e impuesto a la tarifa por hora.
        ejecutar(
            "Calcular costo de asesoría con descuento del 10 % e impuesto del 19 %",
            lambda: sistema.calcular_costo("S-003", 2, Decimal("0.10"), Decimal("0.19")),
        )

        # 13. Se cambia el estado de la reserva confirmada a cancelada.
        ejecutar("Cancelar reserva confirmada", lambda: sistema.cancelar_reserva("R-001").describir())

        # 14. Se verifica el total de objetos que permanecen en las listas del sistema.
        ejecutar("Consultar resumen de registros", lambda: sistema.resumen())

        print("\n" + "=" * 72)
        print(f"DEMOSTRACIÓN FINALIZADA: {operaciones} operaciones ejecutadas.")
        print(f"Archivo de eventos y errores: {sistema.ruta_log}")
        print("Los datos de clientes, servicios y reservas se mantuvieron en memoria.")
        print("=" * 72)
    finally:
        # Garantiza que el archivo de log se cierre aun si ocurre un error inesperado.
        sistema.cerrar()


if __name__ == "__main__":
    ejecutar_demostracion()
