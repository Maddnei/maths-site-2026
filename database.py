import sqlite3
import os
from contextlib import contextmanager
import config

@contextmanager
def get_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist and seed default classes and data."""
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Classes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                level TEXT NOT NULL,
                description TEXT,
                icon TEXT DEFAULT 'book-open',
                color TEXT DEFAULT 'indigo',
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Announcements / News Table (for bulletin, devoirs, meilleures notes, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                badge_type TEXT DEFAULT 'info',
                is_pinned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
            )
        """)

        # 3. Chapters Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                display_order INTEGER DEFAULT 0,
                is_visible INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
            )
        """)

        # 4. Teacher Resources Table (PDFs, Images, Links)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'cours',
                resource_type TEXT NOT NULL,
                file_url TEXT,
                file_size INTEGER DEFAULT 0,
                external_url TEXT,
                description TEXT,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            )
        """)

        # 5. Student Submissions Table (Exercices et corrigés proposés par les élèves)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                author_name TEXT NOT NULL,
                is_anonymous INTEGER DEFAULT 0,
                statement_url TEXT NOT NULL,
                solution_url TEXT NOT NULL,
                student_note TEXT,
                status TEXT DEFAULT 'pending',
                reject_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            )
        """)

        # 6. Site Settings Table (Année scolaire modifiable, titre, configuration)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS site_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Insert default settings if not existing
        cursor.execute("INSERT OR IGNORE INTO site_settings (key, value) VALUES ('school_year', '2026-2027')")
        cursor.execute("INSERT OR IGNORE INTO site_settings (key, value) VALUES ('teacher_name', 'M. Gimenez')")
        cursor.execute("INSERT OR IGNORE INTO site_settings (key, value) VALUES ('site_title', 'Maths & Sciences')")

        # Seed initial classes if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM classes")
        if cursor.fetchone()['cnt'] == 0:
            seed_initial_data(cursor)


def seed_initial_data(cursor):
    """Seed initial classes and sample chapters matching teacher's exact distribution."""
    classes_data = [
        (
            "Seconde (Maths & SNT)",
            "2nde-snt",
            "Seconde Générale",
            "Mathématiques & Sciences Numériques et Technologie",
            "binary",
            "blue",
            1
        ),
        (
            "1ère STMG 1",
            "1ere-stmg-1",
            "Première STMG",
            "Mathématiques appliquées à la gestion et aux sciences technologiques",
            "trending-up",
            "emerald",
            2
        ),
        (
            "1ère STMG 2",
            "1ere-stmg-2",
            "Première STMG",
            "Mathématiques appliquées à la gestion et aux sciences technologiques",
            "pie-chart",
            "teal",
            3
        ),
        (
            "1ère Enseignement Scientifique 1",
            "1ere-es-1",
            "Première Générale",
            "Enseignement Scientifique (Mathématiques & Modélisation)",
            "atom",
            "violet",
            4
        ),
        (
            "1ère Enseignement Scientifique 2",
            "1ere-es-2",
            "Première Générale",
            "Enseignement Scientifique (Mathématiques & Modélisation)",
            "microscope",
            "purple",
            5
        ),
    ]

    for name, code, level, desc, icon, color, order in classes_data:
        cursor.execute("""
            INSERT INTO classes (name, code, level, description, icon, color, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, code, level, desc, icon, color, order))
        class_id = cursor.lastrowid

        # Add a welcoming announcement for each class
        cursor.execute("""
            INSERT INTO announcements (class_id, title, content, badge_type, is_pinned)
            VALUES (?, ?, ?, ?, 1)
        """, (
            class_id,
            "Bienvenue pour l'année scolaire 2026-2027 !",
            "Retrouvez ici l'ensemble des cours, fiches d'exercices, corrigés et liens utiles. N'hésitez pas à participer en partageant vos exercices et corrections dans chaque chapitre !",
            "info"
        ))

        # Add sample chapters depending on level
        if "2nde" in code:
            chapters = [
                (1, "Nombres, calculs et intervalles", "Ensembles de nombres, calculs fractionnaires, puissances, racines et intervalles."),
                (2, "Généralités sur les fonctions & variations", "Notion de fonction, images, antécédents, représentations graphiques et tableaux de variations."),
                (3, "SNT : Données structurées et traitement", "Tableurs, formats de données (CSV), requêtes et traitement de données."),
                (4, "Géométrie vectorielle et repérage", "Vecteurs, coordonnées, colinéarité et configurations du plan."),
            ]
        elif "stmg" in code:
            chapters = [
                (1, "Proportions et pourcentages d'évolution", "Taux d'évolution, évolutions successives et taux global, coefficients multiplicateurs."),
                (2, "Suites arithmétiques et géométriques", "Définition, modélisation de phénomènes discrets, calcul du terme général."),
                (3, "Fonctions polynômes du second degré", "Forme développée, factorisée, étude du signe et extremum."),
                (4, "Statistiques à deux variables & ajustement", "Nuages de points, point moyen, droite d'ajustement affine."),
            ]
        else: # Enseignement Scientifique
            chapters = [
                (1, "Une longue histoire de la matière", "Éléments chimiques, radioactivité, abondance et structure de la matière."),
                (2, "Le rayonnement solaire & bilan radiatif", "Spectre, puissance rayonnée, effet de serre et équilibre thermique terrestre."),
                (3, "La forme et les dimensions de la Terre", "Histoire de la mesure de la Terre d'Ératosthène à la triangulation géodésique."),
                (4, "Son et musique : des phénomènes physiques", "Fréquence, son pur/complexe, harmoniques et gamme musicale."),
            ]

        for num, title, description in chapters:
            cursor.execute("""
                INSERT INTO chapters (class_id, chapter_number, title, description, display_order)
                VALUES (?, ?, ?, ?, ?)
            """, (class_id, num, title, description, num))


# Helper query functions
def get_all_classes():
    with get_db() as conn:
        return conn.execute("SELECT * FROM classes ORDER BY display_order ASC, id ASC").fetchall()


def get_class_by_id(class_id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()


def get_class_by_code(code):
    with get_db() as conn:
        return conn.execute("SELECT * FROM classes WHERE code = ?", (code,)).fetchone()


def get_class_announcements(class_id):
    with get_db() as conn:
        return conn.execute("""
            SELECT * FROM announcements 
            WHERE class_id = ? OR class_id IS NULL 
            ORDER BY is_pinned DESC, created_at DESC
        """, (class_id,)).fetchall()


def get_global_announcements():
    with get_db() as conn:
        return conn.execute("""
            SELECT a.*, c.name as class_name 
            FROM announcements a
            LEFT JOIN classes c ON a.class_id = c.id
            ORDER BY a.is_pinned DESC, a.created_at DESC
            LIMIT 5
        """).fetchall()


def get_class_chapters(class_id, teacher_mode=False):
    with get_db() as conn:
        if teacher_mode:
            query = """
                SELECT c.*, 
                       (SELECT COUNT(*) FROM resources r WHERE r.chapter_id = c.id) as resource_count,
                       (SELECT COUNT(*) FROM student_submissions s WHERE s.chapter_id = c.id AND s.status = 'approved') as approved_exercises_count,
                       (SELECT COUNT(*) FROM student_submissions s WHERE s.chapter_id = c.id AND s.status = 'pending') as pending_exercises_count
                FROM chapters c 
                WHERE c.class_id = ? 
                ORDER BY c.display_order ASC, c.chapter_number ASC
            """
        else:
            query = """
                SELECT c.*, 
                       (SELECT COUNT(*) FROM resources r WHERE r.chapter_id = c.id) as resource_count,
                       (SELECT COUNT(*) FROM student_submissions s WHERE s.chapter_id = c.id AND s.status = 'approved') as approved_exercises_count
                FROM chapters c 
                WHERE c.class_id = ? AND c.is_visible = 1
                ORDER BY c.display_order ASC, c.chapter_number ASC
            """
        return conn.execute(query, (class_id,)).fetchall()


def get_chapter_by_id(chapter_id):
    with get_db() as conn:
        return conn.execute("""
            SELECT c.*, cl.name as class_name, cl.code as class_code, cl.color as class_color, cl.level as class_level
            FROM chapters c
            JOIN classes cl ON c.class_id = cl.id
            WHERE c.id = ?
        """, (chapter_id,)).fetchone()


def get_chapter_resources(chapter_id):
    with get_db() as conn:
        return conn.execute("""
            SELECT * FROM resources 
            WHERE chapter_id = ? 
            ORDER BY display_order ASC, created_at ASC
        """, (chapter_id,)).fetchall()


def get_chapter_approved_submissions(chapter_id):
    with get_db() as conn:
        return conn.execute("""
            SELECT * FROM student_submissions 
            WHERE chapter_id = ? AND status = 'approved' 
            ORDER BY created_at DESC
        """, (chapter_id,)).fetchall()


def get_pending_submissions():
    with get_db() as conn:
        return conn.execute("""
            SELECT s.*, c.title as chapter_title, c.chapter_number, cl.name as class_name, cl.color as class_color
            FROM student_submissions s
            JOIN chapters c ON s.chapter_id = c.id
            JOIN classes cl ON c.class_id = cl.id
            WHERE s.status = 'pending'
            ORDER BY s.created_at DESC
        """).fetchall()


def get_all_submissions_for_admin(status_filter=None):
    with get_db() as conn:
        if status_filter:
            query = """
                SELECT s.*, c.title as chapter_title, c.chapter_number, cl.name as class_name, cl.color as class_color
                FROM student_submissions s
                JOIN chapters c ON s.chapter_id = c.id
                JOIN classes cl ON c.class_id = cl.id
                WHERE s.status = ?
                ORDER BY s.created_at DESC
            """
            return conn.execute(query, (status_filter,)).fetchall()
        else:
            query = """
                SELECT s.*, c.title as chapter_title, c.chapter_number, cl.name as class_name, cl.color as class_color
                FROM student_submissions s
                JOIN chapters c ON s.chapter_id = c.id
                JOIN classes cl ON c.class_id = cl.id
                ORDER BY s.created_at DESC
            """
            return conn.execute(query).fetchall()


def get_pending_submissions_count():
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) as cnt FROM student_submissions WHERE status = 'pending'").fetchone()
        return row['cnt'] if row else 0


# -------------------------------------------------------------------
# Site Settings & Year Transition (Année scolaire & Réinitialisation)
# -------------------------------------------------------------------
def get_setting(key, default=None):
    with get_db() as conn:
        row = conn.execute("SELECT value FROM site_settings WHERE key = ?", (key,)).fetchone()
        return row['value'] if row else default


def set_setting(key, value):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO site_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, str(value)))


def get_all_settings():
    with get_db() as conn:
        rows = conn.execute("SELECT key, value FROM site_settings").fetchall()
        return {r['key']: r['value'] for r in rows}


def reset_end_of_year(new_school_year, reset_type='standard'):
    """
    Reset data at the end of the school year.
    Cleans attached files from Cloudinary and local disk to preserve quotas.
    """
    import storage
    with get_db() as conn:
        cursor = conn.cursor()

        # Update school year setting
        if new_school_year:
            cursor.execute("""
                INSERT INTO site_settings (key, value) VALUES ('school_year', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (new_school_year,))

        if reset_type == 'exercises_only':
            # Delete files from Cloudinary
            submissions = cursor.execute("SELECT statement_url, solution_url FROM student_submissions").fetchall()
            for s in submissions:
                if s['statement_url']:
                    storage.delete_file_from_storage(s['statement_url'])
                if s['solution_url']:
                    storage.delete_file_from_storage(s['solution_url'])

            cursor.execute("DELETE FROM student_submissions")
            return {
                'message': f"Toutes les propositions d'exercices d'élèves ont été effacées du site et du cloud. L'année scolaire est maintenant {new_school_year}.",
                'type': 'exercises_only'
            }

        elif reset_type == 'standard':
            # 1. Clear all student submissions and their files from Cloudinary
            submissions = cursor.execute("SELECT statement_url, solution_url FROM student_submissions").fetchall()
            for s in submissions:
                if s['statement_url']:
                    storage.delete_file_from_storage(s['statement_url'])
                if s['solution_url']:
                    storage.delete_file_from_storage(s['solution_url'])

            cursor.execute("DELETE FROM student_submissions")
            
            # 2. Clear old announcements
            cursor.execute("DELETE FROM announcements")

            # 3. Add fresh welcome announcement for every class
            classes = cursor.execute("SELECT id, name FROM classes").fetchall()
            for c in classes:
                cursor.execute("""
                    INSERT INTO announcements (class_id, title, content, badge_type, is_pinned)
                    VALUES (?, ?, ?, 'info', 1)
                """, (
                    c['id'],
                    f"Bienvenue pour l'année scolaire {new_school_year} !",
                    "Retrouvez ici l'ensemble des cours, fiches d'exercices, corrigés et liens utiles. N'hésitez pas à participer en partageant vos exercices et corrections dans chaque chapitre !"
                ))

            return {
                'message': f"Transition vers l'année scolaire {new_school_year} réussie ! Les photos des élèves et anciennes annonces ont été effacées du cloud. Vos cours et chapitres ont été conservés intacts.",
                'type': 'standard'
            }

        elif reset_type == 'full_factory_reset':
            # Delete all uploaded files (submissions + resources) from Cloudinary
            submissions = cursor.execute("SELECT statement_url, solution_url FROM student_submissions").fetchall()
            for s in submissions:
                if s['statement_url']:
                    storage.delete_file_from_storage(s['statement_url'])
                if s['solution_url']:
                    storage.delete_file_from_storage(s['solution_url'])

            resources = cursor.execute("SELECT file_url FROM resources WHERE file_url IS NOT NULL").fetchall()
            for r in resources:
                if r['file_url']:
                    storage.delete_file_from_storage(r['file_url'])

            cursor.execute("DELETE FROM student_submissions")
            cursor.execute("DELETE FROM resources")
            cursor.execute("DELETE FROM chapters")
            cursor.execute("DELETE FROM announcements")
            cursor.execute("DELETE FROM classes")
            
            # Re-seed
            seed_initial_data(cursor)

            # Update school year again
            cursor.execute("UPDATE site_settings SET value = ? WHERE key = 'school_year'", (new_school_year,))
            
            return {
                'message': f"Réinitialisation totale réussie. Le site et le stockage cloud ont été remis à neuf pour l'année {new_school_year}.",
                'type': 'full_factory_reset'
            }

