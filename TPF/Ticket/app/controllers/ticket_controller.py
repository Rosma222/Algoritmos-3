from flask import Blueprint, request, jsonify, session
from app.models import db
from app.models.ticket import Ticket
from app.models.hito import Hito
from app.models.product import Product
from app.models.user import User
from app.models.notification import Notification

ticket_bp = Blueprint('ticket_bp', __name__)

@ticket_bp.route('/api/tickets', methods=['GET'])
def list_tickets():
    user_id = session.get('user_id')
    role = session.get('role')

    if role == 'client':
        tickets = Ticket.query.filter_by(client_id=user_id).all()
    elif role == 'representative':
        tickets = Ticket.query.filter_by(representative_id=user_id).all()
    else: # admin or general view
        tickets = Ticket.query.all()

    return jsonify([t.to_dict() for t in tickets]), 200

@ticket_bp.route('/api/tickets', methods=['POST'])
def create_ticket():
    data = request.get_json() or {}
    client_id = data.get('client_id') or session.get('user_id')
    product_id = data.get('product_id')
    asunto = data.get('asunto')
    mensaje_inicial = data.get('mensaje_inicial', 'Ticket creado.')

    if not client_id or not product_id or not asunto:
        return jsonify({'error': 'Cliente, producto y asunto son obligatorios'}), 400

    product = Product.query.get_or_404(product_id)
    rubro_id = product.rubro_id

    # Asignar automáticamente un representante que esté especializado en ese rubro si existe
    representative = User.query.filter_by(role='representative', rubro_id=rubro_id).first()
    representative_id = representative.id if representative else None

    ticket = Ticket(
        client_id=client_id,
        representative_id=representative_id,
        product_id=product_id,
        rubro_id=rubro_id,
        asunto=asunto,
        estado='Abierto'
    )
    db.session.add(ticket)
    db.session.flush() # para obtener ticket.id

    # Crear primer hito
    hito = Hito(
        ticket_id=ticket.id,
        user_id=client_id,
        mensaje=mensaje_inicial
    )
    db.session.add(hito)

    # Notificar al representante si fue asignado
    if representative_id:
        notif = Notification(
            user_id=representative_id,
            mensaje=f"Nuevo ticket asignado #{ticket.id}: {asunto}"
        )
        db.session.add(notif)

    db.session.commit()
    return jsonify({'message': 'Ticket creado con éxito', 'ticket': ticket.to_dict()}), 201

@ticket_bp.route('/api/tickets/<int:ticket_id>/hitos', methods=['POST'])
def add_hito(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json() or {}
    user_id = data.get('user_id') or session.get('user_id')
    mensaje = data.get('mensaje')

    if not user_id or not mensaje:
        return jsonify({'error': 'Usuario y mensaje son obligatorios'}), 400

    hito = Hito(
        ticket_id=ticket.id,
        user_id=user_id,
        mensaje=mensaje
    )
    db.session.add(hito)

    # Notificar a la contraparte
    user = User.query.get(user_id)
    target_user_id = ticket.representative_id if user.role == 'client' else ticket.client_id
    if target_user_id:
        notif = Notification(
            user_id=target_user_id,
            mensaje=f"Nueva actualización en ticket #{ticket.id} por {user.username}"
        )
        db.session.add(notif)

    db.session.commit()
    return jsonify({'message': 'Hito agregado con éxito', 'hito': hito.to_dict()}), 201

@ticket_bp.route('/api/tickets/<int:ticket_id>/estado', methods=['PUT'])
def update_ticket_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json() or {}
    nuevo_estado = data.get('estado')

    estados_validos = ['Abierto', 'En Progreso', 'Resuelto', 'Cerrado']
    if nuevo_estado not in estados_validos:
        return jsonify({'error': f'Estado inválido. Debe ser uno de: {estados_validos}'}), 400

    ticket.estado = nuevo_estado
    
    # Notificar al cliente y representante
    for uid in [ticket.client_id, ticket.representative_id]:
        if uid:
            notif = Notification(
                user_id=uid,
                mensaje=f"El ticket #{ticket.id} cambió su estado a: {nuevo_estado}"
            )
            db.session.add(notif)

    db.session.commit()
    return jsonify({'message': 'Estado actualizado', 'ticket': ticket.to_dict()}), 200

@ticket_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No autenticado'}), 401
    notifications = Notification.query.filter_by(user_id=user_id, leida=False).all()
    return jsonify([n.to_dict() for n in notifications]), 200

@ticket_bp.route('/api/notifications/<int:notif_id>/leer', methods=['PUT'])
def mark_notification_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    notif.leida = True
    db.session.commit()
    return jsonify({'message': 'Notificación marcada como leída'}), 200
