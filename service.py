import re
from flask import Blueprint, render_template, request, redirect, abort, flash, session, url_for, g
from babel import numbers, dates
import bd

bp = Blueprint("service", __name__)

REGEXE_CHAMPS_HTML = re.compile(r"<(.*)>.*?|<(.*) />")

@bp.route("/")
def home():
    """Page d'accueil affichant les derniers services."""
    locale = request.cookies.get("local", "fr_CA")
    try:
        with bd.creer_connexion() as conn:
            services = bd.get_service_all(conn)
            if not services:
                abort(400)
        return render_template("home.jinja", services=services, locale=locale)
    except Exception as e:
        flash(f"Erreur de base de données au chargement de la page d'accueil: {e}", "danger")
        return render_template("home.jinja", services=[], locale=locale)

@bp.route("/services")
def services_list():
    """Liste des services avec filtres."""
    locale = request.cookies.get("local", "fr_CA")
    q = (request.args.get("q") or "").strip()
    categorie = request.args.get("categorie")
    localisation = (request.args.get("localisation") or "").strip()

    try:
        with bd.creer_connexion() as conn:
            cats = bd.get_categories(conn)
            rows = bd.search_services(conn, q=q, categorie=categorie, localisation=localisation)
    except Exception as e:
        flash(f"Erreur de base de données lors de la recherche: {e}", "danger")
        cats, rows = [], []

    return render_template("services/service_list.jinja", services=rows, categories=cats, locale=locale)

@bp.route("/<int:id_service>/supprimer", methods=["POST", "GET"])
def supprimer_service(id_service):

    # Vérifie si l'utilisateur est un admin
    if not session.get('est_admin', False):
        
        flash("Accès refusé !", "danger")
        return redirect(url_for('service.services_list'))

    with bd.creer_connexion() as conn:
        bd.supprimer_service(conn, id_service)

  
    flash("Le service a été supprimé !", "success")
    return redirect(url_for('service.services_list'))
     

@bp.route("/services/<int:service_id>")
def service_detail(service_id: int):
    """Détail d'un service."""
    locale = request.cookies.get("local", "fr_CA")
    devise = "USD" if locale == "en_US" else "CAD"

    if not service_id:
        abort(404)

    try:
        with bd.creer_connexion() as conn:
            s = bd.get_service_by_id(conn, service_id)
    except Exception:
        abort(500)

    if not s:
        abort(404)

    s["date_creation_formattee"] = dates.format_date(s["date_creation"], locale=locale)
    s["cout_formatte"] = numbers.format_currency(s["cout"], devise, locale=locale)
    return render_template("service_detail.jinja", s=s, locale=locale)

@bp.route("/publish", methods=["GET", "POST"])
def publish():
    """Ajout d'un service (auth requis)."""
    if not g.user:
        flash("Vous devez être connecté pour publier un service.", "warning")
        return redirect(url_for("compte.connexion"))

    id_proprietaire = g.user["id"]
    locale = request.cookies.get("local", "fr_CA")

    if request.method == "GET":
        with bd.creer_connexion() as conn:
            cats = bd.get_categories(conn)
        return render_template("service_form.jinja", categories=cats, errors={}, form={}, locale=locale)

   
    titre = (request.form.get("titre") or "").strip()
    localisation = (request.form.get("localisation") or "").strip()
    description = (request.form.get("description") or "").strip()
    id_categorie = request.form.get("id_categorie", type=int)
    actif = 1 if (request.form.get("actif") or "1") == "1" else 0
    try:
        cout = float(request.form.get("cout") or 0)
    except ValueError:
        cout = -1

    errors = {}
    if not (1 <= len(titre) <= 50):
        errors["titre"] = "Le titre est obligatoire (1 à 50 caractères)."
    if cout < 0:
        errors["cout"] = "Le coût doit être un nombre positif."

    if errors:
        with bd.creer_connexion() as conn:
            cats = bd.get_categories(conn)
        form = {
            "titre": titre,
            "localisation": localisation,
            "description": description,
            "id_categorie": id_categorie,
            "actif": str(actif),
            "cout": request.form.get("cout", ""),
        }
        return render_template("service_form.jinja", categories=cats, errors=errors, form=form, locale=locale), 400

    try:
        with bd.creer_connexion() as conn:
            new_id = bd.ajout_service(conn, id_categorie, titre, description, localisation, actif, cout, id_proprietaire)
    except Exception as e:
        print(f"Erreur d'ajout de service: {e}")
        flash("Erreur lors de l'ajout du service en base de données.", "danger")
        return redirect(url_for(".publish"))

    flash("Service ajouté avec succès.", "success")
    return redirect(url_for(".service_detail", service_id=new_id), code=303)

@bp.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
def edit_service(service_id: int):
    """Édition d'un service (propriétaire seulement)."""
    if not g.user:
        flash("Vous devez être connecté pour modifier un service.", "warning")
        return redirect(url_for("compte.connexion"))

    id_utilisateur_session = g.user["id"]
    locale = request.cookies.get("local", "fr_CA")

    if not service_id:
        abort(404)

    try:
        with bd.creer_connexion() as conn:
            s = bd.get_service_by_id(conn, service_id)
            if not s:
                abort(404)

            if s["id_utilisateur"] != id_utilisateur_session:
                flash("Vous n'êtes pas autorisé à modifier ce service.", "danger")
                abort(403)

            cats = bd.get_categories(conn)

            if request.method == "GET":
                form_data = {
                    "titre": s["titre"],
                    "localisation": s["localisation"],
                    "description": s["description"],
                    "actif": str(s["actif"]),
                    "cout": s["cout"],
                }
                return render_template("service_edit.jinja", s=s, categories=cats, errors={}, form=form_data, locale=locale)

            titre = (request.form.get("titre") or "").strip()
            localisation = (request.form.get("localisation") or "").strip()
            description = (request.form.get("description") or "").strip()
            actif = 1 if (request.form.get("actif") or "1") == "1" else 0
            try:
                cout = float(request.form.get("cout") or 0)
            except ValueError:
                cout = -1

            errors = {}
            if not (1 <= len(titre) <= 50):
                errors["titre"] = "Le titre est obligatoire (1 à 50 caractères)."
            if cout < 0:
                errors["cout"] = "Le coût doit être un nombre positif."

            if errors:
                form = {
                    "titre": titre,
                    "localisation": localisation,
                    "description": description,
                    "actif": str(actif),
                    "cout": request.form.get("cout", ""),
                }
                return render_template("service_edit.jinja", s=s, categories=cats, errors=errors, form=form, locale=locale), 400

            bd.update_service(conn, service_id, titre, localisation, description, actif, cout)

            flash("Service mis à jour.", "success")
            return redirect(url_for(".service_detail", service_id=service_id), code=303)

    except Exception as e:
        print(f"Erreur d'édition de service: {e}")
        flash("Erreur lors de la mise à jour du service en base de données.", "danger")
        return redirect(url_for(".edit_service", service_id=service_id))
