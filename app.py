
import re
from flask import Flask, flash, render_template, request, redirect, abort, make_response
from flask_babel import Babel
from flask.logging import create_logger
from babel import numbers, dates
import bd

app = Flask(__name__)
logger = create_logger(app)
app.config["SECRET_KEY"] = "dev-change-me"
app.config["BABEL_DEFAULT_LOCALE"] = "fr_CA"
babel = Babel(app)


# regex pour verifier s'il y a une balise html dans les champs

REGEXE_CHAMPS_HTML = re.compile(r"<(.*)>.*?|<(.*) />")

# pour pourvoir injecter mes cookies dans mes pages


@app.get("/")
def home():
    """Page d'index"""
    # if request.cookies.get("local") is None:
    #     request.set_cookie("local", "fr_CA")

    locale = request.cookies.get("local")
    with bd.creer_connexion() as conn, conn.get_curseur() as cur:
        cur.execute(
            """
            SELECT s.id_service, s.titre, s.localisation, c.nom_categorie
            FROM services s
            JOIN categories c ON c.id_categorie = s.id_categorie
            WHERE s.actif = 1
            ORDER BY s.date_creation DESC
            LIMIT 5
        """
        )
        services = cur.fetchall()
    return render_template("home.jinja", services=services, locale=locale)


@app.post("/locale")
def set_locale():
    """Fonction pour gerer les cookies.""" 
    local_code = request.form.get("local_code", "")
    resp = make_response(redirect("/", code=303))
    resp.set_cookie("local", local_code)
    return resp


@app.get("/publish")
def publish_form():
    """Formulaire d'ajout d'un service.""" 
    locale = request.cookies.get("local")
 # pour afficher la page d'edition en get
    with bd.creer_connexion() as c, c.get_curseur() as cur:
        cur.execute(
            "SELECT id_categorie, nom_categorie FROM categories ORDER BY nom_categorie"
        )
        cats = cur.fetchall()
    return render_template("service_form.jinja", categories=cats, errors={}, form={},locale=locale)


