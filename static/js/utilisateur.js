"use strict";

/*global envoyerRequeteAjax*/


let tousLesUtilisateurs = [];   
let utilisateursFiltres = [];      
          
const CLE_STORAGE = "historique_utilisateurs";

let champRecherche = null;
let conteneurTableau = null;
let listeSuggestions = null;


/**
 * Charge TOUS les utilisateurs au démarrage
 */
async function chargerUtilisateurs() {
    try {
        const resultat = await envoyerRequeteAjax("/compte/api/utilisateurs", "GET");

        if (resultat.code === 200 && resultat.utilisateurs) {
            tousLesUtilisateurs = resultat.utilisateurs;
            utilisateursFiltres = tousLesUtilisateurs; 
            console.log(tousLesUtilisateurs)
            construireTableStructure();        

            afficherUtilisateurs();
 
        } else {
            conteneurTableau.innerHTML = "<div class='alert alert-warning'>Aucun utilisateur trouvé.</div>";
        }
    } catch (err) {
        console.error("Erreur chargement utilisateurs :", err);
        conteneurTableau.innerHTML = "<div class='alert alert-danger'>Erreur de chargement.</div>";
    }
}

async function supprimerUtilisateur(id_utilisateur) {
    if (!confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) return;

    try {
        const resultat = await envoyerRequeteAjax(
            `/api/supprimer/utilisateur/${id_utilisateur}`,
            "DELETE"
        );

        if (resultat.code === 200) {         
            location.reload(); 
        }
    } catch (err) {
        console.error("Erreur suppression :", err);
    }
}


function construireTableStructure() {
    conteneurTableau.innerHTML = ""; 

    const table = document.createElement("table");
    table.className = "table table-striped table-bordered";
    table.innerHTML = `
        <thead>
            <tr>
                <th>Nom</th>
                <th>Courriel</th>
                <th>Crédit</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody id="corps-table-utilisateurs">
            
        </tbody>
    `;
    conteneurTableau.appendChild(table);
}

function afficherUtilisateurs() {

    const tbody = document.getElementById("corps-table-utilisateurs");
    if (!tbody) return;

    tbody.innerHTML = "";

    utilisateursFiltres.forEach(u => {
        const tr = document.createElement("tr");
        tr.dataset.idUtilisateur = u.id_utilisateur;
        tr.innerHTML = `
            <td>${u.nom}</td>
            <td>${u.courriel}</td>
            <td>${u.credit} $</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="supprimerUtilisateur(${u.id_utilisateur})">
                    Supprimer
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function supprimerUtilisateur(id_utilisateur) {
    if (!confirm("Voulez-vous vraiment supprimer ce compte ?")) return;

    try {
        const response = await fetch(`/compte/api/supprimer/${id_utilisateur}`, {
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
            const ligne = document.querySelector(`tr[data-id-utilisateur='${id_utilisateur}']`);
            if (ligne) ligne.remove();

            alert(data.message || "Compte supprimé !");
        } else {
            alert(data.message || "Erreur lors de la suppression du compte.");
        }

    } catch (err) {
        console.error("Erreur lors de la suppression :", err);
        alert("Erreur lors de la suppression du compte.");
    }
}



function getHistorique() {
    return JSON.parse(localStorage.getItem(CLE_STORAGE)) || [];
}

function ajouterAuHistorique(terme) {
    if (!terme) return;
    let historique = getHistorique();
    if (!historique.includes(terme)) {
        historique.push(terme);
        localStorage.setItem(CLE_STORAGE, JSON.stringify(historique));
    }
}

function afficherHistorique() {
    if (!listeSuggestions) return;
    listeSuggestions.innerHTML = "";
    
    const historique = getHistorique();
    if (historique.length === 0) {
        listeSuggestions.classList.add("d-none");
        return;
    }

    historique.forEach(email => {
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-action list-group-item-light";
        li.textContent = email;
        li.style.cursor = "pointer";
        li.addEventListener("click", () => {
            champRecherche.value = email;
            filtrerTableau(email); 
        });
        listeSuggestions.appendChild(li);
    });
    listeSuggestions.classList.remove("d-none");
}

/**
 * Filtre le tableau principal selon le texte entré
 */
function filtrerTableau(texte) {
    
    if (texte.length > 3) {
        ajouterAuHistorique(texte);
    }
    
    if (texte === "") {
        utilisateursFiltres = tousLesUtilisateurs; 
    } else {
        utilisateursFiltres = tousLesUtilisateurs.filter(u => 
            u.courriel.toLowerCase().includes(texte.toLowerCase())
        );
    }

  
    afficherUtilisateurs(); 

    if (listeSuggestions) listeSuggestions.classList.add("d-none");
}


function initialisationUtilisateur() {
    conteneurTableau = document.getElementById("tableau-utilisateurs");
    champRecherche = document.getElementById("recherche");
    listeSuggestions = document.getElementById("resultats-recherche-utilisateurs");

    if (!conteneurTableau) {
        return; 
    }
    
    chargerUtilisateurs();

    if (champRecherche) {
        
        champRecherche.addEventListener("input", () => {
            const val = champRecherche.value.trim();
            
            if (val === "") {
                filtrerTableau(""); 
                
            }
            else if (val.length > 3) {
                afficherSuggestionsDynamiques(val);
            }
        });

        champRecherche.addEventListener("focus", () => {
            if (champRecherche.value.trim() === "") {
                afficherHistorique();
            }
        });

        champRecherche.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                const val = champRecherche.value.trim();
                filtrerTableau(val);
            }
        });
    }


    document.addEventListener("click", (e) => {
        if (listeSuggestions && champRecherche && 
            !listeSuggestions.contains(e.target) && e.target !== champRecherche) {
            listeSuggestions.classList.add("d-none");
        }
    });
}

function afficherSuggestionsDynamiques(texte) {
    if (!listeSuggestions) return;
    listeSuggestions.innerHTML = "";
    
    const matches = tousLesUtilisateurs.filter(u => u.courriel.toLowerCase().includes(texte.toLowerCase()));
    
    if (matches.length === 0) {
        listeSuggestions.classList.add("d-none");
        return;
    }

   matches.forEach(u => { 
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-action";
        li.textContent = u.courriel;
        li.style.cursor = "pointer";
        li.addEventListener("click", () => {
            champRecherche.value = u.courriel;
            filtrerTableau(u.courriel);
        });
        listeSuggestions.appendChild(li);
    });
    listeSuggestions.classList.toggle("d-none", matches.length === 0);
}


window.addEventListener("load", initialisationUtilisateur);