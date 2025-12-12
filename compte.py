from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, abort, current_app as app
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


        erreurs = valider_compte(prenom, nom, courriel, mot_de_passe, confirmer_mdp)

        with bd.creer_connexion() as conn:
            if bd.verifier_utilisateur_existe(conn, courriel):
                erreurs["courriel"] = "Ce courriel est déjà utilisé."

        if erreurs:
            return render_template(
                "compte/inscription.jinja",
                titre="Créer un compte",
                erreurs=erreurs,
                compte={"prenom": prenom, "nom": nom, "courriel": courriel}
            )

        mdp_hache = hacher_mdp(mot_de_passe)


        with bd.creer_connexion() as conn:
            bd.ajout_utilisateur(conn, nom, prenom, courriel, mdp_hache)

        flash("Compte créé avec succès.", "success")
        return redirect(url_for("compte.liste_utilisateurs"))

    return render_template(
        'compte/inscription.jinja',
        titre="Créer un compte",
        compte={},
        erreurs={}
    )

@bp_compte.route("/connexion", methods=["GET", "POST"])
def connexion():
    """Gère la connexion de l'utilisateur."""
   
    if request.method == "POST":
        courriel = (request.form.get("courriel") or "").strip()
        mot_de_passe = request.form.get("mot_de_passe", "").strip() 
        mdp = hacher_mdp(mot_de_passe)
        print(mdp)
        with bd.creer_connexion() as conn:
            utilisateurs = bd.obtenir_les_utilisateurs(conn)
            utilisateurTrouve = None
            for utilisateur in utilisateurs:
                if utilisateur["courriel"] == courriel and utilisateur["mot_de_passe"] == mdp:
                    utilisateurTrouve = utilisateur
            print(utilisateurTrouve)
            if utilisateurTrouve:
                session["nom"] = utilisateurTrouve["nom"]
                session["prenom"] = utilisateurTrouve["prenom"]    
                session["id_utilisateur"] = utilisateurTrouve["id_utilisateur"]
                session["courriel"] = utilisateurTrouve["courriel"]
                session["role"] = utilisateurTrouve["role"]
                session["credit"] = utilisateurTrouve["credit"]          
                flash(f"Connexion réussie. Bienvenue, {utilisateurTrouve['courriel']}.", "success")
                app.logger.info(f"Connexion réussie de l'utilisateur :{session.get('nom')} (ID: {session.get('id_utilisateur')})")

                return redirect(url_for("home"), 302) 
            else:
                flash("Courriel ou mot de passe incorrect.", "danger")
                app.logger.warning(f"Tentative de connexion échouée (courriel={courriel})")
                return render_template("compte/connexion.jinja")
    return render_template("compte/connexion.jinja")


@bp_compte.route("/deconnexion")
def deconnexion():
    """Gère la déconnexion de l'utilisateur ."""
    app.logger.info(f"Déconnexion réussie de l'utilisateur: {session.get('nom')} (ID: {session.get('id_utilisateur')})")
    session.clear() 
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("service.home"), 302)



@bp_compte.route("/supprimer/<int:id_utilisateur>", methods=["POST"])
def supprimer_compte(id_utilisateur):
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


@bp_compte.route("/utilisateurs")
def liste_utilisateurs():
    if "id_utilisateur" not in session:
        flash("Pour accéder à cette page, veuillez vous connecter à votre compte.", "warning")
        return redirect(url_for('compte.connexion'))    
    if session.get("role") != "admin":
        abort(403)
    with bd.creer_connexion() as conn:
        utilisateurs = bd.obtenir_les_utilisateurs(conn)
    return render_template("compte/listeUtilisateur.jinja", utilisateurs=utilisateurs, titre="Utilisateurs")
