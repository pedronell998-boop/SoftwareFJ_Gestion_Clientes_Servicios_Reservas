"""Punto de entrada del Sistema Integral de Gestión Software FJ."""

import sys

from demo import ejecutar_demostracion
from software_fj import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    Cliente,
    ReservaSala,
    SistemaGestion,
)
from software_fj.excepciones import DatosInvalidosError, ErrorSoftwareFJ


def menu_interactivo() -> None:
    """Presenta el menú de consola y mantiene activa la sesión de trabajo."""
    sistema = SistemaGestion()
    print("\nSISTEMA INTEGRAL DE GESTIÓN | SOFTWARE FJ")

    try:
        while True:
            # Se muestran las operaciones disponibles en cada iteración.
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
                    # El constructor valida los datos antes de registrar el objeto.
                    cliente = Cliente(
                        input("ID del cliente: "),
                        input("Nombre: "),
                        input("Correo: "),
                        input("Teléfono: "),
                    )
                    sistema.registrar_cliente(cliente)
                    print("Cliente registrado correctamente.")

                elif opcion == "2":
                    # El tipo seleccionado determina qué clase concreta se instancia.
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
                        raise DatosInvalidosError("Tipo de servicio no reconocido.")

                    sistema.registrar_servicio(servicio)
                    print("Servicio registrado correctamente.")

                elif opcion == "3":
                    # La fecha se convierte mediante el método que encadena el error original.
                    fecha = sistema.convertir_fecha(
                        input("Fecha y hora (AAAA-MM-DD HH:MM): ")
                    )
                    reserva = sistema.crear_reserva(
                        input("ID de reserva: "),
                        input("ID de cliente: "),
                        input("ID de servicio: "),
                        fecha,
                        input("Duración en horas: "),
                        input("Cantidad de unidades (1 si no aplica): "),
                        input("Personas (1 si no aplica): "),
                    )
                    print(reserva.describir())

                elif opcion == "4":
                    reserva = sistema.cancelar_reserva(input("ID de reserva: "))
                    print(reserva.describir())

                elif opcion == "5":
                    # Se consultan las colecciones que el sistema conserva en memoria.
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
                    # Los parámetros opcionales permiten calcular variantes del costo.
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
                    # La opción inválida no detiene el ciclo del menú.
                    sistema.logger.warning("Se ingresó una opción de menú no válida: %s", opcion)
                    print("Opción no válida. Intente nuevamente.")

            except (ErrorSoftwareFJ, ValueError) as error:
                # exception() registra el mensaje y la traza para facilitar el diagnóstico.
                sistema.logger.exception("Operación interactiva no completada: %s", error)
                print(f"Operación no completada: {type(error).__name__}: {error}")
                print("El sistema continúa activo; revise el archivo de logs.")
    finally:
        # El bloque finally se ejecuta incluso si el usuario interrumpe la sesión.
        sistema.cerrar()


if __name__ == "__main__":
    # El argumento --demo ejecuta los casos de prueba demostrativos; sin él se abre el menú.
    if "--demo" in sys.argv:
        ejecutar_demostracion()
    else:
        menu_interactivo()
