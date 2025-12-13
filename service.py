import re
from flask import Blueprint, render_template, request, redirect, abort, flash, current_app, session, url_for,current_app as app, jsonify
from babel import numbers, dates
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
import bd

bp_service = Blueprint("service", __name__)

REGEXE_CHAMPS_HTML = re.compile(r"<(.*)>.*?|<(.*) />")

@bp_service.route("/")
def home():
    """Page d'accueil affichant les derniers services."""
    locale = request.cookies.get("local", "fr_CA")
    try:
        with bd.creer_connexion() as conn:
            services = bd.get_service_all(conn)
            if not services:
             abort(400)
        return render_template("services/home.jinja", services=services, locale=locale)
    except Exception :
        abort(500)
    return render_template("services/home.jinja", services=[], locale=locale)

@bp_service.route("/services")
def services_list():
    """Liste des services avec filtres."""
    locale = request.cookies.get("local", "fr_CA")
    q = (request.args.get("q") or "").strip()

    try:
        with bd.creer_connexion() as conn:
    
            rows = bd.search_services(conn, q=q)
    except Exception as e:
        flash(f"Erreur de base de données lors de la recherche: {e}", "danger")
        rows = []

    return render_template("services/service_list.jinja", services=rows)

@bp_service.route("/<int:id_service>/supprimer", methods=["POST"])
def supprimer_service(id_service):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if "id_utilisateur" not in session:
        if is_ajax:
            return jsonify(code=401, message="Vous devez être connecté pour supprimer ce service.")
        else:
            flash("Vous devez être connecté pour supprimer ce service.", "warning")
            return redirect(url_for('compte.connexion'))

    try:
        with bd.creer_connexion() as conn:
            s = bd.get_service_by_id(conn, id_service)
            if not s:
                if is_ajax:
                    return jsonify(code=404, message="Service inexistant.")
                else:
                    abort(404)

            if not session["role"] == "admin" and s["id_utilisateur"] != session["id_utilisateur"]:
                if is_ajax:
                    return jsonify(code=403, message="Vous n'êtes pas autorisé à supprimer ce service.")
                else:
                    flash("Vous n'êtes pas autorisé à supprimer ce service.", "danger")
                    return redirect(url_for('service.services_list'))

            bd.supprimer_service(conn, id_service)

        if is_ajax:
            app.logger.info(f"Suppression service ID={id_service} par utilisateur={session['id_utilisateur']}")
            return jsonify(code=200, message="Le service a été supprimé !")
        else:
            flash("Le service a été supprimé !", "success")
            return redirect(url_for('service.services_list'))

    except Exception as e:
        print(f"Erreur lors de la suppression du service : {e}")
        if is_ajax:
            return jsonify(code=500, message="Erreur lors de la suppression du service.")
        else:
            flash("Erreur lors de la suppression du service.", "danger")
            return redirect(url_for('service.services_list'))

 
@bp_service.route("/services/<int:service_id>")
def service_detail(service_id):
    """Détail d'un service."""
    locale = request.cookies.get("local", "fr_CA")
    devise = "USD" if locale == "en_US" else "CAD"
    s = {}
    try:
        with bd.creer_connexion() as conn:
            s = bd.get_service_by_id(conn, service_id)
    except Exception:
        abort(500)
    if not s:
        abort(404)

    s["date_creation_formattee"] = dates.format_date(s["date_creation"], locale=locale)
    s["cout_formatte"] = numbers.format_currency(s["cout"], devise, locale=locale)
    return render_template("services/service_detail.jinja", s=s, locale=locale)

