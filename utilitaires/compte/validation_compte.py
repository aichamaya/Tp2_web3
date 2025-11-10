import re

regex_html = re.compile(r'<[^>]*>')
regex_courriel = re.compile(r'^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}$')
regex_motDePasse = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')


def valider_compte(prenom_utilisateur,nom_utilisateur,courriel, mot_de_passe, confirmer_mot_de_passe):
    erreurs= {}

    prenom_utilisateur = regex_html.sub('', prenom_utilisateur).strip()
    if not prenom_utilisateur:
        erreurs['prenom_utilisateur'] = "Le prénom est obligatoire"

    nom_utilisateur = regex_html.sub('', nom_utilisateur).strip()
    if not nom_utilisateur:
        erreurs['nom_utilisateur'] = "Le nom est obligatoire"

    if not courriel:
        erreurs['courriel'] = "Veuillez saisir votre courriel."
    elif not regex_courriel.fullmatch(courriel): 
        erreurs['courriel'] = "Veuillez saisir un courriel valide."

    if not mot_de_passe:
        erreurs['mdp'] = "Veuillez saisir un mot de passe."
    elif not regex_motDePasse.match(mot_de_passe):
        erreurs['mdp'] = "Votre mot de passe doit contenir au moins une majuscule, une minuscule, un chiffre, et au moins 8 caractères."

  
    if mot_de_passe != confirmer_mot_de_passe:
        erreurs['confirmer_mdp'] = "Les deux mots de passe saisis ne correspondent pas"

    return erreurs