from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from utilitaires.compte.validation_compte import valider_compte

import hashlib
import bd 

bp_compte = Blueprint('compte', __name__)

def hacher_mdp(mdp_en_clair):
    """Hache un mot de passe avec SHA-512"""
    return hashlib.sha512(mdp_en_clair.encode('utf-8')).hexdigest()

@bp_compte.route('/inscription', methods=["GET", "POST"])
def inscription():

    if request.method == "POST":

        prenom = request.form.get("prenom", "").strip()
        nom = request.form.get("nom", "").strip()
        courriel = request.form.get("courriel", "").strip()   
        mot_de_passe = request.form.get("mot_de_passe", "")
        confirmer_mdp = request.form.get("confirm_mot_de_passe", "")

        erreurs = valider_compte(prenom,nom, courriel, mot_de_passe, confirmer_mdp)

        if not erreurs: 
            with bd.creer_connexion() as conn:
                if bd.verifier_utilisateur_existe(conn, courriel):
                    erreurs["courriel"] = "Ce courriel est déjà utilisé."

        if erreurs:
            return render_template(
                "compte/inscription.jinja",
                titre="Créer un compte",
                erreurs=erreurs,
                compte={"prenom": prenom, "nom": nom, "courriel": courriel}
            ),       
                    
   
        mdp_hache = hacher_mdp(mot_de_passe)

        with bd.creer_connexion() as conn:
            bd.ajout_utilisateur(
                conn, prenom,nom,courriel,mdp_hache
                )

        flash("Compte créé avec succès. Vous pouvez maintenant vous connecter.", "success")    
        return redirect(url_for("services_list"))
    
    return render_template(
        'compte/inscription.jinja',
        titre="Créer un compte",
        compte={},
        erreurs={}
    )


@bp_compte.route("/connexion", methods=["GET", "POST"])
def connexion():
    """Gère la connexion de l'utilisateur."""
    
    # if session.get("id_utilisateur"):
    #     flash("Vous êtes déjà connecté.", "info")
    #     return redirect(url_for("service.home"))

    if request.method == "POST":
        courriel = (request.form.get("courriel") or "").strip()
        mot_de_passe = request.form.get("mot_de_passe", "") 
        mdp = hacher_mdp(mot_de_passe)
        with bd.creer_connexion() as conn:
            utilisateur = bd.authentifier(conn,courriel,mdp)
            if utilisateur:
                session["nom"] = utilisateur["nom"]
                session["prenom"] = utilisateur["prenom"]    
                session["id_utilisateur"] = utilisateur["id_utilisateur"]
                session["courriel"] = utilisateur["courriel"]
                session["role"] = utilisateur["role"]
                session["credit"] = utilisateur["credit"]
            
                flash(f"Connexion réussie. Bienvenue, {utilisateur['courriel']}.", "success")
                return redirect(url_for("home"), 302) 
            else:
                flash("Courriel ou mot de passe incorrect.", "danger")
                return render_template("compte/connexion.jinja")
    return render_template("compte/connexion.jinja")

@bp_compte.route("/deconnexion")
def deconnexion():
    """Gère la déconnexion de l'utilisateur ."""
    session.clear() 
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("service.home"), 302)

@bp_compte.route("/supprimer/<int:user_id>", methods=["POST"])
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
        # if id_session == user_id:
        #     session.clear()
        #     flash("Votre compte a été supprimé avec succès. Au revoir.", "success")
        else:
            flash(f"Le compte utilisateur ID:{user_id} a été supprimé.", "success")
            
    except Exception: 
        flash("Erreur lors de la suppression du compte.", "danger")
        
    return redirect(url_for("service.home")) 

@bp_compte.route("/utilisateurs")
def liste_utilisateurs():
    if "utilisateur_id" not in session:
        flash("Pour accéder à cette page, veuillez vous connecter à votre compte.", "warning")
        return redirect(url_for('compte.connexion'))    
    if session.get("role") != 1:
        abort(403)
    with bd.creer_connexion() as conn:
        utilisateurs = bd.obtenir_les_utilisateurs(conn)
    return render_template("compte/listeUtilisateur.jinja", utilisateurs=utilisateurs, titre="Utilisateurs")