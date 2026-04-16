"""
TranspoBot — Initialisation automatique de la base PostgreSQL
"""
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

def init_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    try:
        print("Initialisation de la base de données...")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicules (
          id SERIAL PRIMARY KEY,
          immatriculation VARCHAR(20) NOT NULL UNIQUE,
          type VARCHAR(10) NOT NULL,
          capacite INT NOT NULL,
          statut VARCHAR(20) DEFAULT 'actif',
          kilometrage INT DEFAULT 0,
          date_acquisition DATE DEFAULT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lignes (
          id SERIAL PRIMARY KEY,
          code VARCHAR(10) NOT NULL UNIQUE,
          nom VARCHAR(100) DEFAULT NULL,
          origine VARCHAR(100) NOT NULL,
          destination VARCHAR(100) NOT NULL,
          distance_km DECIMAL(6,2) DEFAULT NULL,
          duree_minutes INT DEFAULT NULL
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chauffeurs (
          id SERIAL PRIMARY KEY,
          nom VARCHAR(100) NOT NULL,
          prenom VARCHAR(100) NOT NULL,
          telephone VARCHAR(20) DEFAULT NULL,
          numero_permis VARCHAR(30) NOT NULL UNIQUE,
          categorie_permis VARCHAR(5) DEFAULT NULL,
          disponibilite BOOLEAN DEFAULT TRUE,
          vehicule_id INT DEFAULT NULL REFERENCES vehicules(id),
          date_embauche DATE DEFAULT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarifs (
          id SERIAL PRIMARY KEY,
          ligne_id INT NOT NULL REFERENCES lignes(id),
          type_client VARCHAR(10) DEFAULT 'normal',
          prix DECIMAL(10,2) NOT NULL
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trajets (
          id SERIAL PRIMARY KEY,
          ligne_id INT NOT NULL REFERENCES lignes(id),
          chauffeur_id INT NOT NULL REFERENCES chauffeurs(id),
          vehicule_id INT NOT NULL REFERENCES vehicules(id),
          date_heure_depart TIMESTAMP NOT NULL,
          date_heure_arrivee TIMESTAMP DEFAULT NULL,
          statut VARCHAR(20) DEFAULT 'planifie',
          nb_passagers INT DEFAULT 0,
          recette DECIMAL(10,2) DEFAULT 0.00,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
          id SERIAL PRIMARY KEY,
          trajet_id INT NOT NULL REFERENCES trajets(id),
          type VARCHAR(10) NOT NULL,
          description TEXT DEFAULT NULL,
          gravite VARCHAR(10) DEFAULT 'faible',
          date_incident TIMESTAMP NOT NULL,
          resolu BOOLEAN DEFAULT FALSE,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        cursor.execute("SELECT COUNT(*) FROM vehicules")
        if cursor.fetchone()[0] == 0:
            print("Insertion des données...")

            cursor.execute("""INSERT INTO vehicules (id, immatriculation, type, capacite, statut, kilometrage, date_acquisition) VALUES
            (1,'DK-1234-AB','bus',60,'actif',45000,'2021-03-15'),
            (2,'DK-5678-CD','minibus',25,'actif',32000,'2022-06-01'),
            (3,'DK-9012-EF','bus',60,'maintenance',78000,'2019-11-20'),
            (4,'DK-3456-GH','taxi',5,'actif',120000,'2020-01-10'),
            (5,'DK-7890-IJ','minibus',25,'actif',15000,'2023-09-05')""")
            cursor.execute("SELECT setval('vehicules_id_seq', 6)")

            cursor.execute("""INSERT INTO lignes (id, code, nom, origine, destination, distance_km, duree_minutes) VALUES
            (1,'L1','Ligne Dakar-Thiès','Dakar','Thiès',70.50,90),
            (2,'L2','Ligne Dakar-Mbour','Dakar','Mbour',82.00,120),
            (3,'L3','Ligne Centre-Banlieue','Plateau','Pikine',15.00,45),
            (4,'L4','Ligne Aéroport','Centre-ville','AIBD',45.00,60)""")
            cursor.execute("SELECT setval('lignes_id_seq', 5)")

            cursor.execute("""INSERT INTO chauffeurs (id, nom, prenom, telephone, numero_permis, categorie_permis, disponibilite, vehicule_id, date_embauche) VALUES
            (1,'DIOP','Mamadou','+221771234567','P-2019-001','D',TRUE,1,'2019-04-01'),
            (2,'FALL','Ibrahima','+221772345678','P-2020-002','D',TRUE,2,'2020-07-15'),
            (3,'NDIAYE','Fatou','+221773456789','P-2021-003','B',TRUE,4,'2021-02-01'),
            (4,'SECK','Ousmane','+221774567890','P-2022-004','D',TRUE,5,'2022-10-20'),
            (5,'BA','Aminata','+221775678901','P-2023-005','D',TRUE,NULL,'2023-01-10')""")
            cursor.execute("SELECT setval('chauffeurs_id_seq', 6)")

            cursor.execute("""INSERT INTO tarifs (id, ligne_id, type_client, prix) VALUES
            (1,1,'normal',2500),(2,1,'etudiant',1500),(3,1,'senior',1800),
            (4,2,'normal',3000),(5,2,'etudiant',1800),
            (6,3,'normal',500),(7,3,'etudiant',300),
            (8,4,'normal',5000),(9,4,'etudiant',3000)""")
            cursor.execute("SELECT setval('tarifs_id_seq', 10)")

            cursor.execute("""INSERT INTO trajets (id, ligne_id, chauffeur_id, vehicule_id, date_heure_depart, date_heure_arrivee, statut, nb_passagers, recette) VALUES
(1,1,1,1, CURRENT_DATE-6, CURRENT_DATE-5, 'termine',  55, 137500),
(2,1,2,2, CURRENT_DATE-5, CURRENT_DATE-4, 'termine',  20, 50000),
(3,2,3,4, CURRENT_DATE-4, CURRENT_DATE-3, 'termine',  4,  12000),
(4,3,4,5, CURRENT_DATE-3, NULL,           'annule',   0,  0),
(5,1,1,1, CURRENT_DATE-2, CURRENT_DATE-1, 'termine',  58, 145000),
(6,4,2,2, CURRENT_DATE-1, CURRENT_DATE,   'termine',  18, 90000),
(7,1,5,1, CURRENT_DATE,   NULL,           'en_cours', 45, 112500)""")

            cursor.execute("""INSERT INTO incidents (id, trajet_id, type, description, gravite, date_incident, resolu) VALUES
(1,2,'retard',  'Embouteillage au centre-ville',  'faible', CURRENT_DATE-5, TRUE),
(2,3,'panne',   'Crevaison pneu avant droit',      'moyen',  CURRENT_DATE-4, TRUE),
(3,6,'accident','Accrochage léger au rond-point', 'grave',  CURRENT_DATE-1, FALSE)""")

            print("Données insérées!")
        else:
            print("Tables déjà initialisées.")

        conn.commit()
        print("Base de données prête!")

    except Exception as e:
        conn.rollback()
        print(f"Erreur init_db: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_db()
