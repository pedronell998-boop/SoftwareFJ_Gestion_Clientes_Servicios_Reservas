"""Punto de entrada del Sistema Integral de Gestión Software FJ."""

import sys
from datetime import datetime

from demo import ejecutar_demostracion
from software_fj import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    ReservaSala,
    SistemaGestion,
)
from software_fj.excepciones import ErrorSoftwareFJ


def menu_interactivo() -> None:
    """Presenta un menú de consola para operar el sistema."""
    sistema = SistemaGestion()
    print("\nSISTEMA INTEGRAL DE GESTIÓN | SOFTWARE FJ")
    try:
        while True:
            print("\n1. Registrar cliente")
            print("2. Registrar servicio")
            print("3. Crear reserva")
            print("4. Cancelar reserva")
            print("5. Consultar clientes, servicios y reservas")
            print("6. Calcular costo de un servicio")
            print("0. Salir")
            opcion = input("Seleccione una opción: ").strip()

            try:
                if opcion == "1":
                    cliente = Cliente(
                        input("ID del cliente: "), input("Nombre: "),
                        input("Correo: "), input("Teléfono: ")
                    )
                    sistema.registrar_cliente(cliente)
                    print("Cliente registrado correctamente.")

                elif opcion == "2":
                    tipo = input("Tipo (1 sala, 2 equipo, 3 asesoría): ").strip()
                    identificador = input("ID del servicio: ")
                    nombre = input("Nombre del servicio: ")
                    tarifa = input("Tarifa base: ")
                    if tipo == "1":
                        servicio = ReservaSala(
                            identificador, nombre, tarifa, input("Capacidad máxima: ")
                        )
                    elif tipo == "2":
                        servicio = AlquilerEquipo(
                            identificador, nombre, tarifa, input("Unidades disponibles: ")
                        )
                    elif tipo == "3":
                        servicio = AsesoriaEspecializada(
                            identificador, nombre, tarifa, input("Especialidad: ")
                        )
                    else:
                        raise ValueError("Tipo de servicio no reconocido.")
                    sistema.registrar_servicio(servicio)
                    print("Servicio registrado correctamente.")

                elif opcion == "3":
                    fecha = datetime.fromisoformat(input("Fecha y hora (AAAA-MM-DD HH:MM): "))
                    reserva = sistema.crear_reserva(
                        input("ID de reserva: "), input("ID de cliente: "),
                        input("ID de servicio: "), fecha, input("Duración en horas: "),
                        input("Cantidad de unidades (1 si no aplica): "),
                        input("Personas (1 si no aplica): ")
                    )
                    print(reserva.describir())

                elif opcion == "4":
                    reserva = sistema.cancelar_reserva(input("ID de reserva: "))
                    print(reserva.describir())

                elif opcion == "5":
                    print("\nCLIENTES")
                    for elemento in sistema.clientes:
                        print("-", elemento.describir())
                    print("\nSERVICIOS")
                    for elemento in sistema.servicios:
                        print("-", elemento.describir())
                    print("\nRESERVAS")
                    for elemento in sistema.reservas:
                        print("-", elemento.describir())
                    print("\nRESUMEN:", sistema.resumen())

                elif opcion == "6":
                    total = sistema.calcular_costo(
                        input("ID del servicio: "),
                        input("Duración en horas: "),
                        input("Descuento (ej. 0.10 para 10 %): "),
                        input("Impuesto (ej. 0.19 para 19 %): "),
                        input("Cantidad de unidades: "),
                    )
                    print(f"Costo total: ${total}")

                elif opcion == "0":
                    print("Sesión finalizada.")
                    break
                else:
                    print("Opción no válida. Intente nuevamente.")

            except (ErrorSoftwareFJ, ValueError) as error:
                print(f"Operación no completada: {type(error).__name__}: {error}")
                print("El sistema continúa activo; revise el archivo de logs.")
    finally:
        sistema.cerrar()


if __name__ == "__main__":
    if "--demo" in sys.argv:
        ejecutar_demostracion()
    else:
        menu_interactivo()
