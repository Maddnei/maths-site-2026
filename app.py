import os
import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, 
    session, flash, jsonify, send_from_directory, abort
)
from werkzeug.security import check_password_hash, generate_password_hash

import config
import database as db
import storage

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

# Initialize database
db.init_db()


# -------------------------------------------------------------------
# Authentication Helpers
# -------------------------------------------------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Veuillez vous connecter en tant que professeur pour accéder à cette page.', 'warning')
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_global_vars():
    """Inject global variables into all Jinja templates."""
    is_admin = session.get('is_admin', False)
    all_classes = db.get_all_classes()
    pending_count = db.get_pending_submissions_count() if is_admin else 0
    settings = db.get_all_settings()
    school_year = settings.get('school_year', '2026-2027')
    teacher_name = settings.get('teacher_name', 'M. Gimenez')
    site_title = settings.get('site_title', 'Maths & Sciences')

    return {
        'is_admin': is_admin,
        'global_classes': all_classes,
        'pending_submissions_count': pending_count,
        'school_year': school_year,
        'teacher_name': teacher_name,
        'site_title': site_title,
        'site_settings': settings,
        'current_year': datetime.datetime.now().year,
        'admin_username': config.ADMIN_USERNAME
    }


# -------------------------------------------------------------------
# Custom Jinja Filters
# -------------------------------------------------------------------
@app.template_filter('filesize')
def format_filesize_filter(size_bytes):
    return storage.format_file_size(size_bytes)


