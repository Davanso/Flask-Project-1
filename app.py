from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuração do SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo do Livro
class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    data_publicacao = db.Column(db.Date, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    emprestimos = db.relationship('Emprestimo', backref='livro', lazy=True)

    def __repr__(self):
        return f'<Livro {self.titulo}>'

# Modelo de Empréstimo
class Emprestimo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_aluno = db.Column(db.String(200), nullable=False)
    ra = db.Column(db.String(20), nullable=False)
    data_emprestimo = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_devolucao = db.Column(db.DateTime)
    data_limite = db.Column(db.DateTime, nullable=False)
    devolvido = db.Column(db.Boolean, default=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)

    def __repr__(self):
        return f'<Emprestimo {self.nome_aluno} - {self.livro.titulo}>'

# Cria o banco de dados
with app.app_context():
    db.create_all()

# Rota principal - lista todos os livros
@app.route('/')
def index():
    livros = Livro.query.order_by(Livro.data_cadastro.desc()).all()
    return render_template('index.html', livros=livros)

# Rota para adicionar livro
@app.route('/adicionar_livro', methods=['POST'])
def adicionar_livro():
    titulo = request.form['titulo']
    autor = request.form['autor']
    data_publicacao = datetime.strptime(request.form['data_publicacao'], '%Y-%m-%d')
    
    novo_livro = Livro(
        titulo=titulo,
        autor=autor,
        data_publicacao=data_publicacao
    )
    
    try:
        db.session.add(novo_livro)
        db.session.commit()
        return redirect('/')
    except:
        return 'Houve um erro ao cadastrar o livro'

# Rota para remover livro
@app.route('/remover/<int:id>')
def remover_livro(id):
    livro = Livro.query.get_or_404(id)
    
    try:
        db.session.delete(livro)
        db.session.commit()
        return redirect('/')
    except:
        return 'Houve um erro ao remover o livro'

# Rota para página de empréstimo
@app.route('/emprestar/<int:livro_id>')
def pagina_emprestimo(livro_id):
    livro = Livro.query.get_or_404(livro_id)
    return render_template('emprestar.html', livro=livro)

# Rota para realizar empréstimo
@app.route('/realizar_emprestimo/<int:livro_id>', methods=['POST'])
def realizar_emprestimo(livro_id):
    livro = Livro.query.get_or_404(livro_id)
    
    nome_aluno = request.form['nome_aluno']
    ra = request.form['ra']
    data_emprestimo = datetime.now()
    # Define prazo de 14 dias para devolução
    data_limite = data_emprestimo + timedelta(days=14)
    
    novo_emprestimo = Emprestimo(
        nome_aluno=nome_aluno,
        ra=ra,
        data_emprestimo=data_emprestimo,
        data_limite=data_limite,
        livro_id=livro_id
    )
    
    try:
        db.session.add(novo_emprestimo)
        db.session.commit()
        return redirect('/')
    except:
        return 'Houve um erro ao registrar o empréstimo'

# Rota para listar empréstimos
@app.route('/emprestimos')
def listar_emprestimos():
    emprestimos = Emprestimo.query.order_by(Emprestimo.data_emprestimo.desc()).all()
    return render_template('emprestimos.html', emprestimos=emprestimos, datetime=datetime)

# Rota para registrar devolução
@app.route('/devolver/<int:emprestimo_id>')
def devolver_livro(emprestimo_id):
    emprestimo = Emprestimo.query.get_or_404(emprestimo_id)
    
    try:
        emprestimo.devolvido = True
        emprestimo.data_devolucao = datetime.now()
        db.session.commit()
        return redirect('/emprestimos')
    except:
        return 'Houve um erro ao registrar a devolução'

if __name__ == '__main__':
    app.run(debug=True)