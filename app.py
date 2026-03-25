from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_123'

# -----------------------------
# CONEXÃO COM BANCO
# -----------------------------
def get_db():
    return sqlite3.connect('database.db')


# -----------------------------
# LOGIN
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = username
            return redirect('/')
        else:
            return "Login inválido"

    return render_template('login.html')


# -----------------------------
# PROTEGER ROTAS
# -----------------------------
def proteger():
    if 'user' not in session:
        return False
    return True


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route('/')
def home():
    if not proteger():
        return redirect('/login')

    return render_template('index.html')


# -----------------------------
# USUÁRIOS
# -----------------------------
@app.route('/usuarios')
def usuarios():
    if not proteger():
        return redirect('/login')

    return render_template('usuarios.html')


# -----------------------------
# PAGAMENTOS
# -----------------------------
@app.route('/pagamentos')
def pagamentos():
    if not proteger():
        return redirect('/login')

    return render_template('pagamentos.html')


# -----------------------------
# LOGOUT (IMPORTANTE)
# -----------------------------
@app.route('/logout')
def logout():
    session.clear()  # limpa toda sessão
    return redirect('/login')


# -----------------------------
# RODAR APP
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
