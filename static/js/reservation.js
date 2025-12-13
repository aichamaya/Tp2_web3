"use strict";
/*global envoyerRequeteAjax*/

let controleurDispo = null;
let timer = null;

function setEtat(btn, feedback, etat, message) {
  // etat: "neutre" | "ok" | "ko" | "loading"
  if (!btn || !feedback) return;

  // Bouton
  btn.disabled = (etat !== "ok");

  // Texte
  feedback.textContent = message || "";

  // Classes
  feedback.classList.remove("text-success", "text-danger", "text-muted");
  feedback.classList.add("text-muted"); // défaut

  if (etat === "ok") feedback.classList.replace("text-muted", "text-success");
  if (etat === "ko") feedback.classList.replace("text-muted", "text-danger");
  if (etat === "loading") feedback.classList.replace("text-muted", "text-muted");
}

async function verifierDisponibilite(idService) {
  const inputDate = document.getElementById("date");
  const inputHeure = document.getElementById("heure");
  const btn = document.getElementById("btnReserver");
  const feedback = document.getElementById("dispoFeedback");

  if (!inputDate || !inputHeure || !btn || !feedback) return;

  const date = inputDate.value.trim();
  const heure = inputHeure.value.trim();

  // Pas assez d'infos
  if (!date || !heure) {
    if (controleurDispo) controleurDispo.abort();
    setEtat(btn, feedback, "neutre", "Choisissez une date et une heure.");
    return;
  }

  // Annule la requête précédente
  if (controleurDispo) controleurDispo.abort();
  controleurDispo = new AbortController();

  setEtat(btn, feedback, "loading", "Vérification en cours...");

  try {
    const res = await envoyerRequeteAjax(
      `/api/reservations/disponibilite/${idService}`,
      "GET",
      { date, heure },
      controleurDispo
    );

    // Sécurité: si le serveur renvoie un format inattendu
    if (!res || typeof res.disponible !== "boolean") {
      setEtat(btn, feedback, "ko", "Réponse serveur invalide (pas du JSON).");
      return;
    }

    if (res.disponible) {
      setEtat(btn, feedback, "ok", res.message || "Disponible ✅");
    } else {
      setEtat(btn, feedback, "ko", res.message || "Indisponible ❌");
    }

  } catch (err) {
    // Une annulation n'est pas une vraie erreur
    if (err && err.name === "AbortError") return;

    setEtat(btn, feedback, "ko", "Erreur de vérification. Réessayez.");
    console.error(err);
  } finally {
    controleurDispo = null;
  }
}

function initReservationCheck() {
  const form = document.getElementById("formReservation");
  if (!form) return;

  const idService = form.dataset.idService;
  if (!idService) return;

  const inputDate = document.getElementById("date");
  const inputHeure = document.getElementById("heure");
  const btn = document.getElementById("btnReserver");
  const feedback = document.getElementById("dispoFeedback");

  if (!inputDate || !inputHeure || !btn || !feedback) return;

  const handler = () => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => verifierDisponibilite(idService), 250);
  };

  inputDate.addEventListener("input", handler);
  inputHeure.addEventListener("input", handler);

  // État initial
  setEtat(btn, feedback, "neutre", "Choisissez une date et une heure.");
}

window.addEventListener("load", initReservationCheck);
