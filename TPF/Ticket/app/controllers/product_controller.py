from flask import Blueprint, request, jsonify
from app.models import db
from app.models.rubro import Rubro
from app.models.product import Product
from app.models.user import User

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/api/rubros', methods=['GET'])
def list_rubros():
    rubros = Rubro.query.all()
    return jsonify([r.to_dict() for r in rubros]), 200

@product_bp.route('/api/rubros', methods=['POST'])
def create_rubro():
    data = request.get_json() or {}
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')

    if not nombre:
        return jsonify({'error': 'El nombre del rubro es obligatorio'}), 400

    existing = Rubro.query.filter_by(nombre=nombre).first()
    if existing:
        return jsonify({'error': 'El rubro ya existe'}), 400

    rubro = Rubro(nombre=nombre, descripcion=descripcion)
    db.session.add(rubro)
    db.session.commit()
    return jsonify({'message': 'Rubro creado', 'rubro': rubro.to_dict()}), 201

@product_bp.route('/api/products', methods=['GET'])
def list_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200

@product_bp.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json() or {}
    nombre = data.get('nombre')
    marca = data.get('marca')
    modelo = data.get('modelo')
    nro_serie = data.get('nro_serie')
    codigo_interno = data.get('codigo_interno')
    rubro_id = data.get('rubro_id')

    if not all([nombre, marca, modelo, nro_serie, codigo_interno, rubro_id]):
        return jsonify({'error': 'Todos los campos del producto y rubro_id son obligatorios'}), 400

    existing = Product.query.filter((Product.nro_serie == nro_serie) | (Product.codigo_interno == codigo_interno)).first()
    if existing:
        return jsonify({'error': 'Ya existe un producto con el mismo número de serie o código interno'}), 400

    product = Product(
        nombre=nombre,
        marca=marca,
        modelo=modelo,
        nro_serie=nro_serie,
        codigo_interno=codigo_interno,
        rubro_id=rubro_id
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Producto registrado con éxito', 'product': product.to_dict()}), 201

@product_bp.route('/api/representatives/<int:rep_id>/rubro', methods=['PUT'])
def assign_representative_rubro(rep_id):
    data = request.get_json() or {}
    rubro_id = data.get('rubro_id')

    rep = User.query.get_or_404(rep_id)
    if rep.role != 'representative':
        return jsonify({'error': 'El usuario seleccionado no es un representante'}), 400

    rubro = Rubro.query.get_or_404(rubro_id)
    rep.rubro_id = rubro.id
    db.session.commit()
    return jsonify({'message': 'Especialización de rubro asignada con éxito', 'representative': rep.to_dict()}), 200
