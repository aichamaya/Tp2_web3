import types
import contextlib
import mysql.connector

@contextlib.contextmanager
def creer_connexion():
    """Crée une connexion MySQL et commit/rollback automatiquement."""
    conn = mysql.connector.connect(
        user="garneau",
        password="qwerty_123",
        host="127.0.0.1",
        database="services_particuliers",
        raise_on_warnings=True,
       
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

def get_utilisateur_by_courriel(conn, courriel: str):
    """avoir un utlisateur grace à son couurile"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            SELECT id_utilisateur, courriel, mot_de_passe, credit, role
            FROM utilisateurs
            WHERE courriel = %s
            """,
            (courriel,),
        )
        return curseur.fetchone()

def ajout_utilisateur(conn, courriel: str, mot_de_passe_hache: str):
    """ajout un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            INSERT INTO utilisateurs (courriel, mot_de_passe, role, credit)
            VALUES (%s, %s, 'utilisateur', 0)
            """,
            (courriel, mot_de_passe_hache),
        )
        return curseur.lastrowid

def supprimer_utilisateur(conn, user_id: int):
    """supprimé un utlisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute("DELETE FROM utilisateurs WHERE id_utilisateur = %s", (user_id,))
        return curseur.rowcount

def get_credit_utilisateur(conn, id_utilisateur: int):
    """avoir un credit"""
    with conn.get_curseur() as curseur:
        curseur.execute("SELECT credit FROM utilisateurs WHERE id_utilisateur = %s", (id_utilisateur,))
        r = curseur.fetchone()
        return r["credit"] if r else 0

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

def search_services(conn, q: str = "", categorie=None, localisation: str = ""):
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
    if categorie:
        sql += " AND s.id_categorie = %s"
        params.append(categorie)
    if localisation:
        sql += " AND s.localisation LIKE %s"
        params.append(f"%{localisation}%")
    sql += " ORDER BY s.date_creation DESC"

    with conn.get_curseur() as curseur:
        curseur.execute(sql, params)
        return curseur.fetchall()

def get_service_by_id(conn, service_id: int):
    """avoir un service par son ID"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            SELECT s.*, c.nom_categorie, u.courriel AS courriel_proprietaire
            FROM services s
            JOIN categories c USING(id_categorie)
            JOIN utilisateurs u ON s.id_utilisateur = u.id_utilisateur
            WHERE s.id_service = %s
            """,
            (service_id,),
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

def ajout_service(conn, id_categorie, titre, description, localisation, actif, cout, id_proprietaire):
    """ajout de service"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            INSERT INTO services (id_categorie, titre, description, localisation, actif, cout, id_utilisateur)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (id_categorie, titre, description, localisation, actif, cout, id_proprietaire),
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



def ajout_reservation(conn, id_service, id_utilisateur, date_reservation, date_souhaitee, cout_paye):
    """Insère la réservation et met à jour les crédits (réservation payante)."""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            INSERT INTO reservations (id_service, id_utilisateur, date_reservation, date_souhaitee, cout_paye)
            VALUES (%s, %s, NOW(), %s, %s)
            """,
            (id_service, id_utilisateur, date_souhaitee, cout_paye),
        )

   
    update_credit_utilisateur(conn, id_utilisateur, get_credit_utilisateur(conn, id_utilisateur) - cout_paye)

    service = get_service_by_id(conn, id_service)
    if service:
        id_proprietaire = service["id_utilisateur"]
        update_credit_utilisateur(conn, id_proprietaire, get_credit_utilisateur(conn, id_proprietaire) + cout_paye)

    return True

def get_reservations_by_user(conn, id_utilisateur: int):
    """reservetion par un utilisateur"""
    with conn.get_curseur() as curseur:
        curseur.execute(
            """
            SELECT r.*, s.titre, s.cout, u.courriel AS courriel_proprietaire
            FROM reservations r
            JOIN services s ON r.id_service = s.id_service
            JOIN utilisateurs u ON s.id_utilisateur = u.id_utilisateur
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