@app.post("/publish")
def publish_submit():
    """Traite l'ajout de service et redirige vers la page de détail."""

    # pour pourvoir remplir la page de modification

    titre = request.form.get("titre", default="").strip()
    localisation = request.form.get("localisation",default= "").strip()
    description = request.form.get("description",default= "") .strip()
    id_categorie = request.form.get("id_categorie")
    actif = 1 if request.form.get("actif", "1") == "1" else 0
    cout = float(request.form.get("cout") or 0)
    errors = {}
    if not (1 <= len(titre) <= 50):
        errors["titre"] = "Le titre est obligatoire (1 à 50 caractères)."
    if not (1 <= len(localisation) <= 50):
        errors["localisation"] = "La localisation est obligatoire (1 à 50 caractères)."
    if len(description) < 5:
        errors["description"] = "Description trop courte (min. 5 caractères)."
    if not id_categorie:
        errors["id_categorie"] = "Choisissez une catégorie."

    # Interdiction des les balises HTML dans les champs texte

    if REGEXE_CHAMPS_HTML.search(titre or ""):
        errors["titre"] = "Le titre ne doit pas contenir de balises HTML."
    if REGEXE_CHAMPS_HTML.search(localisation or ""):
        errors["localisation"] = "La localisation ne doit pas contenir de balises HTML."
    if REGEXE_CHAMPS_HTML.search(description or ""):
        errors["description"] = "La description ne doit pas contenir de balises HTML."

    if errors:
        with bd.creer_connexion() as c, c.get_curseur() as cur:
            cur.execute(
                "SELECT id_categorie, nom_categorie FROM categories ORDER BY nom_categorie"
            )
            cats = cur.fetchall()
        form = {
            "titre": titre,
            "localisation": localisation,
            "description": description,
            "id_categorie": id_categorie,
            "actif": str(actif),
            "cout": cout,
        }
        return (
            render_template(
                "service_form.jinja", categories=cats, errors=errors, form=form
            ),
            400,
        )

    with bd.creer_connexion() as c, c.get_curseur() as cur:
        cur.execute(
            """
            INSERT INTO services (id_categorie, titre, description, localisation, actif, cout)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (id_categorie, titre, description, localisation, actif, cout),
        )
        new_id = cur.lastrowid

    flash("Service ajouté avec succès.", "success")
    return redirect(f"/services/detail?service_id={new_id}", code=303)
    # ---------- Liste des services

@app.get("/services")
def services_list():
    """Liste filtrable de tous les services."""
    locale = request.cookies.get("local")
    q = request.args.get("q", default="").strip()
    categorie = request.args.get("categorie")
    localisation = request.args.get("localisation",default= "").strip()

    sql = """
        SELECT s.*, c.nom_categorie
        FROM services s JOIN categories c USING(id_categorie)
        WHERE 1=1
    """
    params = []
    if q:
        sql += " AND (s.titre LIKE %s OR s.description LIKE %s)"
        params += [f"%{q}%", f"%{q}%"]
    if categorie:
        sql += " AND s.id_categorie=%s"
        params.append(categorie)
    if localisation:
        sql += " AND s.localisation LIKE %s"
        params.append(f"%{localisation}%")
    sql += " ORDER BY s.date_creation DESC"

    with bd.creer_connexion() as c, c.get_curseur() as cur:
        cur.execute("SELECT id_categorie, nom_categorie FROM categories ORDER BY nom_categorie")
        cats = cur.fetchall()
        cur.execute(sql, params)
        rows = cur.fetchall()

    return render_template("service_list.jinja", services=rows, categories=cats,locale=locale)


    # ---------- Détail


@app.get("/services/detail")
def service_detail_qs():
    """Affiche la page de détails (service_id en query string)."""
    locale = request.cookies.get("local")
    devise = "CAD"

    if locale == "en_US":
        devise = "US"
      
     

    service_id = request.args.get("service_id", type=int)
    if not service_id:
        abort(404)
    with bd.creer_connexion() as c, c.get_curseur() as cur:
        cur.execute(
            """
            SELECT s.*, c.nom_categorie
            FROM services s JOIN categories c USING(id_categorie)
            WHERE s.id_service=%s
        """,
            (service_id,),
        )
        s = cur.fetchone()
    if not s:
        abort(404)
    s["date_creation"]=dates.format_date(s["date_creation"], locale=locale) 
    s["cout"]=numbers.format_currency(s["cout"], devise, locale=locale)

    return render_template("service_detail.jinja", s=s,locale=locale)


# ---------- Édition (GET + POST)
# get


@app.get("/services/edit")
def edit_service_form_qs():
    locale = request.cookies.get("local")
    service_id = request.args.get("service_id", type=int)
    if not service_id:
        abort(404)
    with bd.creer_connexion() as c, c.get_curseur() as cur:
        cur.execute(
            """
            SELECT s.*, c.nom_categorie
            FROM services s JOIN categories c USING(id_categorie)
            WHERE s.id_service=%s
        """,
            (service_id,),
        )
        s = cur.fetchone()
    if not s:
        abort(404)
    return render_template("service_edit.jinja", s=s, errors={}, form={},locale=locale)

    # POST


@app.post("/services/edit")
def edit_service_save_qs():
    """Enregistre les modifications d'un service."""
    locale = request.cookies.get("local")
    service_id = request.form.get("service_id", type=int)
    if not service_id:
        abort(404)

    form = {
        "titre": request.form.get("titre", default="") .strip(),
        "localisation": request.form.get("localisation",default= "").strip(),
        "description": request.form.get("description", "").strip(),
        "actif": request.form.get("actif", "1").strip(),
        "cout": request.form.get("cout").strip(),
    }

    errors = {}
    if not (1 <= len(form["titre"]) <= 50):
        errors["titre"] = "Le titre est obligatoire (1 à 50 caractères)."
    if not (1 <= len(form["localisation"]) <= 50):
        errors["localisation"] = "La localisation est obligatoire (1 à 50 caractères)."
    if len(form["description"]) < 5:
        errors["description"] = "Description trop courte (min. 5 caractères)."

    cout_val = float(form["cout"] or 0)

    if form["actif"] not in ("0", "1"):
        form["actif"] = "1"
    # Interdire les balises HTML dans les champs texte
    if REGEXE_CHAMPS_HTML.search(form["titre"] or ""):
        errors["titre"] = "Le titre ne doit pas contenir de balises HTML."
    if REGEXE_CHAMPS_HTML.search(form["localisation"] or ""):
        errors["localisation"] = "La localisation ne doit pas contenir de balises HTML."
    if REGEXE_CHAMPS_HTML.search(form["description"] or ""):
        errors["description"] = "La description ne doit pas contenir de balises HTML."

    if errors:
        # on recharge l'objet pour réafficher le formulaire avec erreurs
        with bd.creer_connexion() as c, c.get_curseur() as cur:
            cur.execute(
                """
                SELECT s.*, c.nom_categorie
                FROM services s JOIN categories c USING(id_categorie)
                WHERE s.id_service=%s
            """,
                (service_id,),
            )
            s = cur.fetchone()
        return render_template("service_edit.jinja", s=s, errors=errors, form=form,locale=locale), 400

    # UPDATE
    with bd.creer_connexion() as c, c.get_curseur() as cur:
        cur.execute(
            """
            UPDATE services
               SET titre=%s, description=%s, localisation=%s, actif=%s, cout=%s
             WHERE id_service=%s
        """,
            (
                form["titre"],
                form["description"],
                form["localisation"],
                int(form["actif"]),
                cout_val,
                service_id,
            ),
        )

    flash("Service mis à jour.", "success")
    return redirect(
        f"/services/detail?service_id={service_id}",
          code=303)
@app.errorhandler(400)
def bad_request(e):
    """Pour les erreurs 400"""
    logger.exception(e)

    return render_template(
        'erreur.jinja',
        message="code 400: Page Introuvable Desolé.",code ="400"), 400
   

@app.errorhandler(404)
def not_found(e):
    """Fonction qui gère l'erreur 404"""
    logger.exception(e)
    # c'est quoi l'erreur 404 ? ca signifie quoi ?
    return render_template("erreur.jinja", message = "code 404: Détails d’un service inexistant"), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Pour les erreurs 500"""

    logger.exception(e)

    message = "code 500: Erreur en lien avec la BD"

    return render_template(
        'erreur.jinja',
        message=message
    ), 500


if __name__ == "__main__":
    app.run(debug=True)
