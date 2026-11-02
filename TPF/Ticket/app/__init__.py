from flask import Flask, render_template
from app.models import db
from app.models.rubro import Rubro
from app.models.user import User
from app.models.product import Product
from app.models.ticket import Ticket
from app.models.hito import Hito
from app.controllers.auth_controller import auth_bp
from app.controllers.product_controller import product_bp
from app.controllers.ticket_controller import ticket_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-ticketing'
    
    if test_config:
        app.config.update(test_config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticketing.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Registrar Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(ticket_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    with app.app_context():
        db.create_all()
        _seed_initial_data()

    return app

def _seed_initial_data():
    # 1. Rubros requeridos
    rubros_data = [
        ("Línea Blanca", "Heladeras, freezers, lavarropas, secarropas, cocinas, hornos y lavavajillas."),
        ("Climatización", "Aires acondicionados, estufas, calefactores, ventiladores y purificadores."),
        ("Tecno", "Smart TVs, notebooks, tablets, smartphones, consolas de videojuegos, audio y smartwatches."),
        ("Pequeños Electrodomésticos", "Licuadoras, cafeteras, tostadoras, microondas, planchas, aspiradoras y cuidado personal.")
    ]

    for nombre, desc in rubros_data:
        if not Rubro.query.filter_by(nombre=nombre).first():
            db.session.add(Rubro(nombre=nombre, descripcion=desc))
    db.session.commit()

    lb = Rubro.query.filter_by(nombre='Línea Blanca').first()
    clim = Rubro.query.filter_by(nombre='Climatización').first()
    tec = Rubro.query.filter_by(nombre='Tecno').first()
    peq = Rubro.query.filter_by(nombre='Pequeños Electrodomésticos').first()

    # 2. Usuario Admin por defecto
    if not User.query.filter_by(email='admin@ticketing.com').first():
        admin = User(username='admin', email='admin@ticketing.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    # 3. Clientes (password: 123)
    clients_data = [
        ("Juan Pérez", "juan.perez@cliente.com"),
        ("María Gómez", "maria.gomez@cliente.com")
    ]
    for username, email in clients_data:
        if not User.query.filter_by(email=email).first():
            u = User(username=username, email=email, role='client')
            u.set_password('123')
            db.session.add(u)

    # 4. Técnicos / Representantes (6 repartidos en rubros, password: 123)
    reps_data = [
        ("Carlos Línea Blanca", "carlos.lb@ticketing.com", lb.id),
        ("Mariana Línea Blanca", "mariana.lb@ticketing.com", lb.id),
        ("Jorge Clima", "jorge.clima@ticketing.com", clim.id),
        ("Sofía Tecno", "sofia.tecno@ticketing.com", tec.id),
        ("Lucía Tecno", "lucia.tecno@ticketing.com", tec.id),
        ("Pedro Pequeños", "pedro.peque@ticketing.com", peq.id)
    ]
    for username, email, rubro_id in reps_data:
        if not User.query.filter_by(email=email).first():
            u = User(username=username, email=email, role='representative', rubro_id=rubro_id)
            u.set_password('123')
            db.session.add(u)

    db.session.commit()

    # 5. Electrodomésticos (Al menos 3 por rubro = 12 productos)
    products_data = [
        # Línea Blanca
        ("Heladera No Frost", "Samsung", "RT38", "SN-LB-001", "LB-HEL-01", lb.id),
        ("Lavarropas Automático", "Whirlpool", "WNQ60", "SN-LB-002", "LB-LAV-02", lb.id),
        ("Cocina a Gas", "Domec", "C-400", "SN-LB-003", "LB-COC-03", lb.id),
        # Climatización
        ("Aire Acondicionado Split", "LG", "DualInverter", "SN-CL-001", "CL-AIR-01", clim.id),
        ("Estufa a Gas", "Longvie", "E-200", "SN-CL-002", "CL-EST-02", clim.id),
        ("Ventilador de Pie", "Peabody", "V-P18", "SN-CL-003", "CL-VEN-03", clim.id),
        # Tecno
        ("Smart TV 50", "Sony", "Bravia X", "SN-TE-001", "TE-TV-01", tec.id),
        ("Notebook Gamer", "Lenovo", "Legion 5", "SN-TE-002", "TE-NOT-02", tec.id),
        ("Smartphone", "Motorola", "Edge 40", "SN-TE-003", "TE-CEL-03", tec.id),
        # Pequeños Electrodomésticos
        ("Cafetera Express", "Philips", "CafeGourmet", "SN-PE-001", "PE-CAF-01", peq.id),
        ("Microondas Digital", "Atma", "M-20L", "SN-PE-002", "PE-MIC-02", peq.id),
        ("Aspiradora Robot", "Xiaomi", "RobotV1", "SN-PE-003", "PE-ASP-03", peq.id),
    ]

    for nombre, marca, modelo, nro_serie, codigo_interno, rubro_id in products_data:
        if not Product.query.filter_by(codigo_interno=codigo_interno).first():
            p = Product(
                nombre=nombre,
                marca=marca,
                modelo=modelo,
                nro_serie=nro_serie,
                codigo_interno=codigo_interno,
                rubro_id=rubro_id
            )
            db.session.add(p)

    db.session.commit()

    # 6. Tickets de ejemplo con hitos iniciales
    juan = User.query.filter_by(email='juan.perez@cliente.com').first()
    maria = User.query.filter_by(email='maria.gomez@cliente.com').first()
    carlos = User.query.filter_by(email='carlos.lb@ticketing.com').first()
    sofia = User.query.filter_by(email='sofia.tecno@ticketing.com').first()

    heladera = Product.query.filter_by(codigo_interno='LB-HEL-01').first()
    tv = Product.query.filter_by(codigo_interno='TE-TV-01').first()

    if juan and heladera and not Ticket.query.filter_by(asunto='La heladera no enfría en el compartimiento superior.').first():
        t1 = Ticket(
            client_id=juan.id,
            representative_id=carlos.id if carlos else None,
            product_id=heladera.id,
            rubro_id=lb.id,
            asunto='La heladera no enfría en el compartimiento superior.',
            estado='Abierto'
        )
        db.session.add(t1)
        db.session.flush()
        h1 = Hito(
            ticket_id=t1.id,
            user_id=juan.id,
            mensaje='Hola, desde ayer la parte de arriba de la heladera perdió frío. Necesito asistencia técnica.'
        )
        db.session.add(h1)

    if maria and tv and not Ticket.query.filter_by(asunto='Rayas verticales en la pantalla.').first():
        t2 = Ticket(
            client_id=maria.id,
            representative_id=sofia.id if sofia else None,
            product_id=tv.id,
            rubro_id=tec.id,
            asunto='Rayas verticales en la pantalla.',
            estado='En Progreso'
        )
        db.session.add(t2)
        db.session.flush()
        h2 = Hito(
            ticket_id=t2.id,
            user_id=maria.id,
            mensaje='Al encender la tele aparecen rayas de colores en el lateral izquierdo.'
        )
        db.session.add(h2)

    db.session.commit()
