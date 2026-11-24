"""Pruebas automatizadas de validación y manejo de excepciones."""

import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from software_fj import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    ReservaSala,
    SistemaGestion,
)
from software_fj.excepciones import (
    ClienteNoEncontradoError,
    DatosInvalidosError,
    EntidadDuplicadaError,
    ServicioNoDisponibleError,
)


class PruebasSistemaSoftwareFJ(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.sistema = SistemaGestion(Path(self.temp.name))
        self.cliente = Cliente("C-01", "Ana Torres", "ana@example.com", "3001234567")
        self.sistema.registrar_cliente(self.cliente)
        self.sala = ReservaSala("S-01", "Sala Norte", 50000, 10)
        self.equipo = AlquilerEquipo("S-02", "Proyector", 20000, 3)
        self.asesoria = AsesoriaEspecializada("S-03", "Asesoría", 100000, "Software")
        self.sistema.registrar_servicio(self.sala)
        self.sistema.registrar_servicio(self.equipo)
        self.sistema.registrar_servicio(self.asesoria)

    def tearDown(self):
        self.sistema.cerrar()
        self.temp.cleanup()

    def test_01_registro_cliente_valido(self):
        self.assertEqual(self.sistema.buscar_cliente("C-01").nombre, "Ana Torres")

    def test_02_cliente_correo_invalido(self):
        with self.assertRaises(DatosInvalidosError):
            Cliente("C-02", "Luis Pérez", "correo", "3001234567")

    def test_03_cliente_duplicado(self):
        with self.assertRaises(EntidadDuplicadaError):
            self.sistema.registrar_cliente(
                Cliente("C-01", "Otra Persona", "otra@example.com", "3007654321")
            )

    def test_04_creacion_tres_tipos_servicio(self):
        self.assertEqual(len(self.sistema.servicios), 3)
        self.assertTrue(all(isinstance(s, (ReservaSala, AlquilerEquipo, AsesoriaEspecializada))
                            for s in self.sistema.servicios))

    def test_05_servicio_tarifa_invalida(self):
        with self.assertRaises(DatosInvalidosError):
            ReservaSala("S-04", "Sala sin tarifa", 0, 10)

    def test_06_reserva_exitosa(self):
        reserva = self.sistema.crear_reserva(
            "R-01", "C-01", "S-01", datetime(2026, 11, 10, 9), 2, personas=5
        )
        self.assertEqual(reserva.estado.value, "Confirmada")

    def test_07_reserva_cliente_inexistente(self):
        with self.assertRaises(ClienteNoEncontradoError):
            self.sistema.crear_reserva(
                "R-02", "C-99", "S-01", datetime(2026, 11, 10, 9), 1, personas=2
            )

    def test_08_reserva_servicio_inactivo(self):
        self.equipo.desactivar()
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.crear_reserva(
                "R-03", "C-01", "S-02", datetime(2026, 11, 10, 9), 1
            )

    def test_09_cruce_horario(self):
        self.sistema.crear_reserva(
            "R-04", "C-01", "S-01", datetime(2026, 11, 10, 9), 2, personas=4
        )
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.crear_reserva(
                "R-05", "C-01", "S-01", datetime(2026, 11, 10, 10), 1, personas=3
            )

    def test_10_calculo_con_descuento_e_impuesto(self):
        total = self.sistema.calcular_costo("S-03", 2, Decimal("0.10"), Decimal("0.19"))
        self.assertEqual(total, Decimal("214200.00"))

    def test_11_cancelacion_reserva(self):
        reserva = self.sistema.crear_reserva(
            "R-06", "C-01", "S-01", datetime(2026, 11, 11, 9), 1, personas=2
        )
        self.sistema.cancelar_reserva("R-06")
        self.assertEqual(reserva.estado.value, "Cancelada")

    def test_12_encadenamiento_error_fecha(self):
        with self.assertRaises(DatosInvalidosError) as contexto:
            self.sistema.convertir_fecha("fecha-invalida")
        self.assertIsInstance(contexto.exception.__cause__, ValueError)


if __name__ == "__main__":
    unittest.main(verbosity=2)
