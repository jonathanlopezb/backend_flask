# Sistema de Gestión de Préstamos

Esta aplicación en Flask permite gestionar usuarios, clientes y préstamos, incluyendo la creación de préstamos, pagos de cuotas y visualización de historial de préstamos por cliente. También permite relacionar cobradores con clientes y consultar el historial de clientes asignados.

## Requisitos

- Python 3.7+
- Flask
- SQLAlchemy
- werkzeug

## Instalación

1. Clona este repositorio.
2. Crea un entorno virtual e instala las dependencias:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. Ejecuta la aplicación:

    ```bash
    flask run
    ```

4. La aplicación estará disponible en `http://127.0.0.1:5000`.

## Endpoints

    Registrar un Usuario
    Método: POST
    URL: http://127.0.0.1:5000/usuario
    Body (JSON): Ver sección Registrar Usuario

    Registrar un Cliente
    Método: POST
    URL: http://127.0.0.1:5000/cliente
    Body (JSON): Ver sección Registrar Cliente

    Registrar un Préstamo
    Método: POST
    URL: http://127.0.0.1:5000/prestamo
    Body (JSON): Ver sección Registrar Préstamo

    Pagar Cuota de un Préstamo
    Método: POST
    URL: http://127.0.0.1:5000/prestamo/1/pago

    Obtener Clientes de un Cobrador
    Método: GET
    URL: http://127.0.0.1:5000/cobrador/1/clientes

    Consultar Préstamos de un Cliente
    Método: GET
    URL: http://127.0.0.1:5000/cliente/1/prestamos