@app.template_filter('datetime_fr')
def format_datetime_fr(value):
    if not value:
        return ""
    try:
        # SQLite string format "YYYY-MM-DD HH:MM:SS"
        if isinstance(value, str):
            dt = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            dt = value
        months = ["janvier", "février", "mars", "avril", "mai", "juin", 
                  "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        return f"{dt.day} {months[dt.month - 1]} {dt.year} à {dt.strftime('%Hh%M')}"
    except Exception:
        return str(value)


@app.template_filter('date_short_fr')
def format_date_short_fr(value):
    if not value:
        return ""
    try:
        if isinstance(value, str):
            dt = datetime.datetime.fromisoformat(value.split()[0])
        else:
            dt = value
        months = ["janv.", "févr.", "mars", "avr.", "mai", "juin", 
                  "juil.", "août", "sept.", "oct.", "nov.", "déc."]
        return f"{dt.day} {months[dt.month - 1]} {dt.year}"
    except Exception:
        return str(value)


# -------------------------------------------------------------------
# Public Routes
# -------------------------------------------------------------------
@app.route('/')
def index():
    """Home page with class selection cards."""
    classes = db.get_all_classes()
    return render_template('index.html', classes=classes)


@app.route('/classe/<int:class_id>')
def class_view(class_id):
    """Class home page with announcements and chapters."""
    cls = db.get_class_by_id(class_id)
    if not cls:
        flash('Classe introuvable.', 'danger')
        return redirect(url_for('index'))
    
    is_teacher = session.get('is_admin', False)
    announcements = db.get_class_announcements(class_id)
    chapters = db.get_class_chapters(class_id, teacher_mode=is_teacher)
    
    return render_template('class.html', current_class=cls, announcements=announcements, chapters=chapters)


@app.route('/chapitre/<int:chapter_id>')
def chapter_view(chapter_id):
    """Chapter page with teacher resources and student exercise submissions."""
    chapter = db.get_chapter_by_id(chapter_id)
    if not chapter:
        flash('Chapitre introuvable.', 'danger')
        return redirect(url_for('index'))
    
    resources = db.get_chapter_resources(chapter_id)
    approved_submissions = db.get_chapter_approved_submissions(chapter_id)
    
    # Get pending submissions for this chapter if teacher is logged in
    pending_submissions = []
    if session.get('is_admin'):
        with db.get_db() as conn:
            pending_submissions = conn.execute("""
                SELECT * FROM student_submissions 
                WHERE chapter_id = ? AND status = 'pending' 
                ORDER BY created_at DESC
            """, (chapter_id,)).fetchall()
    
    return render_template(
        'chapter.html', 
        chapter=chapter, 
        resources=resources, 
        approved_submissions=approved_submissions,
        pending_submissions=pending_submissions
    )


@app.route('/soumettre-exercice/<int:chapter_id>', methods=['POST'])
def submit_student_exercise(chapter_id):
    """Student submission for exercise & solution photos."""
    chapter = db.get_chapter_by_id(chapter_id)
    if not chapter:
        return jsonify({'success': False, 'message': 'Chapitre inexistant'}), 404

    title = request.form.get('title', '').strip()
    author_name = request.form.get('author_name', '').strip()
    is_anonymous = 1 if request.form.get('is_anonymous') == '1' else 0
    student_note = request.form.get('student_note', '').strip()

    if not title:
        title = "Exercice partagé"
    
    if is_anonymous or not author_name:
        author_name = "Élève anonyme"

    # Process files
    statement_file = request.files.get('statement_photo')
    solution_file = request.files.get('solution_photo')

    if not statement_file or statement_file.filename == '':
        flash("La photo de l'énoncé de l'exercice est obligatoire.", "danger")
        return redirect(url_for('chapter_view', chapter_id=chapter_id))

    if not solution_file or solution_file.filename == '':
        flash("La photo de la correction/solution est obligatoire.", "danger")
        return redirect(url_for('chapter_view', chapter_id=chapter_id))

    # Save statement
    statement_res = storage.save_uploaded_file(statement_file, folder_category='exercises', custom_prefix='enonce_')
    if not statement_res:
        flash("Format d'image non valide pour l'énoncé (PNG, JPG, JPEG, WEBP acceptés).", "danger")
        return redirect(url_for('chapter_view', chapter_id=chapter_id))

    # Save solution
    solution_res = storage.save_uploaded_file(solution_file, folder_category='solutions', custom_prefix='corrige_')
    if not solution_res:
        flash("Format d'image non valide pour la correction (PNG, JPG, JPEG, WEBP acceptés).", "danger")
        return redirect(url_for('chapter_view', chapter_id=chapter_id))

    # Insert in DB with status = 'pending'
    with db.get_db() as conn:
        conn.execute("""
            INSERT INTO student_submissions 
            (chapter_id, title, author_name, is_anonymous, statement_url, solution_url, student_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (
            chapter_id, 
            title, 
            author_name, 
            is_anonymous, 
            statement_res['url'], 
            solution_res['url'], 
            student_note
        ))

    flash("Merci pour ta contribution ! Ta proposition a bien été envoyée au professeur. Elle apparaîtra ici dès qu'elle aura été validée.", "success")
    return redirect(url_for('chapter_view', chapter_id=chapter_id))


# -------------------------------------------------------------------
# Authentication Routes
# -------------------------------------------------------------------
@app.route('/connexion', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        next_page = request.form.get('next') or request.args.get('next')

        # Check against configured credentials
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['is_admin'] = True
            session['username'] = username
            flash('Connexion réussie ! Vous êtes en mode administrateur.', 'success')
            if next_page and not next_page.startswith('//') and not next_page.startswith('http'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Identifiant ou mot de passe incorrect.', 'danger')

    return render_template('admin_login.html', next=request.args.get('next', ''))


@app.route('/deconnexion')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('username', None)
    flash('Vous êtes déconnecté du mode professeur.', 'info')
    return redirect(url_for('index'))


# -------------------------------------------------------------------
# Teacher / Admin Management Routes
# -------------------------------------------------------------------
@app.route('/admin')
@app.route('/admin/moderation')
@admin_required
def admin_moderation():
    """Teacher Moderation Center for all student submissions."""
    status_filter = request.args.get('filter', 'pending')
    submissions = db.get_all_submissions_for_admin(status_filter if status_filter != 'all' else None)
    pending_count = db.get_pending_submissions_count()
    return render_template('admin_mod.html', submissions=submissions, current_filter=status_filter, pending_count=pending_count)


@app.route('/admin/soumissions/<int:submission_id>/valider', methods=['POST'])
@admin_required
def approve_submission(submission_id):
    """Approve a student submission so all students can see it."""
    with db.get_db() as conn:
        conn.execute("""
            UPDATE student_submissions 
            SET status = 'approved', reviewed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (submission_id,))
    
    flash("L'exercice a été validé avec succès et est désormais visible par tous les élèves !", "success")
    return redirect(request.referrer or url_for('admin_moderation'))


@app.route('/admin/soumissions/<int:submission_id>/rejeter', methods=['POST'])
@admin_required
def reject_submission(submission_id):
    """Reject a student submission."""
    reason = request.form.get('reason', '')
    with db.get_db() as conn:
        conn.execute("""
            UPDATE student_submissions 
            SET status = 'rejected', reject_reason = ?, reviewed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (reason, submission_id))
    
    flash("La proposition a été rejetée.", "info")
    return redirect(request.referrer or url_for('admin_moderation'))


@app.route('/admin/soumissions/<int:submission_id>/supprimer', methods=['POST'])
@admin_required
def delete_submission(submission_id):
    """Permanently delete a submission."""
    with db.get_db() as conn:
        conn.execute("DELETE FROM student_submissions WHERE id = ?", (submission_id,))
    flash("La proposition a été supprimée définitivement.", "success")
    return redirect(request.referrer or url_for('admin_moderation'))


# Class Management
@app.route('/admin/classes')
@admin_required
def admin_classes():
    classes = db.get_all_classes()
    return render_template('admin_classes.html', classes=classes)


@app.route('/admin/classes/ajouter', methods=['POST'])
@admin_required
def add_class():
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().lower().replace(' ', '-')
    level = request.form.get('level', '').strip()
    description = request.form.get('description', '').strip()
    color = request.form.get('color', 'indigo')
    icon = request.form.get('icon', 'book-open')
    order = int(request.form.get('display_order', 0) or 0)

    if not name or not code or not level:
        flash("Veuillez renseigner le nom, le code et le niveau de la classe.", "danger")
        return redirect(url_for('admin_classes'))

    try:
        with db.get_db() as conn:
            conn.execute("""
                INSERT INTO classes (name, code, level, description, icon, color, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, code, level, description, icon, color, order))
        flash(f"La classe « {name} » a été créée avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors de la création de la classe (code peut-être déjà utilisé) : {e}", "danger")

    return redirect(url_for('admin_classes'))


@app.route('/admin/classes/<int:class_id>/modifier', methods=['POST'])
@admin_required
def edit_class(class_id):
    name = request.form.get('name', '').strip()
    level = request.form.get('level', '').strip()
    description = request.form.get('description', '').strip()
    color = request.form.get('color', 'indigo')
    icon = request.form.get('icon', 'book-open')
    order = int(request.form.get('display_order', 0) or 0)

    with db.get_db() as conn:
        conn.execute("""
            UPDATE classes 
            SET name = ?, level = ?, description = ?, color = ?, icon = ?, display_order = ?
            WHERE id = ?
        """, (name, level, description, color, icon, order, class_id))

    flash("Classe mise à jour avec succès.", "success")
    return redirect(url_for('admin_classes'))


@app.route('/admin/classes/<int:class_id>/supprimer', methods=['POST'])
@admin_required
def delete_class(class_id):
    with db.get_db() as conn:
        conn.execute("DELETE FROM classes WHERE id = ?", (class_id,))
    flash("Classe supprimée.", "success")
    return redirect(url_for('admin_classes'))


# Announcements Management
@app.route('/admin/annonces/ajouter', methods=['POST'])
@admin_required
def add_announcement():
    class_id = request.form.get('class_id')
    class_id = int(class_id) if class_id and class_id != 'all' else None
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    badge_type = request.form.get('badge_type', 'info')
    is_pinned = 1 if request.form.get('is_pinned') else 0

    if not title or not content:
        flash("Le titre et le contenu de l'annonce sont obligatoires.", "danger")
        return redirect(request.referrer or url_for('index'))

    with db.get_db() as conn:
        conn.execute("""
            INSERT INTO announcements (class_id, title, content, badge_type, is_pinned)
            VALUES (?, ?, ?, ?, ?)
        """, (class_id, title, content, badge_type, is_pinned))

    flash("Information publiée avec succès !", "success")
    return redirect(request.referrer or url_for('index'))


@app.route('/admin/annonces/<int:announcement_id>/modifier', methods=['POST'])
@admin_required
def edit_announcement(announcement_id):
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    badge_type = request.form.get('badge_type', 'info')
    is_pinned = 1 if request.form.get('is_pinned') else 0

    with db.get_db() as conn:
        conn.execute("""
            UPDATE announcements 
            SET title = ?, content = ?, badge_type = ?, is_pinned = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title, content, badge_type, is_pinned, announcement_id))

    flash("Annonce mise à jour avec succès.", "success")
    return redirect(request.referrer or url_for('index'))


@app.route('/admin/annonces/<int:announcement_id>/supprimer', methods=['POST'])
@admin_required
def delete_announcement(announcement_id):
    with db.get_db() as conn:
        conn.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))
    flash("Annonce supprimée.", "success")
    return redirect(request.referrer or url_for('index'))


# Chapters Management
@app.route('/admin/chapitres/ajouter', methods=['POST'])
@admin_required
def add_chapter():
    class_id = int(request.form.get('class_id'))
    chapter_number = int(request.form.get('chapter_number', 1))
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    if not title:
        flash("Le titre du chapitre est requis.", "danger")
        return redirect(url_for('class_view', class_id=class_id))

    with db.get_db() as conn:
        conn.execute("""
            INSERT INTO chapters (class_id, chapter_number, title, description, display_order)
            VALUES (?, ?, ?, ?, ?)
        """, (class_id, chapter_number, title, description, chapter_number))

    flash(f"Chapitre {chapter_number} : {title} ajouté avec succès !", "success")
    return redirect(url_for('class_view', class_id=class_id))


@app.route('/admin/chapitres/<int:chapter_id>/modifier', methods=['POST'])
@admin_required
def edit_chapter(chapter_id):
    chapter_number = int(request.form.get('chapter_number', 1))
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    is_visible = 1 if request.form.get('is_visible') else 0

    with db.get_db() as conn:
        conn.execute("""
            UPDATE chapters 
            SET chapter_number = ?, title = ?, description = ?, is_visible = ?, display_order = ?
            WHERE id = ?
        """, (chapter_number, title, description, is_visible, chapter_number, chapter_id))

    flash("Chapitre modifié avec succès.", "success")
    return redirect(request.referrer or url_for('chapter_view', chapter_id=chapter_id))


@app.route('/admin/chapitres/<int:chapter_id>/supprimer', methods=['POST'])
@admin_required
def delete_chapter(chapter_id):
    chapter = db.get_chapter_by_id(chapter_id)
    class_id = chapter['class_id'] if chapter else None
    
    with db.get_db() as conn:
        conn.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))

    flash("Chapitre supprimé.", "success")
    if class_id:
        return redirect(url_for('class_view', class_id=class_id))
    return redirect(url_for('index'))


# Resources Management (PDFs, Images, Links)
@app.route('/admin/chapitres/<int:chapter_id>/ressources/ajouter', methods=['POST'])
@admin_required
def add_resource(chapter_id):
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'cours')
    resource_type = request.form.get('resource_type', 'file')
    description = request.form.get('description', '').strip()
    external_url = request.form.get('external_url', '').strip()

    if not title:
        flash("Le titre de la ressource est obligatoire.", "danger")
        return redirect(url_for('chapter_view', chapter_id=chapter_id))

    file_url = None
    file_size = 0

    if resource_type == 'link':
        if not external_url:
            flash("L'URL du lien internet est obligatoire.", "danger")
            return redirect(url_for('chapter_view', chapter_id=chapter_id))
        if not (external_url.startswith('http://') or external_url.startswith('https://')):
            external_url = 'https://' + external_url
        res_type = 'link'
    else:
        uploaded_file = request.files.get('file')
        if not uploaded_file or uploaded_file.filename == '':
            flash("Veuillez sélectionner un fichier (PDF, PNG, JPG, JPEG).", "danger")
            return redirect(url_for('chapter_view', chapter_id=chapter_id))

        saved_file = storage.save_uploaded_file(uploaded_file, folder_category='documents', custom_prefix='doc_')
        if not saved_file:
            flash("Format de fichier non pris en charge. Formats acceptés : PDF, PNG, JPG, JPEG, WEBP.", "danger")
            return redirect(url_for('chapter_view', chapter_id=chapter_id))

        file_url = saved_file['url']
        file_size = saved_file['size']
        res_type = saved_file['file_type']

    with db.get_db() as conn:
        conn.execute("""
            INSERT INTO resources (chapter_id, title, category, resource_type, file_url, file_size, external_url, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (chapter_id, title, category, res_type, file_url, file_size, external_url, description))

    flash("Ressource ajoutée avec succès au chapitre !", "success")
    return redirect(url_for('chapter_view', chapter_id=chapter_id))


@app.route('/admin/ressources/<int:resource_id>/supprimer', methods=['POST'])
@admin_required
def delete_resource(resource_id):
    with db.get_db() as conn:
        conn.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
    flash("Ressource supprimée avec succès.", "success")
    return redirect(request.referrer or url_for('index'))


# -------------------------------------------------------------------
# Site Settings & End of Year Transition (Fin d'année & Réinitialisation)
# -------------------------------------------------------------------
@app.route('/admin/parametres')
@admin_required
def admin_settings():
    """Settings page: edit school year, teacher name, site title, and end-of-year reset."""
    settings = db.get_all_settings()
    current_year = settings.get('school_year', '2026-2027')
    
    # Calculate next recommended school year (e.g. 2026-2027 -> 2027-2028)
    next_year_str = "2027-2028"
    try:
        parts = current_year.split('-')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            y1 = int(parts[0]) + 1
            y2 = int(parts[1]) + 1
            next_year_str = f"{y1}-{y2}"
    except Exception:
        next_year_str = "2027-2028"

    # Statistics for the admin
    stats = {}
    with db.get_db() as conn:
        stats['submissions_count'] = conn.execute("SELECT COUNT(*) as c FROM student_submissions").fetchone()['c']
        stats['announcements_count'] = conn.execute("SELECT COUNT(*) as c FROM announcements").fetchone()['c']
        stats['resources_count'] = conn.execute("SELECT COUNT(*) as c FROM resources").fetchone()['c']
        stats['chapters_count'] = conn.execute("SELECT COUNT(*) as c FROM chapters").fetchone()['c']
        stats['classes_count'] = conn.execute("SELECT COUNT(*) as c FROM classes").fetchone()['c']

    return render_template(
        'admin_settings.html', 
        settings=settings, 
        next_year_str=next_year_str,
        stats=stats
    )


@app.route('/admin/parametres/modifier', methods=['POST'])
@admin_required
def update_site_settings():
    """Save updated school year, teacher name, and site title."""
    school_year = request.form.get('school_year', '').strip()
    teacher_name = request.form.get('teacher_name', '').strip()
    site_title = request.form.get('site_title', '').strip()

    if school_year:
        db.set_setting('school_year', school_year)
    if teacher_name:
        db.set_setting('teacher_name', teacher_name)
    if site_title:
        db.set_setting('site_title', site_title)

    flash("Paramètres du site mis à jour avec succès !", "success")
    return redirect(url_for('admin_settings'))


@app.route('/admin/reinitialisation-fin-annee', methods=['POST'])
@admin_required
def reset_end_of_year_action():
    """Execute end-of-year reset in one click."""
    new_school_year = request.form.get('new_school_year', '').strip()
    reset_type = request.form.get('reset_type', 'standard')
    confirmation_text = request.form.get('confirmation_text', '').strip()

    # Safety check
    if confirmation_text.upper() != 'REINITIALISER':
        flash("La réinitialisation a été annulée : vous devez taper 'REINITIALISER' pour confirmer.", "danger")
        return redirect(url_for('admin_settings'))

    if not new_school_year:
        new_school_year = db.get_setting('school_year', '2026-2027')

    res = db.reset_end_of_year(new_school_year, reset_type=reset_type)
    flash(res['message'], "success")
    return redirect(url_for('admin_settings'))


# -------------------------------------------------------------------
# Error Handlers
# -------------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(413)
def request_entity_too_large(error):
    flash("Le fichier est trop volumineux (limite maximale : 32 Mo).", "danger")
    return redirect(request.referrer or url_for('index'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
