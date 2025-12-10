/**
 * Pour faciliter les requêtes Ajax.
 */

/* eslint-disable no-unused-vars */

/*global envoyerRequeteAjax*/

"use strict";


async function supprimerUtilisateur(id_utilisateur) {
    

    if (controleur) {
        controleur.abort();
    }

    controleur = new AbortController();

    try {
        const resultat = await envoyerRequeteAjax(
            `api/supprimer/utilisateur/${id_utilisateur}`,
            "DELETE",
            null,
            controleur
        );

        if (resultat.code === 200) {
           afficherListeUtilisateur();
        }
        controleur = null;
    } catch (err) {
        if (err.name !== "AbortError") {
            console.error("Erreur AJAX :", err);
        }
    }
}

async function afficherListeUtilisateur() {
    try {
        const resultat = await envoyerRequeteAjax(
            "compte/api/utilisateurs",
            "GET",
        );

        if (resultat.code === 200 && resultat.utilisateurs) {
            const utilisateurs = resultat.utilisateurs;
            const champRecherche = document.getElementById("recherche");
            const filtre = champRecherche ? champRecherche.value.trim().toLowerCase() : "";
            const liste = filtre.length > 3
                ? utilisateurs.filter(u => u.courriel.toLowerCase().includes(filtre))
                : utilisateurs;


            let table = document.createElement("table");
            table.className = "table table-striped table-bordered";

            let thead = document.createElement("thead");
            thead.innerHTML = `
                <tr>
                    <th>Nom</th>
                    <th>Courriel</th>
                    <th>Crédit</th>
                    <th>Supprimer</th>
                   
                </tr>
            `;
            table.appendChild(thead);

            let tbody = document.createElement("tbody");
            liste.forEach(u => {
                let tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${u.nom}</td>
                    <td>${u.courriel}</td>
                    
                    <td>${u.credit} $</td>
                    <td>
                        <button class="btn btn-sm btn-danger"
                                onclick="supprimerUtilisateur(${u.id_utilisateur})">
                            Supprimer
                        </button>
                    </td> `;
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);

            const container = document.getElementById("tableau-utilisateurs");
            container.innerHTML = ""; 
            container.appendChild(table);
        } else {
            console.warn("Aucun utilisateur trouvé.");
        }
    } catch (err) {
        console.error("Erreur lors de l'affichage des utilisateurs :", err);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const champCourriel = document.getElementById("courriel");
    const messageCourriel = document.getElementById("messageCourriel");
    const formInscription = document.getElementById("form-inscription");

    let courrielValide = false;

    if (champCourriel) {
        champCourriel.addEventListener("blur", async () => {
            const courriel = champCourriel.value.trim();
            if (courriel.length === 0) return;

            try {
                const resultat = await envoyerRequeteAjax(
                    `/compte/api/verifier_courriel?courriel=${encodeURIComponent(courriel)}`,
                    "GET"
                );

                if (resultat.existe) {
                    messageCourriel.textContent = " Ce courriel est déjà inscrit.";
                    messageCourriel.className = "mt-1 text-sm text-red-600 font-medium";
                    courrielValide = false;
                } else {
                    messageCourriel.textContent = "Ce courriel est disponible.";
                    messageCourriel.className = "mt-1 text-sm text-green-600 font-medium";
                    courrielValide = true;
                }
            } catch (err) {
                console.error("Erreur AJAX :", err);
            }
        });

        formInscription.addEventListener("submit", e => {
            if (!courrielValide) {
                e.preventDefault();
                messageCourriel.textContent = "Veuillez entrer un courriel valide et non déjà inscrit.";
                messageCourriel.className = "mt-1 text-sm text-red-600 font-medium";
            }
        });
    }
});

function initialisationUtilisateur() {
    
    if (champRecherche) {
        champRecherche.addEventListener("input", rechercherUtilisateur);
    }

    if (listeResultats && champRecherche) {
        document.addEventListener("click", (e) => {
            if (!listeResultats.contains(e.target) && e.target !== champRecherche) {
                listeResultats.classList.add("d-none");
            }
        });
    }
}

window.addEventListener("load", initialisationUtilisateur);



