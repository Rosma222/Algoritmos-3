# Ticketing System - Agent Instructions

## Stack Tecnológico
- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Marshmallow, SQLite.
- **Frontend**: HTML5 semántico, CSS3 moderno (Flexbox/Grid), JavaScript ES6+ puro (sin frameworks ni dependencias de npm).
- **Arquitectura**: MVC (Model-View-Controller).

## Comandos de Desarrollo
- **Crear entorno virtual**: `python -m venv venv`
- **Activar entorno virtual (PowerShell)**: `.\venv\Scripts\Activate.ps1`
- **Instalar dependencias**: `pip install -r requirements.txt`
- **Ejecutar pruebas (TDD)**: `pytest`
- **Ejecutar aplicación**: `python run.py`

## Normas y Convenciones
- **TDD**: Codificar utilizando desarrollo guiado por pruebas (`pytest`).
- **Seguridad**: Gestión de sesiones e inicio de sesión a través de `auth_controller.py`.
- **Validación de Usuarios**: No permitir duplicación de usuarios.
- **Fechas**: Almacenar y manipular fechas locales (`YYYY-MM-DD`) sin conversiones automáticas UTC para evitar desfases en ART (UTC-3).
- **Estructura Modular**: `app/models/`, `app/controllers/`, `app/templates/`, `app/static/`.
