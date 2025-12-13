from flask import Flask, render_template, request, redirect, make_response, session,url_for,g
from flask_babel import Babel
from service import bp_service
from reservation import bp_reservation
from compte import bp_compte
from api import bp_api
import os
import logging
import dotenv 
from api import bp_api



if not os.getenv('BD_UTILISATEUR'):
    dotenv.load_dotenv('.env')

app = Flask(__name__)


app.logger.setLevel(logging.DEBUG)
app.config['CHEMIN_VERS_AJOUTS'] = os.path.join('static', 'images', 'ajouts')
os.makedirs(app.config['CHEMIN_VERS_AJOUTS'], exist_ok=True)

app.config["BABEL_DEFAULT_LOCALE"] = "fr_CA"
app.secret_key = os.getenv('SECRET_SESSION')
babel = Babel(app)


@app.before_request
def load_user():
    """utilisateur"""
    g.user = None
    if session.get("id_utilisateur"):
        g.user = {
            "id": session["id_utilisateur"],
            "courriel": session.get("courriel"),
            "role": session.get("role"),
            "credit": session.get("credit"),
        }

app.register_blueprint(bp_service, url_prefix="/")
app.register_blueprint(bp_reservation, url_prefix="/reservation")
app.register_blueprint(bp_compte, url_prefix="/compte")
app.register_blueprint(bp_api, url_prefix="/api")

@app.route("/")
def home():
    """page acceuil"""
    return redirect(url_for('services_list'))



@app.post("/locale")
def set_locale():
    """Gère le changement de langue via cookie."""
    code = (request.form.get("local_code") or "fr_CA").strip()
    if code not in ("fr_CA", "en_CA", "en_US"):
        code = "fr_CA"

    resp = make_response(redirect(request.referrer or "/", 303))
    resp.set_cookie("local", code, max_age=3600 * 24 * 365, samesite="Lax")
    return resp


@app.errorhandler(403)
def e403(_e):
    """Pour les erreurs 403 (Accès Interdit)."""
    return render_template(
        "erreur/erreur.jinja",
        message="Vous n'avez pas la permission d'accéder à cette ressource.", tittle ="Code 403 : Accès Interdit"
    ), 403


@app.errorhandler(404)
def e404(_e):
    """message erreur 404"""
    return render_template("erreur/erreur.jinja", message=" Détails d’un service inexistant", tittle ="Code 404 : service inexistant"),404


@app.errorhandler(400)
def e400(_e):
    """"message erreur"""
    return render_template("erreur/erreur.jinja", message="code 400: Requête invalide",tittle ="Code 400 : Requête invalide" ), 400


@app.errorhandler(500)
def e500(_e):
    """message erreur lié à la BD"""
    return render_template("erreur/erreur.jinja", message="code 500: Erreur en lien avec la BD",tittle ="Code 500 : Erreur BD"), 500


if __name__ == "__main__":
    app.run(debug=True)
