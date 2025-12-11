"use strict";

/*global envoyerRequeteAjax*/

let tousLesServices = [];
let indexAffichage = 0;
const nbInitial = 6;
const nbParScroll = 3;

async function chargerServicesRecents() {
    try {
        const container = document.getElementById("services-recents");
        if (!container) return;

        const resultat = await envoyerRequeteAjax("/api/services/recents", "GET");

        if (resultat.code === 200 && resultat.services) {
            container.innerHTML = "";  

            resultat.services.forEach(s => {
                const div = document.createElement("div");
                div.className = "col-md-4";
                div.innerHTML = `
                    <div class="card h-100" data-id-service="${s.id_service}">
                        ${s.nom_image ? `<img class="card-img-top object-fit-cover" style="height: 200px;" src="/static/images/ajouts/${s.nom_image}" alt="${s.titre}">` : ""}
                        <div class="card-body">
                            <h5 class="card-title mb-1">${s.titre}</h5>
                            <div class="small text-muted">${s.nom_categorie} • ${s.localisation}</div>
                        </div>
                        <a class="btn btn-primary" href="/services/${s.id_service}">Détail</a>
                    </div>
                `;
                container.appendChild(div);
            });
        }
    } catch (err) {
        console.error("Erreur chargement services récents :", err);
    }
}

function rafraichirServicesRecents() {

    setInterval(() => {
        chargerServicesRecents();
    }, 5000);
}

async function chargerTousLesServices() {
    try {
        const resultat = await envoyerRequeteAjax("/api/services", "GET");
        if (resultat.code === 200 && resultat.services) {
            tousLesServices = resultat.services;
            afficherPlusDeServices(nbInitial);
        }
    } catch (err) {
        console.error("Erreur chargement tous les services :", err);
    }
}

function afficherPlusDeServices(nombre = nbParScroll) {
    const container = document.getElementById("liste-services");
    if (!container) return;

    const fin = Math.min(indexAffichage + nombre, tousLesServices.length);

    for (let i = indexAffichage; i < fin; i++) {
        const s = tousLesServices[i];
        const div = document.createElement("div");
        div.className = "col-md-4";
        div.innerHTML = `
            <div class="card h-100">
                ${s.nom_image ? `<img class="card-img-top object-fit-cover" style="height: 200px;" src="/static/images/ajouts/${s.nom_image}" alt="${s.titre}">` : ""}
                <div class="card-body">
                    <h5 class="card-title mb-1">${s.titre}</h5>
                    <div class="small text-muted">${s.nom_categorie} • ${s.localisation}</div>
                </div>
                <a class="btn btn-primary" href="/services/${s.id_service}">Détail</a>
            </div>
        `;
        container.appendChild(div);
    }

    indexAffichage = fin;

    if (indexAffichage >= tousLesServices.length) {
        window.removeEventListener("scroll", scrollHandler);
        const msg = document.createElement("p");
        msg.className = "text-muted text-center mt-3";
        msg.textContent = "Tous les services sont affichés.";
        container.appendChild(msg);
    }
}

function scrollHandler() {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
        afficherPlusDeServices();
    }
}

function initialisation() {

    chargerServicesRecents();
    chargerTousLesServices();
    rafraichirServicesRecents();
    
    window.addEventListener("scroll", scrollHandler);
    
}

window.addEventListener("load", initialisation);