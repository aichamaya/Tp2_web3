"use strict";

/*global envoyerRequeteAjax*/
let tousLesServices = [];
let indexAffichage = 0;
const nbInitial = 6;
const nbParScroll = 3;

let controleur = null;
const CLE_STORAGE = "tableauLocal"; 

let champRecherche = null;
let chargement = null;
let listeResultats = null;
let conteneurServices = null;
let piedPage = null;


async function chargerTousLesServices() {
    try {
        
        const liste = await envoyerRequeteAjax("/api/services", "GET");

        if (liste && liste.length > 0) {

            tousLesServices = liste;
            console.log("Nombre total de services :", tousLesServices.length);
            indexAffichage = 0;

            if (piedPage) piedPage.classList.add("d-none");
            afficherPlusDeServices(nbInitial);

            if (indexAffichage < tousLesServices.length) {
                window.addEventListener("scroll", gererDefilement);
            } else {
                if (piedPage) piedPage.classList.remove("d-none");
            }
         
        } else {
            const msg = document.getElementById("message-aucun-service");
            if (msg) msg.classList.remove("d-none");
        }


    } catch (err) {
        console.error("Erreur chargement services :", err);
    }
}

function afficherPlusDeServices(nombre) {
    if (!conteneurServices) return;

    const fin = Math.min(indexAffichage + nombre, tousLesServices.length);

    for (let i = indexAffichage; i < fin; i++) {
        const s = tousLesServices[i];

        const col = document.createElement("div");
        col.className = "col-md-4";

        const imageSrc = s.nom_image 
            ? `/static/images/ajouts/${s.nom_image}` 
            : "/static/images/default_service.png";

        col.innerHTML = `
            <div class="card h-100 shadow-sm border-0" data-id-service="${s.id_service}">
                <a href="/services/${s.id_service}">
                    <img class="card-img-top object-fit-cover rounded-top" style="height: 200px;"
                        src="${imageSrc}" alt="${s.titre}"
                        onerror="this.src='/static/images/default_service.png'">
                </a>
                <div class="card-body">
                    <h5 class="card-title mb-2 fw-semibold">${s.titre}</h5>
                    <p class="small text-muted mb-3">
                        <i class="bi bi-tag"></i> ${s.nom_categorie} • 
                        <i class="bi bi-geo-alt"></i> ${s.localisation}
                    </p>
                    <div class="d-grid gap-2">
                        <a href="/services/${s.id_service}" class="btn btn-outline-primary w-100">Voir détails</a>
                        ${
                            (s.id_utilisateur_current === s.id_utilisateur || s.role_current === "admin")
                                ? `<a href="/services/${s.id_service}/edit" class="btn btn-outline-secondary w-100">Modifier</a>
                                   <button class="btn btn-outline-danger w-100" onclick="supprimerService(${s.id_service})">Supprimer</button>`
                                : (s.actif ? `<a href="/reservation/formulaire/${s.id_service}" class="btn btn-outline-success w-100">Réserver</a>` : "")
                        }
                    </div>
                </div>
            </div>
        `;

        conteneurServices.appendChild(col);
    }

    indexAffichage = fin;
}


async function supprimerService(id_service) {
    if (!confirm("Voulez-vous vraiment supprimer ce service ?")) return;

    try {
        const response = await fetch(`/api/supprimer/service/${id_service}`, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
            
        });

        let data = {};
        try {
            data = await response.json();
        } catch {
            data = { code: response.ok ? 200 : 500, message: "Réponse invalide du serveur." };
        }

        if (data.code === 200) {

            const card = document.querySelector(`.card[data-id-service='${id_service}']`);
            if (card) {
                const col = card.closest(".col-md-4");
                if (col) col.remove();
            }

            alert(data.message || "Service supprimé !");
        } else {
            alert(data.message || "Erreur lors de la suppression du service.");
        }

    } catch (err) {
        console.error("Erreur lors de la suppression :", err);
        alert("Erreur lors de la suppression du service.");
    }
}



function gererDefilement() {
    console.log("gererDefilement appelé");
    if ((window.innerHeight + window.scrollY) >= 0.95 * document.body.offsetHeight) {
        // Ajoute 3 services de plus
        afficherPlusDeServices(nbParScroll);
    }

    // Si tous les services sont affichés, on enlève l'événement scroll
    if (indexAffichage >= tousLesServices.length) {
        if (piedPage) piedPage.classList.remove("d-none");
        window.removeEventListener("scroll", gererDefilement);
    }
  
}

