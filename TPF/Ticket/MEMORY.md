# Estado del Proyecto (MEMORY.md)  

## Estado Actual  
- Versión: v1.1 funcional con seed data completo y arquitectura MVC.  
- Archivos Backend: `run.py`, `requirements.txt`, `app/__init__.py` (incluyendo sembrado completo de datos), `app/models/` (`rubro.py`, `user.py`, `product.py`, `ticket.py`, `hito.py`, `notification.py`), `app/controllers/` (`auth_controller.py`, `product_controller.py`, `ticket_controller.py`).  
- Archivos Frontend: `app/templates/index.html`, `app/static/css/styles.css`, `app/static/js/app.js`.  
- Tests: `tests/test_ticketing.py` (todos pasando correctamente con `pytest`).  

## Datos Sembrados (Seed Data)
- **Rubros**: 4 (Línea Blanca, Climatización, Tecno, Pequeños Electrodomésticos).
- **Técnicos (Representantes)**: 6 técnicos distribuidos en los rubros con contraseña `123`.
- **Clientes**: 2 usuarios registrados (`juan.perez@cliente.com`, `maria.gomez@cliente.com`) con contraseña `123`.
- **Productos**: 12 electrodomésticos (3 por cada rubro).
- **Tickets**: 2 tickets de ejemplo con hitos iniciales vinculados.

## Decisiones Tomadas  
- Las fechas se guardan como cadenas locales `'YYYY-MM-DD'` y `'YYYY-MM-DD HH:MM:SS'` en hora local para evitar desfases UTC (ART UTC-3).  
- Arquitectura estricta MVC sin dependencias de npm ni bundlers, utilizando JS puro y CSS3 nativo.  
- Se implementó validación estricta para prevenir la duplicación de usuarios y asociar representantes con rubros de especialización.  

## Errores Resueltos  
- Resolución de conflictos de unicidad en pruebas al sembrar datos iniciales de rubros por defecto en `create_app()`.  

## Pendiente  
- Ninguno. Prototipo completo, sembrado y verificado con TDD.  
