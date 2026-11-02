import pytest
from app import create_app, db
from app.models.user import User
from app.models.rubro import Rubro
from app.models.product import Product
from app.models.ticket import Ticket
from app.models.hito import Hito

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_prevent_duplicate_users(app):
    with app.app_context():
        user1 = User(username='testuser', email='test@test.com', role='client')
        user1.set_password('password123')
        db.session.add(user1)
        db.session.commit()

        # Try to add user with same email or username
        user2 = User(username='testuser2', email='test@test.com', role='client')
        db.session.add(user2)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()

def test_rubro_and_representative_specialization(app):
    with app.app_context():
        rubro = Rubro.query.filter_by(nombre='Línea Blanca').first()

        rep = User(username='rep1', email='rep@test.com', role='representative', rubro_id=rubro.id)
        rep.set_password('123456')
        db.session.add(rep)
        db.session.commit()

        assert rep.rubro.nombre == 'Línea Blanca'

def test_product_registration(app):
    with app.app_context():
        rubro = Rubro.query.filter_by(nombre='Climatización').first()

        product = Product(
            nombre='Aire Split',
            marca='CoolTech',
            modelo='X200',
            nro_serie='SN123456',
            codigo_interno='CLIM-01',
            rubro_id=rubro.id
        )
        db.session.add(product)
        db.session.commit()

        assert product.codigo_interno == 'CLIM-01'
        assert product.rubro.nombre == 'Climatización'

def test_ticket_and_hitos(app):
    with app.app_context():
        rubro = Rubro.query.filter_by(nombre='Tecno').first()

        client_user = User(username='client1', email='client@test.com', role='client')
        client_user.set_password('pass')
        rep_user = User(username='rep1', email='rep@test.com', role='representative', rubro_id=rubro.id)
        rep_user.set_password('pass')
        db.session.add_all([client_user, rep_user])
        db.session.commit()

        product = Product(
            nombre='Smart TV 50',
            marca='Visio',
            modelo='V50',
            nro_serie='TV999',
            codigo_interno='TEC-01',
            rubro_id=rubro.id
        )
        db.session.add(product)
        db.session.commit()

        ticket = Ticket(
            client_id=client_user.id,
            representative_id=rep_user.id,
            product_id=product.id,
            rubro_id=rubro.id,
            asunto='No enciende la pantalla',
            estado='Abierto'
        )
        db.session.add(ticket)
        db.session.commit()

        hito = Hito(
            ticket_id=ticket.id,
            user_id=client_user.id,
            mensaje='Hola, la tele no prende desde ayer.'
        )
        db.session.add(hito)
        db.session.commit()

        assert len(ticket.hitos) == 1
        assert ticket.hitos[0].mensaje == 'Hola, la tele no prende desde ayer.'
