from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    favorito = db.relationship("Favorito", back_populates = "usuario", uselist = False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    nombre = db.Column(db.String(50), nullable = False)
    apellido = db.Column(db.String(50), nullable = True)



    def __repr__(self):
        return '<Usuario %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "nombre": self.nombre,
            # do not serialize the password, its a security breach
        }

class Favorito(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    usuario = db.relationship("Usuario", back_populates = "favorito")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable = False)

    planeta = db.relationship("Planeta")
    planeta_id = db.Column(db.Integer, db.ForeignKey("planeta.id"), nullable = True)

    personaje = db.relationship("Personaje")
    personaje_id = db.Column(db.Integer, db.ForeignKey("personaje.id"), nullable = True)

    # __table_args__= (db.UniqueConstraint{
    #     user_id,
    #     planeta_id,
    #     personaje_id,
    #     name="debe tener una sola coincidencia"
    # },)


    def serialize(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "planeta_id": self.planeta_id,
            "personaje_id": self.personaje_id
        }

class Planeta(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    name = db.Column(db.String(30), nullable = False)
    population = db.Column(db.Integer, nullable = False)
    climate = db.Column(db.String(30), nullable = False)
    terrain = db.Column(db.String(30), nullable = False)
    gravity = db.Column(db.String(30), nullable = False)

    def __repr__(self):
        return '<Planeta %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.name,
        }

class Personaje(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    name = db.Column(db.String(30), nullable = False)
    hair_color = db.Column(db.String(30), nullable = False)
    eyes_color = db.Column(db.String(30), nullable = False)
    gender = db.Column(db.String(30), nullable = False)

    def __repr__(self):
        return '<Personaje %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.name,
        }

