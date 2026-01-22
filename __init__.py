from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)                                                                                                                  
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn
conn = get_db()
cursor = conn.cursor()


# Fonction pour créer une clé "authentifie" dans la session utilisateur
def est_authentifie():
    return session.get('authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification'))

  # Si l'utilisateur est authentifié
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Vérifier les identifiants
        if request.form['username'] == 'admin' and request.form['password'] == 'password': # password à cacher par la suite
            session['authentifie'] = True
            # Rediriger vers la route lecture après une authentification réussie
            return redirect(url_for('lecture'))
        else:
            # Afficher un message d'erreur si les identifiants sont incorrects
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')  # Rediriger vers la page d'accueil après l'enregistrement
    

@app.route("/fiche_nom", methods=["GET", "POST"])
def fiche_nom():
    auth = request.authorization
    if not auth or auth.username != "user" or auth.password != "12345":
        return ("Accès refusé", 401, {
            "WWW-Authenticate": 'Basic realm="Login requis"'
        })

    nom = request.form.get("nom")
    data = []

    if nom:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM clients WHERE nom LIKE ?",
            (f"%{nom}%",)
        )
        data = cursor.fetchall()

    return render_template("fiche_nom.html", data=data)







@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role FROM users WHERE username=? AND password=?",
            (user, pwd)
        )
        res = cursor.fetchone()

        if res:
            session["user_id"] = res["id"]
            session["role"] = res["role"]
            return redirect("/livres")

    return render_template("formulaire_authentification.html")


@app.route("/livres")
def livres():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livres")
    livres = cursor.fetchall()
    return render_template("read_data.html", livres=livres)





@app.route("/ajouter_livre", methods=["GET", "POST"])
def ajouter_livre():
    if session.get("role") != "admin":
        return "Accès interdit", 403

    if request.method == "POST":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)",
            (request.form["titre"], request.form["auteur"], request.form["stock"])
        )
        conn.commit()
        return redirect("/livres")

    return render_template("ajouter_client.html")

@app.route("/emprunter/<int:id>")
def emprunter(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO emprunts (user_id, livre_id) VALUES (?, ?)",
        (session["user_id"], id)
    )
    cursor.execute(
        "UPDATE livres SET stock = stock - 1 WHERE id=?",
        (id,)
    )
    conn.commit()
    return redirect("/livres")



@app.route("/api/livres")
def api_livres():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT titre, auteur, stock FROM livres")
    return jsonify(cursor.fetchall())



def get_tasks_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/tasks")
def tasks_home():
    return render_template("tasks_home.html")



                                                                                                                                       
if __name__ == "__main__":
  app.run(debug=True)
