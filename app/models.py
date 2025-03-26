from app import db
from sqlalchemy import PrimaryKeyConstraint

class Widget(db.Model):
    __tablename__ = 'widgets'
    id_widget = db.Column(db.String(30), primary_key=True, nullable=False)
    name_widget = db.Column(db.Text, nullable=False)
    paid = db.Column(db.Boolean, default=None)
    price = db.Column(db.DECIMAL(8, 2), default=None)

    def __repr__(self):
        return f"<Widget(id_widget='{self.id_widget}', name_widget='{self.name_widget}')>"

class Installation(db.Model):
    __tablename__ = 'installations'
    client_domain = db.Column(db.String(255), primary_key=True, nullable=False)
    id_widget = db.Column(db.String(30), primary_key=True, nullable=False)
    date_install = db.Column(db.Date, nullable=False)
    date_expire = db.Column(db.Date, nullable=False)
    trial = db.Column(db.Boolean, default=None)
    status = db.Column(db.SmallInteger, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('client_domain', 'id_widget'),
    )

    def __repr__(self):
        return f"<Installation(client_domain='{self.client_domain}', id_widget='{self.id_widget}')>"