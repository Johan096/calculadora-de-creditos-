from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    matricula = db.Column(db.String(100), unique=True, nullable=False)

class Materia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    creditos = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

# Rutas
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form["nombre"]
        matricula = request.form["matricula"]
        usuario = Usuario.query.filter_by(matricula=matricula).first()
        if not usuario:
            usuario = Usuario(nombre=nombre, matricula=matricula)
            db.session.add(usuario)
            db.session.commit()
        session["usuario_id"] = usuario.id
        session["nombre"] = usuario.nombre
        session["matricula"] = usuario.matricula
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/inicio", methods=["GET", "POST"])
def index():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    usuario_id = session["usuario_id"]
    if request.method == "POST":
        nombre = request.form["nombre"]
        creditos = int(request.form["creditos"])
        nueva = Materia(nombre=nombre, creditos=creditos, usuario_id=usuario_id)
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for("index"))

    materias = Materia.query.filter_by(usuario_id=usuario_id).all()
    total = sum(m.creditos for m in materias)
    faltan = max(0, 140 - total)
    return render_template("index.html", materias=materias, total=total, faltan=faltan)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    materia = Materia.query.get_or_404(id)
    if request.method == "POST":
        materia.nombre = request.form["nombre"]
        materia.creditos = int(request.form["creditos"])
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("editar.html", materia=materia)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
