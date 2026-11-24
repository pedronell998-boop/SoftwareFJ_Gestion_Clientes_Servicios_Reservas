"""Modelo orientado a objetos del sistema integral de Software FJ."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from typing import Optional

from .excepciones import (
    DatosInvalidosError,
    EstadoReservaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
)

# Cuantización monetaria: todos los totales se expresan con dos decimales.
CENTAVO = Decimal("0.01")


def convertir_decimal(valor: object, campo: str) -> Decimal:
    """Convierte un valor a Decimal y conserva la causa si la conversión falla."""
    # Decimal evita los pequeños errores binarios propios de los números float.
    try:
        resultado = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise DatosInvalidosError(f"El campo '{campo}' debe ser numérico.") from error
    if not resultado.is_finite():
        raise DatosInvalidosError(f"El campo '{campo}' debe ser un número finito.")
    return resultado


def validar_duracion(duracion: object) -> Decimal:
    """Valida que la duración de una reserva sea un número positivo."""
    valor = convertir_decimal(duracion, "duración")
    if valor <= 0:
        raise DatosInvalidosError("La duración debe ser mayor que cero.")
    return valor


def validar_porcentaje(valor: object, campo: str) -> Decimal:
    """Valida porcentajes expresados como fracción entre 0 y 1."""
    porcentaje = convertir_decimal(valor, campo)
    if porcentaje < 0 or porcentaje > 1:
        raise DatosInvalidosError(f"'{campo}' debe estar entre 0 y 1.")
    return porcentaje


def validar_entero_positivo(valor: object, campo: str) -> int:
    """Valida cantidades enteras positivas, sin aceptar valores booleanos."""
    if isinstance(valor, bool):
        raise DatosInvalidosError(f"'{campo}' debe ser un entero positivo.")
    try:
        numero = int(valor)
    except (TypeError, ValueError) as error:
        raise DatosInvalidosError(f"'{campo}' debe ser un entero positivo.") from error
    # La comparación textual evita aceptar decimales o cadenas ambiguas como "2.5".
    if str(numero) != str(valor).strip() or numero <= 0:
        raise DatosInvalidosError(f"'{campo}' debe ser un entero positivo.")
    return numero


class Entidad(ABC):
    # Las entidades comparten un identificador y un contrato de descripción.
    """Abstracción común para las entidades identificables del sistema."""

    def __init__(self, identificador: str) -> None:
        if not isinstance(identificador, str) or not identificador.strip():
            raise DatosInvalidosError("El identificador no puede estar vacío.")
        self._identificador = identificador.strip()

    @property
    def identificador(self) -> str:
        """Devuelve el identificador de la entidad sin permitir su edición directa."""
        return self._identificador

    @abstractmethod
    def describir(self) -> str:
        """Entrega una descripción legible de la entidad."""
        raise NotImplementedError


class Cliente(Entidad):
    # Los atributos con doble guion bajo aplican encapsulación por nombre.
    """Cliente con datos personales encapsulados y validados."""

    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(identificador)
        self.__nombre = self._validar_nombre(nombre)
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_telefono(telefono)

    @staticmethod
    def _validar_nombre(nombre: str) -> str:
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise DatosInvalidosError("El nombre debe contener al menos tres caracteres.")
        return nombre.strip()

    @staticmethod
    def _validar_correo(correo: str) -> str:
        patron = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not isinstance(correo, str) or not re.match(patron, correo.strip()):
            raise DatosInvalidosError("El correo electrónico no tiene un formato válido.")
        return correo.strip().lower()

    @staticmethod
    def _validar_telefono(telefono: str) -> str:
        if not isinstance(telefono, str):
            raise DatosInvalidosError("El teléfono debe registrarse como texto.")
        digitos = re.sub(r"[\s()+-]", "", telefono)
        if not digitos.isdigit() or not 7 <= len(digitos) <= 15:
            raise DatosInvalidosError("El teléfono debe contener entre 7 y 15 dígitos.")
        return telefono.strip()

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return self.__telefono

    def describir(self) -> str:
        return f"Cliente {self.identificador}: {self.nombre} | {self.correo} | {self.telefono}"


class Servicio(Entidad, ABC):
    # Las clases concretas heredan esta información y redefinen las reglas propias.
    """Clase abstracta que define la interfaz común de los servicios."""

    def __init__(self, identificador: str, nombre: str, tarifa_base: object) -> None:
        super().__init__(identificador)
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidosError("El nombre del servicio es obligatorio.")
        tarifa = convertir_decimal(tarifa_base, "tarifa base")
        if tarifa <= 0:
            raise DatosInvalidosError("La tarifa base debe ser mayor que cero.")
        self._nombre = nombre.strip()
        self._tarifa_base = tarifa.quantize(CENTAVO, rounding=ROUND_HALF_UP)
        self._activo = True

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> Decimal:
        return self._tarifa_base

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self) -> None:
        self._activo = False

    def activar(self) -> None:
        self._activo = True

    def _calcular_total(
        self,
        duracion: object = 1,
        descuento: object = 0,
        impuesto: object = Decimal("0.19"),
        cantidad: object = 1,
    ) -> Decimal:
        """Calcula el valor con duración, cantidad, descuento e impuesto."""
        horas = validar_duracion(duracion)
        unidades = validar_entero_positivo(cantidad, "cantidad")
        rebaja = validar_porcentaje(descuento, "descuento")
        tributo = validar_porcentaje(impuesto, "impuesto")
        # Fórmula: tarifa × horas × unidades; luego se aplica descuento e impuesto.
        subtotal = self._tarifa_base * horas * unidades
        total = subtotal * (Decimal("1") - rebaja) * (Decimal("1") + tributo)
        return total.quantize(CENTAVO, rounding=ROUND_HALF_UP)

    @abstractmethod
    def validar_parametros(
        self, duracion: object, cantidad: object = 1, personas: Optional[object] = None
    ) -> None:
        """Aplica las reglas particulares del servicio."""
        raise NotImplementedError

    @abstractmethod
    def calcular_costo(
        self,
        duracion: object = 1,
        descuento: object = 0,
        impuesto: object = Decimal("0.19"),
        cantidad: object = 1,
        personas: Optional[object] = None,
    ) -> Decimal:
        """Calcula el costo según el tipo de servicio."""
        raise NotImplementedError

    @abstractmethod
    def describir(self) -> str:
        raise NotImplementedError


class ReservaSala(Servicio):
    # Una sala se reserva individualmente y no puede superar su capacidad.
    """Servicio de reserva de salas con límite de capacidad."""

    def __init__(
        self, identificador: str, nombre: str, tarifa_base: object, capacidad_maxima: object
    ) -> None:
        super().__init__(identificador, nombre, tarifa_base)
        self.capacidad_maxima = validar_entero_positivo(capacidad_maxima, "capacidad máxima")

    def validar_parametros(
        self, duracion: object, cantidad: object = 1, personas: Optional[object] = None
    ) -> None:
        validar_duracion(duracion)
        if validar_entero_positivo(cantidad, "cantidad") != 1:
            raise DatosInvalidosError("La reserva de sala se realiza por una sala a la vez.")
        asistentes = validar_entero_positivo(personas if personas is not None else 1, "personas")
        if asistentes > self.capacidad_maxima:
            raise DatosInvalidosError(
                f"La sala admite máximo {self.capacidad_maxima} personas; se recibieron {asistentes}."
            )

    def calcular_costo(
        self, duracion: object = 1, descuento: object = 0,
        impuesto: object = Decimal("0.19"), cantidad: object = 1,
        personas: Optional[object] = None,
    ) -> Decimal:
        self.validar_parametros(duracion, cantidad, personas)
        return self._calcular_total(duracion, descuento, impuesto, cantidad)

    def describir(self) -> str:
        return (
            f"Sala {self.nombre} | Tarifa/hora: ${self.tarifa_base} | "
            f"Capacidad: {self.capacidad_maxima} personas | Estado: {'activa' if self.activo else 'inactiva'}"
        )


class AlquilerEquipo(Servicio):
    # El alquiler puede incluir varias unidades, siempre dentro del inventario.
    """Servicio de alquiler de equipos con inventario disponible."""

    def __init__(
        self, identificador: str, nombre: str, tarifa_base: object, unidades_disponibles: object
    ) -> None:
        super().__init__(identificador, nombre, tarifa_base)
        self.unidades_disponibles = validar_entero_positivo(
            unidades_disponibles, "unidades disponibles"
        )

    def validar_parametros(
        self, duracion: object, cantidad: object = 1, personas: Optional[object] = None
    ) -> None:
        validar_duracion(duracion)
        unidades = validar_entero_positivo(cantidad, "cantidad")
        if unidades > self.unidades_disponibles:
            raise DatosInvalidosError(
                f"Solo hay {self.unidades_disponibles} unidades disponibles; se solicitaron {unidades}."
            )

    def calcular_costo(
        self, duracion: object = 1, descuento: object = 0,
        impuesto: object = Decimal("0.19"), cantidad: object = 1,
        personas: Optional[object] = None,
    ) -> Decimal:
        self.validar_parametros(duracion, cantidad, personas)
        return self._calcular_total(duracion, descuento, impuesto, cantidad)

    def describir(self) -> str:
        return (
            f"Equipo {self.nombre} | Tarifa/unidad/hora: ${self.tarifa_base} | "
            f"Unidades: {self.unidades_disponibles} | Estado: {'activo' if self.activo else 'inactivo'}"
        )


class AsesoriaEspecializada(Servicio):
    # Una asesoría se agenda por sesión y tiene un máximo de ocho horas.
    """Servicio de asesoría profesional por horas."""

    def __init__(
        self, identificador: str, nombre: str, tarifa_base: object, especialidad: str
    ) -> None:
        super().__init__(identificador, nombre, tarifa_base)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise DatosInvalidosError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()

    def validar_parametros(
        self, duracion: object, cantidad: object = 1, personas: Optional[object] = None
    ) -> None:
        horas = validar_duracion(duracion)
        if horas > Decimal("8"):
            raise DatosInvalidosError("Una asesoría no puede superar ocho horas por reserva.")
        if validar_entero_positivo(cantidad, "cantidad") != 1:
            raise DatosInvalidosError("La asesoría se agenda por una sesión a la vez.")

    def calcular_costo(
        self, duracion: object = 1, descuento: object = 0,
        impuesto: object = Decimal("0.19"), cantidad: object = 1,
        personas: Optional[object] = None,
    ) -> Decimal:
        self.validar_parametros(duracion, cantidad, personas)
        return self._calcular_total(duracion, descuento, impuesto, cantidad)

    def describir(self) -> str:
        return (
            f"Asesoría {self.nombre} | Especialidad: {self.especialidad} | "
            f"Tarifa/hora: ${self.tarifa_base} | Estado: {'activa' if self.activo else 'inactiva'}"
        )


class EstadoReserva(Enum):
    # Enum restringe los estados a los valores definidos para el ciclo de reserva.
    """Estados permitidos para el ciclo de vida de una reserva."""

    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"


class Reserva(Entidad):
    # La reserva relaciona objetos del dominio y calcula su costo al construirse.
    """Reserva que relaciona un cliente con un servicio y un periodo."""

    def __init__(
        self,
        identificador: str,
        cliente: Cliente,
        servicio: Servicio,
        fecha_inicio: datetime,
        duracion: object,
        cantidad: object = 1,
        personas: Optional[object] = None,
        descuento: object = 0,
        impuesto: object = Decimal("0.19"),
    ) -> None:
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("La reserva requiere un objeto Servicio válido.")
        if not isinstance(fecha_inicio, datetime):
            raise DatosInvalidosError("La fecha de inicio debe ser un objeto datetime válido.")
        self._duracion = validar_duracion(duracion)
        self._cantidad = validar_entero_positivo(cantidad, "cantidad")
        self._personas = personas
        # La validación polimórfica aplica la regla correspondiente al servicio recibido.
        servicio.validar_parametros(self._duracion, self._cantidad, self._personas)
        if not servicio.activo:
            raise ServicioNoDisponibleError("No se puede reservar un servicio inactivo.")
        self.cliente = cliente
        self.servicio = servicio
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_inicio + timedelta(hours=float(self._duracion))
        self.estado = EstadoReserva.PENDIENTE
        # El mismo método se resuelve según la clase concreta del servicio.
        self.total = servicio.calcular_costo(
            self._duracion, descuento, impuesto, self._cantidad, self._personas
        )

    @property
    def duracion(self) -> Decimal:
        return self._duracion

    @property
    def cantidad(self) -> int:
        """Cantidad de unidades asociadas a la reserva."""
        return self._cantidad

    def confirmar(self) -> None:
        """Confirma una reserva que todavía está pendiente."""
        if self.estado is not EstadoReserva.PENDIENTE:
            raise EstadoReservaError("Solo se pueden confirmar reservas pendientes.")
        if not self.servicio.activo:
            raise ServicioNoDisponibleError("El servicio fue desactivado y no puede confirmarse.")
        self.estado = EstadoReserva.CONFIRMADA

    def cancelar(self) -> None:
        """Cancela una reserva pendiente o confirmada."""
        if self.estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
            raise EstadoReservaError("La reserva ya fue cancelada y no admite otra cancelación.")
        self.estado = EstadoReserva.CANCELADA

    def procesar(self) -> None:
        """Procesa la confirmación y encadena los errores de dominio."""
        # Se conserva el error original como causa de la excepción de nivel superior.
        try:
            self.confirmar()
        except (EstadoReservaError, ServicioNoDisponibleError) as error:
            raise ReservaInvalidaError(
                f"No fue posible procesar la reserva {self.identificador}."
            ) from error

    def describir(self) -> str:
        return (
            f"Reserva {self.identificador} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Inicio: {self.fecha_inicio:%Y-%m-%d %H:%M} | "
            f"Duración: {self.duracion} h | Total: ${self.total} | Estado: {self.estado.value}"
        )
