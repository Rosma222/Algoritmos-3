from datetime import datetime
from . import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    leida = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.String(20), nullable=False, default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mensaje': self.mensaje,
            'leida': self.leida,
            'fecha': self.fecha
        }
