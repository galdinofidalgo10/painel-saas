from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ---------------- BANCO ---------------- #

def conectar():
    return sqlite3.connect("database.db")

def criar_db():
    con = conectar()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios_admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT,
        creditos INTEGER DEFAULT 5
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pagamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT,
        valor REAL,
        status TEXT
    )
    """)

    con.commit()
    con.close()

criar_db()

# ---------------- ADMIN PADRÃO ---------------- #

def criar_admin():
    con = conectar()
    cur = con.cursor()

    senha_hash = generate_password_hash("123456")

    try:
        cur.execute("INSERT INTO usuarios_admin (username, password) VALUES (?, ?)", ("admin", senha_hash))
        con.commit()
    except:
        pass

    con.close()

criar_admin()

# ---------------- SEGURANÇA ---------------- #

def protegido():
    return "logado" in session

# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        senha = request.form["password"]

        con = conectar()
        cur = con.cursor()

        cur.execute("SELECT password FROM usuarios_admin WHERE username=?", (user,))
        resultado = cur.fetchone()

        if resultado and check_password_hash(resultado[0], senha):
            session["logado"] = True
            return redirect("/")
        else:
            return render_template("login.html", erro="Usuário ou senha inválidos")

    return render_template("login.html")

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- DASHBOARD ---------------- #

@app.route("/")
def index():
    if not protegido():
        return redirect("/login")

    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM usuarios")
    usuarios = cur.fetchone()[0]

    cur.execute("SELECT SUM(valor) FROM pagamentos WHERE status='aprovado'")
    faturamento = cur.fetchone()[0] or 0

    return render_template("index.html", usuarios=usuarios, faturamento=faturamento)

# ---------------- USUÁRIOS ---------------- #

@app.route("/usuarios")
def usuarios():
    if not protegido():
        return redirect("/login")

    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT * FROM usuarios")
    dados = cur.fetchall()

    return render_template("usuarios.html", dados=dados)

@app.route("/add_user", methods=["POST"])
def add_user():
    if not protegido():
        return redirect("/login")

    telegram_id = request.form["telegram_id"]

    con = conectar()
    cur = con.cursor()

    cur.execute("INSERT INTO usuarios (telegram_id, creditos) VALUES (?, 5)", (telegram_id,))
    con.commit()

    return redirect("/usuarios")

@app.route("/add_credito", methods=["POST"])
def add_credito():
    if not protegido():
        return redirect("/login")

    user_id = request.form["id"]
    valor = int(request.form["creditos"])

    con = conectar()
    cur = con.cursor()

    cur.execute("UPDATE usuarios SET creditos = creditos + ? WHERE id=?", (valor, user_id))
    con.commit()

    return redirect("/usuarios")

# ---------------- PAGAMENTOS ---------------- #

@app.route("/pagamentos")
def pagamentos():
    if not protegido():
        return redirect("/login")

    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT * FROM pagamentos")
    dados = cur.fetchall()

    return render_template("pagamentos.html", dados=dados)

# ---------------- PRODUÇÃO ---------------- #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
