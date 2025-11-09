from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import check_password_hash
import bd
from flask import Blueprint
bp = Blueprint('compte', __name__)

@bp.route("/inscription", methods=["GET", "POST"])
def inscription():
   
    return render_template("compte/inscription.jinja")

@bp.route("/connexion", methods=["GET", "POST"])
def connexion():
    """Gère la connexion de l'utilisateur."""
    
    if session.get("id_utilisateur"):
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for("service.home"))

    if request.method == "POST":
        courriel = (request.form.get("courriel") or "").strip()
        mot_de_passe = request.form.get("mot_de_passe", "") 

        with bd.creer_connexion() as conn:
            utilisateur = bd.get_utilisateur_by_courriel(conn, courriel) 
        
  
        if utilisateur and check_password_hash(utilisateur["mot_de_passe"], mot_de_passe):
           
            session.clear()
            session["id_utilisateur"] = utilisateur["id_utilisateur"]
            session["courriel"] = utilisateur["courriel"]
            session["role"] = utilisateur["role"]
            session["credit"] = utilisateur["credit"]
            
            flash(f"Connexion réussie. Bienvenue, {utilisateur['courriel']}.", "success")
            return redirect(url_for("service.home"), 302) 
        else:
            flash("Courriel ou mot de passe incorrect.", "danger")
            return render_template("connexion.jinja", form={"courriel": courriel}), 401 

  
    return render_template("connexion.jinja", form={})

@bp.route("/deconnexion")
def deconnexion():
    """Gère la déconnexion de l'utilisateur (TACHE ACCOMPLIE)."""
    session.clear() 
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("service.home"), 302)

@bp.route("/supprimer/<int:user_id>", methods=["POST"])
def supprimer_compte(user_id):
    """Suppression du compte."""
   
    id_session = session.get("id_utilisateur")
    if not id_session:
        flash("Vous devez être connecté pour effectuer cette action.", "danger")
        return redirect(url_for("compte.connexion"))
        
   
    if id_session != user_id and session.get("role") != "admin":
        abort(403)  
    try:
        with bd.creer_connexion() as conn:
            lignes_supprimees = bd.supprimer_utilisateur(conn, user_id) 
            
        if lignes_supprimees == 0:
            flash("Erreur: Compte non trouvé ou déjà supprimé.", "danger")
            return redirect(url_for("service.home"))     
        if id_session == user_id:
            session.clear()
            flash("Votre compte a été supprimé avec succès. Au revoir.", "success")
        else:
            flash(f"Le compte utilisateur ID:{user_id} a été supprimé par l'administrateur.", "success")
            
    except Exception: 
    flash("Erreur lors de la suppression du compte.", "danger")
        
    return redirect(url_for("service.home")) 


