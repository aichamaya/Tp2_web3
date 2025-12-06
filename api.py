from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort,jsonify

from service import bp_service
from compte import bp_compte
import bd 

bp_api = Blueprint('api', __name__)

@bp_service.route("api/services")
def services_list_api():
    """Liste des services avec filtres."""
    q = (request.args.get("q") or "").strip().lower()
    try:
        with bd.creer_connexion() as conn:
            rows = bd.search_services(conn, q=q)
    except Exception as e:
         rows = []

    return jsonify(rows)

@bp_service.route("api/supprimer/service/<int:id_service>")
def supprimer_service_api(id_service):
    """Supprime un service si l'utilisateur est admin ou le créateur."""
    data ={}
    
    if "id_utilisateur" not in session:
        data = {
            "message": "Vous devez être connecté pour supprimer un service.",
            "code": 401
        }
        return  jsonify(data)   
    try:
        with bd.creer_connexion() as conn:
            s = bd.get_service_by_id(conn, id_service)
            if not s:
                data = {
                "message": "service inexistant",
                "code": 404
                }
                return jsonify(data)
              
            
            # Vérifie si l'utilisateur est admin ou propriétaire
            if not session.get('est_admin', False) and s["id_utilisateur"] != session["id_utilisateur"]:
                data = {
                    "message": "Vous n'êtes pas autorisé à supprimer ce service.",
                    "code": 404
                }
                return jsonify(data)
              
        ligne_affectee = bd.supprimer_service(conn, id_service) 

        if ligne_affectee == 1:
            data = {
                    "message": "Le service a été supprimé !",
                    "code": 200
            }
            return jsonify(data)
    except Exception as e:
        data = {
        "message": str(e), 
        "code": 500
        }
        return jsonify(data)

@bp_compte.route("api/supprimer/utilisateur/<int:id_utilisateur>")
def supprimer_compte_api(id_utilisateur):
    """Suppression du compte."""
    data ={}
    id_session = session.get("id_utilisateur")
    if not id_session:
        data = {
            "message": "Vus devez être connecté pour effectuer cette action.",
            "code": 401
        }
        return  jsonify(data)  
        
    if id_session != id_utilisateur and session.get("role") != "admin":
        data = {
        "message": "Pour accéder à cette page, veuillez vous connecter à votre compte.", 
        "code": 404
        }  
        return jsonify(data)
    try:
        with bd.creer_connexion() as conn:
            lignes_supprimees = bd.supprimer_utilisateur(conn, id_utilisateur) 
            
        if lignes_supprimees == 0:
            data = {
                "message": "Erreur: Compte non trouvé ou déjà supprimé.",
                "code": 401
            }
            return  jsonify(data)     
        else:
            data = {
                "message": "Le compte utilisateur a été supprimé.",
                "code": 200
            }
            return  jsonify(data) 
            
    except Exception: 
        data = {
                "message": "Erreur lors de la suppression du compte.",
                "code": 401
            }
        return  jsonify(data) 


@bp_compte.route("compte/api/utilisateurs")
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