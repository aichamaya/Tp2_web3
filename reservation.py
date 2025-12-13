from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, current_app as app
from datetime import datetime
import bd

bp_reservation = Blueprint("reservation", __name__)


@bp_reservation.route("/mes_reservations", methods=["GET"])
def liste_reservations():
    if not session.get("id_utilisateur"):
        flash("Vous devez être connecté pour voir vos réservations.", "warning")
        return redirect(url_for("compte.connexion"))

    id_utilisateur = session["id_utilisateur"]

    with bd.creer_connexion() as conn:
        reservations_faites = bd.get_reservations_by_user(conn, id_utilisateur)
        reservations_recues = bd.get_reservations_for_owner(conn, id_utilisateur)

    return render_template(
        "reservation_list.jinja",
        reservations_faites=reservations_faites,
        reservations_recues=reservations_recues
    )


@bp_reservation.route("/formulaire/<int:id_service>", methods=["GET"])
def formulaire_reservation(id_service):
    if not session.get("id_utilisateur"):
        flash("Vous devez être connecté pour réserver un service.", "warning")
        return redirect(url_for("compte.connexion"))

    with bd.creer_connexion() as conn:
        s = bd.get_service_by_id(conn, id_service)
        if not s:
            abort(404)

    return render_template("services/reservation.jinja", s=s)


@bp_reservation.route("/<int:id_service>", methods=["POST"])
def reserver_service(id_service):
    if not session.get("id_utilisateur"):
        flash("Vous devez être connecté pour réserver un service.", "warning")
        return redirect(url_for("compte.connexion"))

    id_utilisateur = session["id_utilisateur"]

    date_choisie = (request.form.get("date") or "").strip()
    heure_choisie = (request.form.get("heure") or "").strip()

    try:
        date_obj = datetime.strptime(date_choisie, "%Y-%m-%d").date()
        heure_obj = datetime.strptime(heure_choisie, "%H:%M").time()
    except Exception:
        flash("Date ou heure invalide.", "danger")
        return redirect(url_for("reservation.formulaire_reservation", id_service=id_service))

    
    date_reservation = date_obj.strftime("%Y-%m-%d")      
    date_souhaitee = heure_obj.strftime("%H:%M:%S")      

    with bd.creer_connexion() as conn:
        service = bd.get_service_by_id(conn, id_service)
        if not service:
            abort(404)

        if service["id_utilisateur"] == id_utilisateur:
            flash("Vous ne pouvez pas réserver votre propre service.", "danger")
            return redirect(url_for("service.service_detail", service_id=id_service))

        if bd.service_a_deja_ete_reserve(conn, id_service, date_reservation, date_souhaitee):
            flash("Ce service est déjà réservé à cette date et heure.", "warning")
            return redirect(url_for("reservation.formulaire_reservation", id_service=id_service))

        cout = service.get("cout") or 0
        credit = bd.get_credit_utilisateur(conn, id_utilisateur)
        if cout > 0 and credit < cout:
            flash(f"Crédit insuffisant. Il faut {cout} crédits, vous avez {credit}.", "danger")
            return redirect(url_for("reservation.formulaire_reservation", id_service=id_service))

        try:
            bd.ajout_reservation(conn, id_service, id_utilisateur, date_reservation, date_souhaitee)
        except Exception as e:
            app.logger.error(f"Erreur réservation : {e}")
            flash("Une erreur est survenue lors de la réservation.", "danger")
            return redirect(url_for("reservation.formulaire_reservation", id_service=id_service))

    flash("Réservation confirmée !", "success")
    return redirect(url_for("reservation.liste_reservations"), code=303)
