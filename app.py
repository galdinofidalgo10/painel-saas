from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'segredo_super_forte_123'

# =====================
# BANCO DE DADOS
# =====================
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabela():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            plano TEXT DEFAULT 'free'
        )
    ''')
    conn.commit()
    conn.close()

criar_tabela()

# =====================
# LOGIN
# =====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        senha = request.form['password']

        conn = get_db()
        usuario = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user, senha)
        ).fetchone()
        conn.close()

        if usuario:
            session['user_id'] = usuario['id']
            session['plano'] = usuario['plano']
            return redirect('/')
        else:
            return "Login inválido"

    return render_template('login.html')

# =====================
# LOGOUT
# =====================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# =====================
# PROTEÇÃO
# =====================
def protegido():
    return 'user_id' in session

# =====================
# HOME (PAINEL)
# =====================
@app.route('/')
def index():
    if not protegido():
        return redirect('/login')

    plano = session.get('plano')

    return render_template('index.html', plano=plano)

# =====================
# FUNÇÃO PREMIUM
# =====================
@app.route('/consulta')
def consulta():
    if not protegido():
        return redirect('/login')

    if session.get('plano') != 'premium':
        return "⚠️ Você precisa ser PREMIUM para acessar"

    return "🔍 Consulta liberada (dados aqui)"

# =====================
# CRIAR USUÁRIO (teste)
# =====================
@app.route('/criar')
def criar():
    conn = get_db()
    conn.execute("INSERT INTO users (username, password, plano) VALUES (?, ?, ?)",
                 ("admin", "1234", "premium"))
    conn.commit()
    conn.close()
    return "Usuário criado"

# =====================
# RODAR
# =====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
