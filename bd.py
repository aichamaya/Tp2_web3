import os
import types
import contextlib
import mysql.connector

@contextlib.contextmanager
def creer_connexion():
    """Crée une connexion MySQL et commit/rollback automatiquement."""
    conn = mysql.connector.connect(
       user=os.getenv('BD_UTILISATEUR'),
        password=os.getenv('BD_MDP'),
        host=os.getenv('BD_SERVEUR'),
        database=os.getenv('BD_NOM_SCHEMA'),
        port=int(os.getenv('BD_PORT')),
        raise_on_warnings=True
       
    )
   
    conn.get_curseur = types.MethodType(get_curseur, conn)

    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()

@contextlib.contextmanager
def get_curseur(self):
    """Curseur dict, fermé automatiquement."""
    curseur = self.cursor(dictionary=True, buffered=True)
    try:
        yield curseur
    finally:
        curseur.close()

# def hacher_mdp(mdp_en_clair):
#     """Prend un mot de passe en clair et lui applique une fonction de hachage"""
#     return hashlib.sha512(mdp_en_clair.encode('utf-8')).hexdigest()

def verifier_utilisateur_existe(conn, courriel):
    """obtenir un utlisateur grâce à son couuriel"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            SELECT id_utilisateur
            FROM utilisateurs
            WHERE courriel = %(courriel)s
            """,
            {
                "courriel" : courriel
            }
        
        )
        utilisateur = curseur.fetchone()

    return utilisateur['id_utilisateur'] if utilisateur else None
    
def authentifier(conn, courriel, mdp):
    """Retourne un utilisateur avec le courriel et le mot de passe"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "SELECT courriel , mot_de_passe FROM utilisateurs WHERE courriel = %(courriel)s AND mot_de_passe = %(mot_de_passe)s",
            {
                "courriel": courriel,
                "mot_de_passe": mdp  
            }
        )
        return curseur.fetchone()


def ajout_utilisateur(conn, nom, prenom, courriel, mot_de_passe_hache):
    """ajoute un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            INSERT INTO utilisateurs ( nom, prenom, courriel, mot_de_passe, credit,role)
            VALUES (         
            %(nom)s,
            %(prenom)s, 
            %(courriel)s, 
            %(mot_de_passe)s, 
             0, "utiisateur")
            """,
            {
            
                'nom': nom,
                'prenom': prenom,
                'courriel': courriel,
                'mot_de_passe':  mot_de_passe_hache       
            }
                
        )
   

def supprimer_utilisateur(conn, user_id: int):
    """supprimé un utlisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute("DELETE FROM utilisateurs WHERE id_utilisateur = %s", (user_id,))
        return curseur.rowcount

def get_credit_utilisateur(conn, id_utilisateur: int):
    """avoir un credit"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT credit FROM utilisateurs WHERE id_utilisateur = %s", (id_utilisateur,))
        resultat = curseur.fetchone()
        return resultat["credit"] if resultat else 0

               
def update_credit_utilisateur(conn, id_utilisateur: int, nouveau_credit: float):
    """mise à jour du compte de credit"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            "UPDATE utilisateurs SET credit = %s WHERE id_utilisateur = %s",
            (nouveau_credit, id_utilisateur),
        )
        return curseur.rowcount


def get_categories(conn):
    """avoir les categories"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            SELECT id_categorie, nom_categorie
            FROM categories
            ORDER BY nom_categorie
            """
        )
        return curseur.fetchall()

def search_services(conn, q: str = ""):
    """pour recherche un service"""
    sql = """
        SELECT s.*, c.nom_categorie
        FROM services s
        JOIN categories c USING(id_categorie)
        WHERE s.actif = 1
    """
    params = []
    if q:
        sql += " AND (s.titre LIKE %s OR s.description LIKE %s)"
        params += [f"%{q}%", f"%{q}%"]
    sql += " ORDER BY s.date_creation DESC"

    with conn.get_curseur() as curseur:
        curseur.execute(sql, params)
        return curseur.fetchall()

def get_service_by_id(conn, service_id):
    """avoir un service par son ID"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            SELECT s.*, c.nom_categorie
            FROM services s
            JOIN categories c ON s.id_categorie = c.id_categorie
            WHERE id_service = %s
            """,
            (service_id,)
        )
        return curseur.fetchone()

