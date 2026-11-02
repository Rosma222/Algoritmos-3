from datetime import datetime
from . import db

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    representative_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rubro_id = db.Column(db.Integer, db.ForeignKey('rubros.id'), nullable=False)
    asunto = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='Abierto') # Abierto, En Progreso, Resuelto, Cerrado
    fecha_creacion = db.Column(db.String(20), nullable=False, default=lambda: datetime.now().strftime('%Y-%m-%d'))

    client = db.relationship('User', foreign_keys=[client_id], backref=db.backref('tickets_como_cliente', lazy=True))
    representative = db.relationship('User', foreign_keys=[representative_id], backref=db.backref('tickets_como_representante', lazy=True))
    product = db.relationship('Product', backref=db.backref('tickets', lazy=True))
    rubro = db.relationship('Rubro', backref=db.backref('tickets', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_name': self.client.username if self.client else None,
            'representative_id': self.representative_id,
            'representative_name': self.representative.username if self.representative else 'Sin Asignar',
            'product_id': self.product_id,
            'product_info': f"{self.product.marca} {self.product.nombre} ({self.product.codigo_interno})" if self.product else None,
            'rubro_id': self.rubro_id,
            'rubro_name': self.rubro.nombre if self.rubro else None,
            'asunto': self.asunto,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion,
            'hitos': [h.to_dict() for h in self.hitos]
        }
