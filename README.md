# Sistema Integral de Gestión de Clientes, Servicios y Reservas – Software FJ

Proyecto académico de la Fase 4 del curso Programación (213023), UNAD.

## Alcance
Aplicación de consola orientada a objetos para administrar clientes, tres tipos de servicios y reservas. No utiliza bases de datos. Los datos se mantienen en listas durante la ejecución y el archivo `logs/software_fj.log` registra eventos y errores.

## Requisitos
- Python 3.10 o superior.
- No requiere paquetes externos; utiliza la biblioteca estándar.

## Estructura
- `main.py`: menú interactivo.
- `demo.py`: demostración de 14 operaciones.
- `software_fj/excepciones.py`: excepciones personalizadas.
- `software_fj/modelos.py`: clases de dominio, abstracción, herencia y polimorfismo.
- `software_fj/sistema.py`: coordinación de operaciones y logs.
- `tests/test_sistema.py`: 12 pruebas automatizadas.
- `logs/`: archivo de eventos y errores generado al ejecutar.

## Ejecución
Desde esta carpeta:
```bash
python main.py
python main.py --demo
python -m unittest discover -s tests -v
```

## GitHub
Crear o confirmar el repositorio del grupo, agregar a los cinco integrantes y subir la carpeta completa. La URL real debe copiarse en el informe y en la participación del foro. No se incluye una dirección ficticia.
