from flask import Blueprint, request, session,jsonify,current_app
from datetime import datetime

from service import bp_service
from compte import bp_compte
import bd 

bp_api = Blueprint('api', __name__)

@bp_service.route("/api/services")
def services_list_api():
    """Recherche des services par mot-clé."""

    id_current = session.get("id_utilisateur")
    role_current = session.get("role")

    q = (request.args.get("q") or "").strip().lower()
    try:
        with bd.creer_connexion() as conn:
            services = bd.search_services(conn, q=q)
            print("Nombre de services actifs récupérés :", len(services))
    except Exception as e:
         services = []
         
    for s in services:
        s["id_utilisateur_current"] = id_current
        s["role_current"] = role_current
    return jsonify(services)


    
@bp_compte.route("api/supprimer/<int:id_utilisateur>", methods=["POST"])
def supprimer_utilisateur(id_utilisateur):
    """Suppression du compte via AJAX uniquement."""
    if "id_utilisateur" not in session:
        return jsonify(code=401, message="Vous devez être connecté pour effectuer cette action.")

    if session["id_utilisateur"] != id_utilisateur and session.get("role") != "admin":
        return jsonify(code=403, message="Vous n'êtes pas autorisé à supprimer ce compte.")

    try:
        with bd.creer_connexion() as conn:
            lignes_supprimees = bd.supprimer_utilisateur(conn, id_utilisateur)

        if lignes_supprimees == 0:
            return jsonify(code=404, message="Compte non trouvé ou déjà supprimé.")

        return jsonify(code=200, message="Le compte utilisateur a été supprimé.")

    except Exception as e:
        print(f"Erreur lors de la suppression du compte : {e}")
        return jsonify(code=500, message="Erreur lors de la suppression du compte.")


@bp_compte.route("/api/utilisateurs")
def liste_utilisateurs_api():
    data ={}

    if "id_utilisateur" not in session:
        data = {
        "message": "Pour accéder à cette page, veuillez vous connecter à votre compte.", 
        "code": 401
        }   
        return jsonify(data)
    
    if session.get("role") != "admin":
        data = {
        "message": "Pour accéder à cette page, veuillez vous connecter à votre compte.", 
        "code": 404
        }  
        return jsonify(data)
    
    with bd.creer_connexion() as conn:
        utilisateurs = bd.obtenir_les_utilisateurs(conn)
        data = {
        "utilisateurs": utilisateurs, 
        "code": 200
        }  

    return jsonify(data)

@bp_compte.route("api/verifier_courriel")
def verifier_courriel():
    """vérifie si un courriel est saisi."""
    courriel = request.args.get("courriel", "").strip().lower()
    if not courriel:
        return jsonify({"existe": False})

    try:
        with bd.creer_connexion() as conn:
            utilisateur = bd.verifier_utilisateur_existe(conn, courriel)
        return jsonify({"existe": utilisateur is not None})
    except Exception as e:
        return jsonify({"existe": False, "error": str(e)})
    
@bp_service.route("/api/services/recents")
def api_services_recents():
    """Retourne la liste complète des services."""
    with bd.creer_connexion() as conn:
        services = bd.get_service_all(conn)
    return jsonify(code=200, services=services)

@bp_service.route("/api/services")
def api_services():
    """Retourne les 5 derniers services ajoutés."""
    with bd.creer_connexion() as conn:
        services = bd.get_service_all(conn)
        current_app.logger.info(f"Affichage des services dans la page d'accueil par l'utilisateur (ID= {session.get('id_utilisateur')})")


    return jsonify(code=200, services=services)

@bp_api.route("/api/reservations/disponibilite/<int:id_service>", methods=["GET"])
def api_disponibilite_reservation(id_service: int):
    """
    Vérifie si un service est disponible pour une date + heure (AJAX).
    GET ?date=YYYY-MM-DD&heure=HH:MM
    Retour: { disponible: bool, message: str }
    """
    date_str = (request.args.get("date") or "").strip()
    heure_str = (request.args.get("heure") or "").strip()

    if not date_str or not heure_str:
        return jsonify(disponible=False, message="Choisissez une date et une heure."), 200

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        heure_obj = datetime.strptime(heure_str, "%H:%M").time()
    except ValueError:
        return jsonify(disponible=False, message="Date ou heure invalide."), 200

    with bd.creer_connexion() as conn:
        service = bd.get_service_by_id(conn, id_service)
        if not service:
            return jsonify(disponible=False, message="Service introuvable."), 404

        # IMPORTANT: doit matcher ta BD (DATE + TIME)
        deja_reserve = bd.service_a_deja_ete_reserve(conn, id_service, date_obj, heure_obj)

    if deja_reserve:
        return jsonify(disponible=False, message="⛔ Déjà réservé à cette date et heure."), 200

    return jsonify(disponible=True, message="✅ Disponible."), 200
