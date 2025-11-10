import re
regex_html = re.compile(r'<[^>]*>')
regex_courriel = re.compile(r'^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}$')
regex_mdp = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')

def valider_service(titre, description, localisation, cout, id_categorie, photo, photo_obligatoire=True, est_modification=False):
    erreurs = {}


    if not titre:
        erreurs['titre'] = "Veuillez saisir le titre du service"
    elif regex_html.search(titre):
        erreurs['titre'] = "Le titre est invalide."

  
    if not description:
        erreurs['description'] = "Veuillez saisir une description"
    elif regex_html.search(description):
        erreurs['description'] = "La description est invalide."

    if not localisation:
        erreurs['localisation'] = "Veuillez entrer une localisation "
    elif regex_html.match(localisation):
        erreurs['localisation'] = "La localisation est invalide."


    if not cout:
        erreurs['cout'] = "Veuillez entrer le coût"
    else:
        cout = float(cout)
        if cout < 0:
            erreurs['cout'] = "Le coût doit être un nombre positif"


    if not est_modification and not id_categorie:
        erreurs['id_categorie'] = "Veuillez choisir une catégorie"
    
    if photo_obligatoire:
      
        if not photo or photo.filename.strip() == "":
            erreurs['photo'] = "Veuillez ajouter une photo"
        if len(photo.filename) > 20:
            erreurs['photo'] = "Le nom de la photo est trop long"
    else:
   
        if photo and photo.filename.strip() != "":
            if len(photo.filename) > 20:
                erreurs['photo'] = "Le nom de la photo est trop long"
    return erreurs
