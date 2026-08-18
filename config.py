import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'maths-gimenez-secret-key-2026-xyz894')

# Admin credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'dgimenez')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Cadolive+2406')

# Database
DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'site.db'))

# File Uploads
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp', 'gif'}
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max per upload request

# Optional Cloudinary Configuration (for 25 GB free cloud media storage)
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', '')

USE_CLOUDINARY = bool(CLOUDINARY_URL or (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET))

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'documents'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'exercises'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'solutions'), exist_ok=True)
