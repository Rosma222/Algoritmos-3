from datetime import datetime
from . import db

class Hito(db.Model):
    __tablename__ = 'hitos'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.String(20), nullable=False, default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    ticket = db.relationship('Ticket', backref=db.backref('hitos', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('hitos', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'role': self.user.role if self.user else None,
            'mensaje': self.mensaje,
            'fecha': self.fecha
        }
