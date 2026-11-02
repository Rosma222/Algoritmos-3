from . import db

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    nro_serie = db.Column(db.String(100), unique=True, nullable=False)
    codigo_interno = db.Column(db.String(100), unique=True, nullable=False)
    rubro_id = db.Column(db.Integer, db.ForeignKey('rubros.id'), nullable=False)

    rubro = db.relationship('Rubro', backref=db.backref('productos', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'marca': self.marca,
            'modelo': self.modelo,
            'nro_serie': self.nro_serie,
            'codigo_interno': self.codigo_interno,
            'rubro_id': self.rubro_id,
            'rubro': self.rubro.nombre if self.rubro else None
        }
