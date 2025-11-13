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

    id_utilisateur = session["user_id"]
    locale = request.cookies.get("local", "fr_CA")

    with bd.creer_connexion() as conn:
        reservations_faites = bd.get_reservations_by_user(conn, id_utilisateur)
        reservations_recues = bd.get_reservations_for_owner(conn, id_utilisateur)

    devise = "USD" if locale == "en_US" else "CAD"

    def format_reservation(r):
        r["date_souhaitee_formattee"] = dates.format_date(r["date_souhaitee"], format="full", locale=locale)
        r["date_reservation_formattee"] = dates.format_datetime(r["date_reservation"], format="short", locale=locale)
        r["cout_paye_formatte"] = numbers.format_currency(r["cout_paye"], devise, locale=locale)
        return r

    reservations_faites = [format_reservation(r) for r in reservations_faites]
    reservations_recues = [format_reservation(r) for r in reservations_recues]

    return render_template(
        "reservation_list.jinja",
        reservations_faites=reservations_faites,
        reservations_recues=reservations_recues,
        locale=locale,
    )

@bp_reservation.route("reservation/reserver", methods=["POST"])
def reserver_service():
    """Soumettre une réservation."""
    if not session.get("id_utilisateur"):
        flash("Vous devez être connecté pour réserver un service.", "warning")
        service_id = request.form.get("id_service")
        return redirect(url_for("service.service_detail", service_id=service_id))

    id_utilisateur = session["id_utilisateur"]
    service_id = request.form.get("id_service", type=int)
    date_souhaitee_str = request.form.get("date_souhaitee")

    errors = {}

    with bd.creer_connexion() as conn:
        service = bd.get_service_by_id(conn, service_id)
        credit_utilisateur = bd.get_credit_utilisateur(conn, id_utilisateur)

    if not service:
        abort(404)

    if service["id_utilisateur"] == id_utilisateur:
        flash("Vous ne pouvez pas réserver votre propre service.", "danger")
        return redirect(url_for("service.service_detail", service_id=service_id))

    cout_service = service.get("cout") or 0.0

    try:
        date_souhaitee = datetime.strptime(date_souhaitee_str, "%Y-%m-%d").date()
        if date_souhaitee < date.today():
            errors["date_souhaitee"] = "La date souhaitée ne peut pas être dans le passé."
    except ValueError:
        errors["date_souhaitee"] = "Format de date invalide."

    if cout_service > 0 and credit_utilisateur < cout_service:
        errors["credit"] = f"Crédit insuffisant. Il vous faut {cout_service} crédits, vous avez {credit_utilisateur}."

    if errors:
        for error in errors.values():
            flash(error, "danger")
        return redirect(url_for("service.service_detail", service_id=service_id))

    try:
        with bd.creer_connexion() as conn:
            bd.ajout_reservation(conn, service_id, id_utilisateur, datetime.now(), date_souhaitee, cout_service)
    except Exception as e:
        print(f"Erreur lors de la réservation et/ou de la transaction: {e}")
        flash("Une erreur est survenue lors de la tentative de réservation.", "danger")
        return redirect(url_for("service.service_detail", service_id=service_id))

    flash(f"Réservation de '{service['titre']}' pour le {date_souhaitee_str} confirmée!", "success")
    return redirect(url_for(".liste_reservations"), code=303)
