from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from datetime import datetime, date
from babel import dates, numbers
import bd
bp_reservation = Blueprint("reservation", __name__) 

@bp_reservation.route("reservation/", methods=["GET"])
def liste_reservations():
    """Affiche les réservations faites et reçues."""
    if not session:
        flash("Vous devez être connecté pour voir vos réservations.", "warning")
        return redirect(url_for("compte.connexion"))

    id_utilisateur = session["id_utilisateur"]
    locale = request.cookies.get("local", "fr_CA")

    with bd.creer_connexion() as conn:
        reservations_faites = bd.get_reservations_by_user(conn, id_utilisateur)
        reservations_recues = bd.get_reservations_for_owner(conn, id_utilisateur)

    devise = "USD" if locale == "en_US" else "CAD"

    return render_template(
        "reservation_list.jinja",
        reservations_faites=reservations_faites,
        reservations_recues=reservations_recues,
        locale=locale,
    )

@bp_reservation.route("reservation/<int:id_service>", methods=["POST"])
def reserver_service(id_service):
    """Soumettre une réservation."""
    if not session.get("id_utilisateur"):
        flash("Vous devez être connecté pour réserver un service.", "warning")
        abort(401)
    id_utilisateur = session["id_utilisateur"]
    date_choisir =""
    heure_choisir=""

    errors = {}
    date_choisir = request.form.get("date")
    heure_choisir = request.form.get("heure")
    with bd.creer_connexion() as conn:
        s= bd.get_service_by_id(conn, id_service)
        credit_utilisateur = bd.get_credit_utilisateur(conn, id_utilisateur)
        if bd.service_a_deja_ete_reserve(conn,id_service, date_choisir,heure_choisir):
            flash("Desolée ce service est déja reservé pour cette date")
            return render_template("services/reservation.jinja", date_choisir=date_choisir, heure_choisir=heure_choisir, s=s)
        

    if not s:
        abort(404)
    if s["id_utilisateur"] == id_utilisateur:
        flash("Vous ne pouvez pas réserver votre propre service.", "danger")
        return redirect(url_for("service.service_detail", service_id=id_service))

    cout_service = s.get("cout") or 0.0
    if not heure_choisir  :
        errors["heure_choisir"] ="veuillez choisir une heure svp"
    if not date_choisir :
        errors["date_choisir"] = "Veuillez choisir uen date svp"

    if cout_service > 0 and credit_utilisateur < cout_service:
        errors["credit"] = f"Crédit insuffisant. Il vous faut {cout_service} crédits, vous avez {credit_utilisateur}."

    if errors:
        for error in errors.values():
            flash(error, "danger")
        return redirect(url_for("service.service_detail", service_id=id_service))

    try:
        with bd.creer_connexion() as conn:
            bd.ajout_reservation(conn, id_service, id_utilisateur,  date_choisir, heure_choisir, cout_service)
    except Exception as e:
        print(f"Erreur lors de la réservation et/ou de la transaction: {e}")
        flash("Une erreur est survenue lors de la tentative de réservation.", "danger")
        return redirect(url_for("service.service_detail", service_id=id_service))

    flash(f"Réservation de '{s['titre']}' pour le {date_choisir} confirmée!", "success")
    return redirect(url_for(".liste_reservations"), code=303)

@bp_reservation.route("reservation/<int:id_service>")
def formulaire_reservation(id_service):
    """formulaire de modifiction"""
    # try:
    with bd.creer_connexion() as conn:
            s =bd.get_service_by_id(conn,id_service)
            if not s:
                abort(404)
    return render_template("services/reservation.jinja", s=s) 
    # except Exception as e:
        # abort(500)
