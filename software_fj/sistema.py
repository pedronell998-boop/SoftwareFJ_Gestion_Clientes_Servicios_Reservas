"""Servicios de aplicación, validación de operaciones y registro de eventos."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from typing import Optional

from .excepciones import (
    ClienteNoEncontradoError,
    DatosInvalidosError,
    EntidadDuplicadaError,
    ErrorSoftwareFJ,
    ReservaNoEncontradaError,
    ServicioNoDisponibleError,
    ServicioNoEncontradoError,
)
from .modelos import AlquilerEquipo, Cliente, Reserva, Servicio


class SistemaGestion:
    """Administra clientes, servicios y reservas mediante listas en memoria."""

    def __init__(self, directorio_logs: Optional[Path] = None) -> None:
        # Las colecciones se conservan en memoria durante la sesión.
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        raiz = Path(__file__).resolve().parent.parent
        self.directorio_logs = Path(directorio_logs) if directorio_logs else raiz / "logs"
        # Se crea el directorio de logs si todavía no existe.
        self.directorio_logs.mkdir(parents=True, exist_ok=True)
        self.ruta_log = self.directorio_logs / "software_fj.log"
        self.logger = logging.getLogger(f"software_fj.{id(self)}")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        if not self.logger.handlers:
            manejador = logging.FileHandler(self.ruta_log, encoding="utf-8")
            manejador.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
            )
            self.logger.addHandler(manejador)
        # El formato incluye fecha, nivel y mensaje para facilitar la trazabilidad.
        self.logger.info("Sistema Software FJ inicializado.")

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        """Registra un cliente y evita identificadores o correos duplicados."""
        try:
            if not isinstance(cliente, Cliente):
                raise DatosInvalidosError("Solo se pueden registrar objetos Cliente.")
            if any(c.identificador == cliente.identificador for c in self.clientes):
                raise EntidadDuplicadaError(
                    f"Ya existe un cliente con ID {cliente.identificador}."
                )
            if any(c.correo == cliente.correo for c in self.clientes):
                raise EntidadDuplicadaError(
                    f"El correo {cliente.correo} ya está asociado a otro cliente."
                )
        except ErrorSoftwareFJ as error:
            # exception() incorpora la traza del error, no solo su descripción.
            self.logger.exception("Error al registrar cliente: %s", error)
            raise
        else:
            self.clientes.append(cliente)
            self.logger.info("Cliente registrado: %s", cliente.identificador)
            return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        """Registra un servicio especializado después de validar su identidad."""
        try:
            if not isinstance(servicio, Servicio):
                raise DatosInvalidosError("El objeto recibido no corresponde a un Servicio.")
            if any(s.identificador == servicio.identificador for s in self.servicios):
                raise EntidadDuplicadaError(
                    f"Ya existe un servicio con ID {servicio.identificador}."
                )
        except ErrorSoftwareFJ as error:
            self.logger.exception("Error al registrar servicio: %s", error)
            raise
        else:
            self.servicios.append(servicio)
            self.logger.info("Servicio registrado: %s", servicio.identificador)
            return servicio

    def buscar_cliente(self, identificador: str) -> Cliente:
        """Busca un cliente por su identificador."""
        for cliente in self.clientes:
            if cliente.identificador == identificador:
                return cliente
        raise ClienteNoEncontradoError(f"No existe el cliente {identificador}.")

    def buscar_servicio(self, identificador: str) -> Servicio:
        """Busca un servicio por su identificador."""
        for servicio in self.servicios:
            if servicio.identificador == identificador:
                return servicio
        raise ServicioNoEncontradoError(f"No existe el servicio {identificador}.")

    def buscar_reserva(self, identificador: str) -> Reserva:
        """Busca una reserva por su identificador."""
        for reserva in self.reservas:
            if reserva.identificador == identificador:
                return reserva
        raise ReservaNoEncontradaError(f"No existe la reserva {identificador}.")

    @staticmethod
    def convertir_fecha(fecha_texto: str) -> datetime:
        """Convierte una fecha ISO y encadena el ValueError si el formato es incorrecto."""
        try:
            return datetime.fromisoformat(fecha_texto)
        except (TypeError, ValueError) as error:
            raise DatosInvalidosError(
                "La fecha debe usar el formato AAAA-MM-DD HH:MM."
            ) from error

    def _validar_cruce_horario(self, nueva: Reserva) -> None:
        """Impide reservar el mismo servicio en periodos que se superponen."""
        # Se comparan intervalos: dos reservas se cruzan si cada una empieza
        # antes de que termine la otra. Solo cuentan reservas confirmadas.
        reservas_superpuestas = [
            existente
            for existente in self.reservas
            if (
                existente.servicio.identificador == nueva.servicio.identificador
                and existente.estado.value == "Confirmada"
                and nueva.fecha_inicio < existente.fecha_fin
                and existente.fecha_inicio < nueva.fecha_fin
            )
        ]
        if isinstance(nueva.servicio, AlquilerEquipo):
            unidades_comprometidas = sum(reserva.cantidad for reserva in reservas_superpuestas)
            if unidades_comprometidas + nueva.cantidad > nueva.servicio.unidades_disponibles:
                raise ServicioNoDisponibleError(
                    "No hay suficientes unidades de equipo para cubrir las reservas que coinciden en ese horario."
                )
        elif reservas_superpuestas:
            raise ServicioNoDisponibleError(
                f"El servicio {nueva.servicio.nombre} ya tiene una reserva confirmada en ese horario."
            )

    def crear_reserva(
        self,
        identificador: str,
        cliente_id: str,
        servicio_id: str,
        fecha_inicio: datetime | str,
        duracion: object,
        cantidad: object = 1,
        personas: Optional[object] = None,
        descuento: object = 0,
        impuesto: object = 0.19,
    ) -> Reserva:
        """Crea y confirma una reserva; registra errores y garantiza el cierre del proceso."""
        try:
            cliente = self.buscar_cliente(cliente_id)
            servicio = self.buscar_servicio(servicio_id)
            fecha = self.convertir_fecha(fecha_inicio) if isinstance(fecha_inicio, str) else fecha_inicio
            nueva = Reserva(
                identificador, cliente, servicio, fecha, duracion,
                cantidad, personas, descuento, impuesto
            )
            self._validar_cruce_horario(nueva)
            nueva.procesar()
        except ErrorSoftwareFJ as error:
            # Registra el fallo y vuelve a elevarlo para que la interfaz lo informe.
            self.logger.exception("No se pudo crear la reserva %s: %s", identificador, error)
            raise
        else:
            # else se ejecuta únicamente si todas las validaciones terminaron bien.
            self.reservas.append(nueva)
            self.logger.info("Reserva confirmada: %s", identificador)
            return nueva
        finally:
            # finally registra el cierre del intento, sea exitoso o fallido.
            self.logger.info("Finalizó el intento de creación de reserva %s.", identificador)

    def cancelar_reserva(self, identificador: str) -> Reserva:
        """Cancela una reserva y registra el cambio de estado."""
        try:
            reserva = self.buscar_reserva(identificador)
            reserva.cancelar()
        except ErrorSoftwareFJ as error:
            self.logger.exception("Error al cancelar reserva %s: %s", identificador, error)
            raise
        else:
            self.logger.info("Reserva cancelada: %s", identificador)
            return reserva

    def calcular_costo(
        self,
        servicio_id: str,
        duracion: object = 1,
        descuento: object = 0,
        impuesto: object = 0.19,
        cantidad: object = 1,
        personas: Optional[object] = None,
    ):
        """Permite varias formas de cálculo mediante parámetros opcionales.

        Python no realiza sobrecarga tradicional por firma; los argumentos
        opcionales permiten ofrecer variantes de uso de un mismo método.
        """
        try:
            # La búsqueda también queda dentro del try: un ID inexistente debe registrarse.
            servicio = self.buscar_servicio(servicio_id)
            total = servicio.calcular_costo(duracion, descuento, impuesto, cantidad, personas)
        except ErrorSoftwareFJ as error:
            self.logger.exception("Error al calcular costo del servicio %s: %s", servicio_id, error)
            raise
        else:
            # El registro de éxito solo se escribe si búsqueda y cálculo concluyen bien.
            self.logger.info("Costo calculado para servicio %s: %s", servicio_id, total)
            return total

    def resumen(self) -> dict[str, int]:
        """Devuelve el número de registros en las listas internas."""
        return {
            "clientes": len(self.clientes),
            "servicios": len(self.servicios),
            "reservas": len(self.reservas),
        }

    def cerrar(self) -> None:
        """Cierra los manejadores de log para liberar el archivo."""
        # Se copia la lista para poder retirar los manejadores mientras se itera.
        for manejador in list(self.logger.handlers):
            manejador.flush()
            manejador.close()
            self.logger.removeHandler(manejador)
