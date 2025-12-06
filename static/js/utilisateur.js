/**
 * Pour faciliter les requêtes Ajax.
 */

/* eslint-disable no-unused-vars */


/*global envoyerRequeteAjax*/

"use strict";

async function supprimerUtilisateur(id_service) {
    if (controleur) {
        controleur.abort();
    }

    controleur = new AbortController();

    try {
        const resultat = await envoyerRequeteAjax(
            `api/supprimer/utilisateur/${id_service}`,
            "GET",
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
            utilisateurs.forEach(u => {
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


function initialisation() {
    afficherListeUtilisateur();
}

window.addEventListener("load", initialisation);