@bp_service.route("/publish", methods=["GET", "POST"])
def publish():
    """Ajout d'un service ."""
 
    image_nom= ""
    id_proprietaire = session["id_utilisateur"]
    locale = request.cookies.get("local", "fr_CA")

    if request.method == "GET":
        with bd.creer_connexion() as conn:
            cats = bd.get_categories(conn)
        return render_template("services/service_form.jinja", categories=cats, errors={}, form={}, locale=locale)

    # Traitement du formulaire POST
    titre = (request.form.get("titre") or "").strip()
    localisation = (request.form.get("localisation") or "").strip()
    description = (request.form.get("description") or "").strip()
    id_categorie = request.form.get("id_categorie", type=int)
    actif = 1 if (request.form.get("actif") or "1") == "1" else 0
    photo = request.files.get('photo')

    try:
        cout = float(request.form.get("cout") or 0)
    except ValueError:
        cout = -1

    errors = {}
    if not (1 <= len(titre) <= 50):
        errors["titre"] = "Le titre est obligatoire (1 à 50 caractères)."
    if cout < 0:
        errors["cout"] = "Le coût doit être un nombre positif."
    if photo and photo.filename != "":
        if not photo.content_type.startswith('image/'):
            errors["nom_image"] = "Veuillez selectionner une image"
        else :
            image_nom = enregistrer_image(photo)


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
            'photo': image_nom
        }
        return render_template("service_form.jinja", categories=cats, errors=errors, form=form, locale=locale), 400

    try:
        with bd.creer_connexion() as conn:
            new_id = bd.ajout_service(conn, id_categorie, titre, description, localisation, actif, cout, id_proprietaire,image_nom)
    except Exception as e:
        print(f"Erreur lors de l'ajout de service: {e}")
        flash("Erreur lors de l'ajout du service en base de données.", "danger")
        return redirect(url_for(".publish"))

    flash("Service ajouté avec succès.", "success")
    app.logger.info(f"Ajout service ID={new_id} par utilisateur={session['id_utilisateur']}")
    
    return redirect(url_for(".service_detail", service_id=new_id), code=303)

@bp_service.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
def edit_service(service_id):
    """Édition d'un service ."""
    if "id_utilisateur" not in session:
        flash("Vous devez être connecté pour modifier un service.", "warning")
        return redirect(url_for("compte.connexion"))

  
    locale = request.cookies.get("local", "fr_CA")
    s ={}
    cats = {}
    form ={}
    errors = {}
    try:
        with bd.creer_connexion() as conn:
            s = bd.get_service_by_id(conn, service_id)
            if not s:
                abort(404)

            if s["id_utilisateur"] != session.get("id_utilisateur"):
                flash("Seul le propriétaire peut modifier ce service.", "danger")
                abort(403)
                
            cats = bd.get_categories(conn)

            if request.method == "GET":
                form_data = {
                    "titre": s["titre"],
                    "localisation": s["localisation"],
                    "description": s["description"],
                    "actif": str(s["actif"]),
                    "cout": s["cout"],
                    "photo" : s["nom_image"]
                }
                return render_template("services/service_edit.jinja", s=s, categories=cats, errors={}, form=form_data, locale=locale)

            # Traitement du formulaire POST
            titre = (request.form.get("titre") or "").strip()
            localisation = (request.form.get("localisation") or "").strip()
            description = (request.form.get("description") or "").strip()
            photo = (request.files.get("photo"))
            actif = 1 if (request.form.get("actif") or "1") == "1" else 0
            ancien_photo = (request.form.get("ancien_photo"))
            image_nom =""
            
            try:
                cout = float(request.form.get("cout") or 0)
            except ValueError:
                cout = -1
            if not (1 <= len(titre) <= 50):
                errors["titre"] = "Le titre est obligatoire (1 à 50 caractères)."
            if cout < 0:
                errors["cout"] = "Le coût doit être un nombre positif."
            image_nom = ancien_photo
            if photo and photo.filename != "":
                image_nom = enregistrer_image(photo)

            if errors:
                form = {
                    "titre": titre,
                    "localisation": localisation,
                    "description": description,
                    "actif": str(actif),
                    "cout": request.form.get("cout", ""),
                    "photo" : image_nom
                }
                return render_template("services/service_edit.jinja", s=s, categories=cats, errors=errors, form=form, locale=locale), 400

            bd.update_service_with_image(conn, service_id, titre, localisation, description, actif, cout,image_nom)

            app.logger.info(f"Modification service ID={service_id} par utilisateur={session['id_utilisateur']}")
            flash("Service mis à jour.", "success")
            return redirect(url_for("service.service_detail", service_id=service_id), code=303)

    except Exception as e:
        print(f"Erreur d'édition de service: {e}")
        flash("Erreur lors de la mise à jour du service en base de données.", "danger")
        return render_template("services/service_edit.jinja", s=s, categories=cats, errors=errors, form=form, locale=locale)

    
def enregistrer_image(photo):
    """Permet d'enregistrer l'image."""
    extension_image = os.path.splitext(photo.filename)[1]
    nom_image = datetime.now().strftime("%Y%m%d_%H%M%S")+extension_image
    chemin_complet = os.path.join(app.config['CHEMIN_VERS_AJOUTS'], nom_image)
    photo.save(chemin_complet)
    return nom_image