def get_service_all(conn):
    """5 derniers services actifs (incluant nom_image)."""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            SELECT s.id_service, s.titre, s.localisation, c.nom_categorie, s.nom_image
            FROM services s
            JOIN categories c ON c.id_categorie = s.id_categorie
            WHERE s.actif = 1
            ORDER BY s.date_creation DESC
            LIMIT 5
            """
        )
        return curseur.fetchall()

def ajout_service(conn, id_categorie, titre, description, localisation, actif, cout, id_proprietaire, nom_image):
    """ajout de service"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            INSERT INTO services (id_categorie, titre, description, localisation, actif, cout, nom_image, id_utilisateur)
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
            """,
            (id_categorie, titre, description, localisation, actif, cout, nom_image, id_proprietaire),
        )
        return curseur.lastrowid

def update_service(conn, service_id, titre, localisation, description, actif, cout):
    """MàJ sans image (route d'édition standard)."""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            UPDATE services
               SET titre=%s, description=%s, localisation=%s, actif=%s, cout=%s
             WHERE id_service=%s
            """,
            (titre, description, localisation, actif, cout, service_id),
        )
        return curseur.rowcount

def update_service_with_image(conn, service_id, titre, localisation, description, actif, cout, nom_image):
    """Variante si tu gères l'upload d'image."""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            UPDATE services
               SET titre=%s, description=%s, localisation=%s, actif=%s, cout=%s, nom_image=%s
             WHERE id_service=%s
            """,
            (titre, description, localisation, actif, cout, nom_image, service_id),
        )
        return curseur.rowcount
    
def supprimer_service(conn, id_service):
    with conn.get_curseur() as curseur:
        curseur.execute(
            'DELETE FROM services WHERE id_service = %(id)s',
            {'id': id_service}
        )
    return curseur.rowcount



def ajout_reservation(conn, id_service, id_utilisateur, date_reservation, date_souhaitee):
    """Insère la réservation et met à jour les crédits (réservation payante)."""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            INSERT INTO reservations (id_service, id_utilisateur, date_reservation, date_souhaitee)
            VALUES (
            %(id_service)s, 
            %(id_utilisateur)s, 
            %(date_reservation)s, 
            %(date_souhaitee)s)
            """,
            {
                'id_service': id_service,
                'id_utilisateur' :id_utilisateur ,
                'date_reservation' : date_reservation,
                'date_souhaitee': date_souhaitee
                },
        )

   
    service = get_service_by_id(conn, id_service)
    cout_service = service.get("cout", 0) if service else 0

    if cout_service > 0:
        update_credit_utilisateur(conn, id_utilisateur, get_credit_utilisateur(conn, id_utilisateur) - cout_service)
        if service:
            id_proprietaire = service["id_utilisateur"]
            update_credit_utilisateur(conn, id_proprietaire, get_credit_utilisateur(conn, id_proprietaire) + cout_service)

    return True

def get_reservations_by_user(conn, id_utilisateur: int):
    """reservation par un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            SELECT * 
            FROM reservations r     
            JOIN utilisateurs u ON r.id_utilisateur = u.id_utilisateur
            WHERE r.id_utilisateur = %s
            ORDER BY r.date_souhaitee DESC
            """,
            (id_utilisateur,),
        )
        return curseur.fetchall()

def get_reservations_for_owner(conn, id_proprietaire: int):
    """methode pour reserver"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            SELECT r.*, s.titre, s.cout, u.courriel AS courriel_reservant
            FROM reservations r
            JOIN services s ON r.id_service = s.id_service
            JOIN utilisateurs u ON r.id_utilisateur = u.id_utilisateur
            WHERE s.id_utilisateur = %s
            ORDER BY r.date_souhaitee DESC
            """,
            (id_proprietaire,),
        )
        return curseur.fetchall()
    
def service_a_deja_ete_reserve(conn, id_service, date, heure):
    """verifie si le a été reservè ou pas"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT COUNT(*) AS total FROM reservations WHERE id_service = %s and date_reservation = %s and date_souhaitee = %s", (id_service, date, heure,))
        result = curseur.fetchone()
        return result["total"] > 0

def obtenir_les_utilisateurs(conn):
    """permet d'obtenir la liste des utilisateurs"""
    with conn.get_curseur() as curseur:
        curseur.execute("""
            SELECT *
            FROM utilisateurs
            
        """)
        return curseur.fetchall()
    

    
