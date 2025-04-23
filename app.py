import datetime
import secrets
from random import randint
import sqlalchemy as db
from sqlalchemy import func, desc

from flask import Flask, render_template, request, redirect, url_for, session
from PyPDF2 import PdfReader
import os
import plotly.express as px
import pandas as pd

from db_connection import *

app = Flask(__name__)
app.secret_key = secrets.token_hex()

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://adrien:password@localhost/perso'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_app(app)

# Liste d'élèves fictive
liste_eleves = [
    {'nom': 'Dupont', 'prenom': 'Jean', 'age': 20},
    {'nom': 'Martin', 'prenom': 'Marie', 'age': 20},
    {'nom': 'Durand', 'prenom': 'Pierre', 'age': 21},
    {'nom': 'Leroy', 'prenom': 'Sophie', 'age': 21},
    {'nom': 'Moreau', 'prenom': 'Luc', 'age': 19},
]

@app.route('/')
def index():
    # Page d'accueil
    return render_template('index.html')

@app.route('/heure')
def heure():
    # Affiche l'heure actuelle
    date_heure = datetime.datetime.now()
    h = date_heure.hour
    m = date_heure.minute
    s = date_heure.second
    return render_template('heure.html', h=h, m=m, s=s)

@app.route('/eleves')
def eleves():
    # Filtre les élèves par âge si un paramètre est fourni
    age = request.args.get('age', type=int)
    eleves_select = [eleve for eleve in liste_eleves if eleve['age'] == age] if age else liste_eleves
    return render_template('eleve.html', liste_eleves=eleves_select)

# Liste d'utilisateurs fictive
utilisateurs = [
    {"nom": "admin", "mdp": "1234"},
    {"nom": "marie", "mdp": "nsi"},
    {"nom": "paul", "mdp": "azerty"}
]

def recherche_utilisateur(nom_utilisateur, mot_de_passe):
    # Recherche un utilisateur dans la liste en fonction du nom et du mot de passe
    for utilisateur in utilisateurs:
        if utilisateur['nom'] == nom_utilisateur and utilisateur['mdp'] == mot_de_passe:
            return utilisateur
    return None

@app.route("/login", methods=["POST", "GET"])
def login():
    # Gère la connexion des utilisateurs
    if request.method == "POST":
        donnees = request.form
        nom = donnees.get('nom')
        mdp = donnees.get('mdp')

        utilisateur = recherche_utilisateur(nom, mdp)

        if utilisateur is not None:
            # Si l'utilisateur est trouvé, on le connecte
            session['nom_utilisateur'] = utilisateur['nom']
            return redirect(url_for('index'))
        else:
            # Si l'utilisateur est inconnu, on reste sur la page de connexion
            return redirect(request.url)
    else:
        # Si l'utilisateur est déjà connecté, on le redirige vers l'accueil
        if 'nom_utilisateur' in session:
            return redirect(url_for('index'))
        return render_template("login.html")

@app.route('/logout')
def logout():
    # Déconnecte l'utilisateur
    session.pop('nom_utilisateur', None)
    return redirect(url_for('login'))

@app.route("/compteur")
def compteur():
    # Compte le nombre de visites de la page par l'utilisateur
    if "compteur" not in session:
        session['compteur'] = 1
    else:
        session['compteur'] = session['compteur'] + 1
    nb_visites = session['compteur']
    return f"Vous avez visité cette page {nb_visites} fois"

@app.route("/traitement", methods=["POST", "GET"])
def traitement():
    # Traite les données soumises par un formulaire
    if request.method == "POST":
        donnees = request.form
        nom = donnees.get('nom')
        mdp = donnees.get('mdp')
        if nom == 'admin' and mdp == '1234':
            # Si les identifiants sont corrects, on affiche un message
            return render_template("traitement.html", nom_utilisateur=nom)
        else:
            # Sinon, on affiche une page sans message
            return render_template("traitement.html")
    else:
        # Redirige vers l'accueil si la méthode est GET
        return redirect(url_for('index'))

@app.route("/jeu", methods=["POST", "GET"])
def jeu():
    # Jeu du nombre mystère
    if request.method == "POST":
        reponse = int(request.form.get('nombre'))
        if reponse == session['nombre']:
            # Si l'utilisateur trouve le nombre
            message = "Bravo, vous avez trouvé le nombre mystère !"
            session["en_cours"] = False
        elif reponse < session['nombre']:
            # Si le nombre est trop petit
            message = "Trop petit !"
        else:
            # Si le nombre est trop grand
            message = "Trop grand !"
        return render_template("nombre_mystere.html", message=message)
    else:
        # Initialise un nouveau nombre mystère
        nombre = randint(0, 100)
        session['nombre'] = nombre
        session['en_cours'] = True
        return render_template("nombre_mystere.html")

@app.route("/somme", methods=["POST", "GET"])
def somme():
    # Calcule la somme des chiffres d'un nombre entier
    if request.method == "POST":
        donnees = request.form.get('nombre')
        resultat = sum(int(i) for i in donnees)

        # Enregistre le calcul dans la base de données
        db.session.add(Calcul(
            nombre=donnees,
            somme=resultat,
            utilisateur=session['nom_utilisateur'],
            date_calcul=datetime.datetime.now()
        ))
        db.session.commit()

        return render_template("somme.html", resultat=resultat, nombre=donnees)
    else:
        # Affiche le formulaire de calcul
        return render_template("somme.html")

@app.route("/pdf", methods=["POST", "GET"])
def pdf():
    # Analyse un fichier PDF pour compter le nombre de mots
    if request.method == "POST":
        fichier = request.files['pdf_file']
        if fichier:
            chemin = f"uploads/{fichier.filename}"
            os.makedirs("uploads", exist_ok=True)
            fichier.save(chemin)
            lecteur = PdfReader(chemin)
            contenu = ""
            for page in lecteur.pages:
                contenu += page.extract_text() or ""
            nombre_mots = len(contenu.split())

            # Enregistre les données dans la base de données
            db.session.add(Document(
                nb_test=nombre_mots,
                date_upload=datetime.datetime.now()
            ))
            db.session.commit()

            return render_template("pdf.html", nombre_mots=nombre_mots)
        return None
    else:
        # Affiche le formulaire d'upload
        return render_template("pdf.html")

@app.route("/visualisation", methods=["POST", "GET"])
def visualisation():
    # Génère un graphique des utilisateurs avec le plus de tests réalisés
    données = (
        db.session.query(Calcul.utilisateur, func.count().label("nb_test"))
        .group_by(Calcul.utilisateur)
        .order_by(desc("nb_test"))
        .limit(5)
        .all()
    )

    # Convertit les résultats en DataFrame
    df = pd.DataFrame(données, columns=['utilisateur', 'nb_test'])

    # Crée le graphique
    fig = px.bar(df, x='utilisateur', y='nb_test', title='Top 5 des utilisateurs par nombre de tests réalisés')
    fig.update_layout(xaxis_title='Utilisateur', yaxis_title='Nombre de tests')

    # Convertit le graphique en HTML
    graph_html = fig.to_html(full_html=False)

    # Affiche le graphique dans le template
    return render_template("visualisation.html", graph_html=graph_html)

if __name__ == '__main__':
    # Lance l'application Flask
    app.run(debug=True)