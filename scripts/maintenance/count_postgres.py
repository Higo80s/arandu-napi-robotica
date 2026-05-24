
from flask import Flask
from models import db, User, Campus, ProgramaAcademico, Edital, Modalidade, Bolsista

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost:5432/gestao_editais'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("Contagem de Registros (PostgreSQL):")
    print(f"Usuarios: {User.query.count()}")
    print(f"Campus: {Campus.query.count()}")
    print(f"Programas: {ProgramaAcademico.query.count()}")
    print(f"Editais: {Edital.query.count()}")
    print(f"Modalidades: {Modalidade.query.count()}")
    print(f"Bolsistas: {Bolsista.query.count()}")
