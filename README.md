# Sistema Integral de Gestión de Clientes, Servicios y Reservas – Software FJ

Proyecto académico de la Fase 4 del curso Programación (213023), UNAD.

## Repositorio
https://github.com/pedronell998-boop/SoftwareFJ_Gestion_Clientes_Servicios_Reservas

## Alcance
Aplicación de consola orientada a objetos para administrar clientes, tres tipos de servicios y reservas. No utiliza bases de datos. Los datos se mantienen en listas durante la ejecución y el archivo `logs/software_fj.log` registra eventos y errores.

## Requisitos
- Python 3.10 o superior.
- No requiere paquetes externos; utiliza la biblioteca estándar.

## Estructura
- `main.py`: menú interactivo y captura de errores de entrada.
- `demo.py`: demostración de 14 operaciones válidas e inválidas.
- `software_fj/excepciones.py`: excepciones personalizadas del dominio.
- `software_fj/modelos.py`: clases, validaciones, abstracción, herencia y polimorfismo.
- `software_fj/sistema.py`: coordinación de operaciones, reglas de reserva y registro de logs.
- `tests/test_sistema.py`: 12 pruebas automatizadas con `unittest`.
- `logs/`: archivo de eventos y errores generado durante la ejecución.

## Ejecución
Desde la carpeta raíz del proyecto:

```bash
python main.py
python main.py --demo
python -m unittest discover -s tests -v
```

## Manejo de excepciones y comentarios
El código incluye docstrings para describir clases y métodos, comentarios en los bloques de validación y explicaciones de las cláusulas `try`, `except`, `else` y `finally`. Los errores controlados se registran en `logs/software_fj.log`; el encadenamiento conserva la excepción original mediante `raise ... from error`.

## Trabajo en GitHub
El historial del repositorio debe reflejar únicamente los aportes efectivamente realizados por cada integrante. Si la actividad se desarrolla con cinco participantes, se deben gestionar sus accesos y registrar las contribuciones reales mediante commits, ramas y revisiones, de acuerdo con las instrucciones del tutor.