/**
 * Récupère tableauLocal et retourne un json (tableau d'objets JS)
 * Utilise JSON.parse
 */
function getTableauFromLocalStorage() {
    const data = localStorage.getItem(CLE_STORAGE);
   
    return data ? JSON.parse(data) : [];
}

/**
 * Ajoute un mot clé au tableauLocal
 * - Récupère le tableau actuel
 * - Ajoute le nouvel élément (push)
 * - Sauvegarde avec setItem et JSON.stringify
 */
function ajouterElementAuTableau(motCle) {
    if (!motCle) return;

    let tableau = getTableauFromLocalStorage();

    if (!tableau.includes(motCle)) {
        tableau.push(motCle);
        
        localStorage.setItem(CLE_STORAGE, JSON.stringify(tableau));
    }
}

/**
 * Récupère les valeurs et les ajoute dans un div (ul) comme éléments li.
 * Implémente un évènement click pour afficher la suggestion sélectionnée.
 */
function afficherLocalStorage() {
    if(!listeResultats) return;
    listeResultats.innerHTML = "";
    
    const tableau = getTableauFromLocalStorage();

    if (tableau.length === 0) {
        listeResultats.classList.add("d-none");
        return;
    }

    
    tableau.forEach(mot => {
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-action list-group-item-secondary"; 
        li.textContent = mot;
        li.style.cursor = "pointer";

        
        li.addEventListener("click", () => {
            
            champRecherche.value = mot;
            rechercher();
        
        });

        listeResultats.appendChild(li);
    });

    listeResultats.classList.remove("d-none");
}



async function rechercher() {
    if (!champRecherche || !listeResultats || !chargement) return;

    const aChercher = champRecherche.value.trim();


    if (aChercher === "") {
        if (controleur) controleur.abort();
        chargement.classList.add("d-none");

        afficherLocalStorage(); 
        return;
    }

    if (aChercher.length < 3) {
        listeResultats.classList.add("d-none");
        return; 
    }

    chargement.classList.remove("d-none");

    if (controleur) {
        controleur.abort();
    }
    controleur = new AbortController();

    try {
        const resultats = await envoyerRequeteAjax(
            "/api/services",
            "GET",
            { q: aChercher },
            controleur
        );

        afficherResultats(resultats);
        chargement.classList.add("d-none");
        controleur = null;

    } catch (err) {
        if (err.name !== "AbortError") {
            console.error("Erreur AJAX :", err);
            listeResultats.classList.add("d-none");
            chargement.classList.add("d-none");
        }
    }
}

function afficherResultats(resultats) {
    if (!listeResultats) return; 

    listeResultats.innerHTML = "";

    if (!resultats || resultats.length === 0) {
        listeResultats.classList.add("d-none");
        return;
    }

    for (const service of resultats) {
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-action";
        li.textContent = service.titre;
        li.style.cursor = "pointer";
        
        li.addEventListener("click", () => {
            
            ajouterElementAuTableau(service.titre);
                     
            window.location.href = `/services/${service.id_service}`;
        });
        
        listeResultats.appendChild(li);
    }

    listeResultats.classList.remove("d-none");
}

function initialisation() {

    conteneurServices = document.getElementById("liste-services");
    piedPage = document.getElementById("pied-page-services");   
    champRecherche = document.getElementById("recherche");
    chargement = document.getElementById("chargement");
    listeResultats = document.getElementById("resultats-recherche");

    if (piedPage) piedPage.className = "d-none";


    if (conteneurServices) {
        chargerTousLesServices();
    }
  
    if (champRecherche) {

        champRecherche.addEventListener("input", rechercher);
        champRecherche.addEventListener("focus", () => {
  
            if (champRecherche.value.trim() === "") {
                afficherLocalStorage();
            }
        });
    }

   
    if (listeResultats && champRecherche) {
        document.addEventListener("click", (e) => {
            if (!listeResultats.contains(e.target) && e.target !== champRecherche) {
                listeResultats.classList.add("d-none");
            }
        });
    }

}

window.addEventListener("load", initialisation);