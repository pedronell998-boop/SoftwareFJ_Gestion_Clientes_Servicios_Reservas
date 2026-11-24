"""Excepciones de dominio utilizadas por el Sistema Software FJ."""


class ErrorSoftwareFJ(Exception):
    """Clase base para los errores controlados de la aplicación."""


class DatosInvalidosError(ErrorSoftwareFJ):
    """Se produce cuando un dato no cumple las reglas de validación."""


class EntidadDuplicadaError(ErrorSoftwareFJ):
    """Se produce cuando se intenta registrar un identificador repetido."""


class ClienteNoEncontradoError(ErrorSoftwareFJ):
    """Se produce cuando el cliente solicitado no está registrado."""


class ServicioNoEncontradoError(ErrorSoftwareFJ):
    """Se produce cuando el servicio solicitado no está registrado."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se produce cuando un servicio está inactivo o tiene cruce horario."""


class ReservaNoEncontradaError(ErrorSoftwareFJ):
    """Se produce cuando la reserva solicitada no existe."""


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Se produce cuando una reserva no puede procesarse correctamente."""


class EstadoReservaError(ErrorSoftwareFJ):
    """Se produce cuando una operación no corresponde al estado de reserva."""
