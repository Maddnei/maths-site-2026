import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import config

# Initialize Cloudinary if available
if config.USE_CLOUDINARY:
    try:
        import cloudinary
        import cloudinary.uploader
        if config.CLOUDINARY_URL:
            cloudinary.config(cloudinary_url=config.CLOUDINARY_URL)
        else:
            cloudinary.config(
                cloud_name=config.CLOUDINARY_CLOUD_NAME,
                api_key=config.CLOUDINARY_API_KEY,
                api_secret=config.CLOUDINARY_API_SECRET,
                secure=True
            )
    except Exception as e:
        print(f"Warning: Cloudinary initialization failed: {e}")


def is_allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in config.ALLOWED_EXTENSIONS


def get_file_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def optimize_and_save_image(file_storage, dest_path, max_dimension=2000, quality=85):
    """
    Reads an uploaded image, corrects EXIF orientation (crucial for smartphone photos),
    resizes if larger than max_dimension, and saves optimized JPEG/PNG.
    """
    try:
        image = Image.open(file_storage)
        # Fix EXIF orientation from smartphones
        image = ImageOps.exif_transpose(image)
        
        # Convert RGBA to RGB if saving as JPEG
        if image.mode in ('RGBA', 'LA', 'P') and dest_path.lower().endswith(('.jpg', '.jpeg')):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode not in ('RGB', 'RGBA', 'L'):
            image = image.convert('RGB')
        
        # Resize if too large
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Save
        if dest_path.lower().endswith(('.jpg', '.jpeg')):
            image.save(dest_path, 'JPEG', quality=quality, optimize=True)
        elif dest_path.lower().endswith('.png'):
            image.save(dest_path, 'PNG', optimize=True)
        else:
            image.save(dest_path)
            
        return os.path.getsize(dest_path)
    except Exception as e:
        # Fallback to direct raw save if Pillow fails
        file_storage.seek(0)
        file_storage.save(dest_path)
        return os.path.getsize(dest_path)


def save_uploaded_file(file_storage, folder_category='documents', custom_prefix=''):
    """
    Saves an uploaded file either locally or on Cloudinary.
    Returns a dict with:
      - url: The relative or absolute URL to display/download the file
      - filename: Safe original or generated filename
      - size: File size in bytes
      - file_type: 'pdf' or 'image'
    """
    if not file_storage or file_storage.filename == '':
        return None

    orig_filename = secure_filename(file_storage.filename)
    ext = get_file_extension(orig_filename)
    if not ext or ext not in config.ALLOWED_EXTENSIONS:
        return None

    is_pdf = ext == 'pdf'
    file_type = 'pdf' if is_pdf else 'image'
    
    unique_id = str(uuid.uuid4())[:10]
    saved_name = f"{custom_prefix}{unique_id}_{orig_filename}" if orig_filename else f"{custom_prefix}{unique_id}.{ext}"

    # If Cloudinary is configured, upload to Cloudinary
    if config.USE_CLOUDINARY:
        try:
            # Cloudinary: Use 'image' for images and 'image' or 'raw' with flags
            # For PDF files in Cloudinary, upload as 'image' with format='pdf' OR 'raw' with access_mode='public'
            if is_pdf:
                resource_type = "raw"
                cloud_public_id = f"{custom_prefix}{unique_id}_{orig_filename}"
                upload_result = cloudinary.uploader.upload(
                    file_storage,
                    folder=f"site2026/{folder_category}",
                    public_id=cloud_public_id,
                    resource_type=resource_type,
                    type="upload",
                    access_mode="public"
                )
            else:
                resource_type = "image"
                cloud_public_id = f"{custom_prefix}{unique_id}"
                upload_result = cloudinary.uploader.upload(
                    file_storage,
                    folder=f"site2026/{folder_category}",
                    public_id=cloud_public_id,
                    resource_type=resource_type,
                    type="upload",
                    access_mode="public"
                )

            return {
                'url': upload_result.get('secure_url', upload_result.get('url')),
                'filename': orig_filename,
                'size': upload_result.get('bytes', 0),
                'file_type': file_type,
                'is_cloud': True
            }
        except Exception as e:
            print(f"Cloudinary upload error, falling back to local: {e}")
            file_storage.seek(0)

    # Local Storage fallback / default
    target_dir = os.path.join(config.UPLOAD_FOLDER, folder_category)
    os.makedirs(target_dir, exist_ok=True)
    local_path = os.path.join(target_dir, saved_name)

    if is_pdf:
        file_storage.seek(0)
        file_storage.save(local_path)
        file_size = os.path.getsize(local_path)
    else:
        file_storage.seek(0)
        file_size = optimize_and_save_image(file_storage, local_path)

    relative_url = f"/static/uploads/{folder_category}/{saved_name}"

    return {
        'url': relative_url,
        'filename': orig_filename,
        'size': file_size,
        'file_type': file_type,
        'is_cloud': False,
        'local_path': local_path
    }


def format_file_size(size_bytes):
    if not size_bytes:
        return "0 Ko"
    if size_bytes < 1024:
        return f"{size_bytes} o"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} Ko"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} Mo"


def delete_file_from_storage(file_url):
    """
    Deletes a file either from local disk or from Cloudinary
    when a resource or submission is deleted from the website,
    ensuring Cloudinary free quotas (25GB) are never exceeded.
    """
    if not file_url:
        return

    # 1. Local file deletion
    if file_url.startswith('/static/uploads/'):
        rel_path = file_url.replace('/static/uploads/', '')
        local_path = os.path.join(config.UPLOAD_FOLDER, rel_path)
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception as e:
                print(f"Error removing local file {local_path}: {e}")
        return

    # 2. Cloudinary deletion
    if config.USE_CLOUDINARY and 'cloudinary.com' in file_url:
        try:
            import cloudinary
            import cloudinary.uploader

            is_raw = '/raw/' in file_url
            resource_type = 'raw' if is_raw else 'image'

            if '/upload/' in file_url:
                after_upload = file_url.split('/upload/')[1]
                # Strip version like v1787068678/ if present
                if after_upload.startswith('v') and '/' in after_upload:
                    parts = after_upload.split('/', 1)
                    if parts[0][1:].isdigit():
                        after_upload = parts[1]
                
                # For raw files Cloudinary public_id has full name, for images without extension
                public_id = after_upload if is_raw else after_upload.rsplit('.', 1)[0]
                
                # Delete from Cloudinary
                res = cloudinary.uploader.destroy(public_id, resource_type=resource_type, invalidate=True)
                
                # If not found with inferred type and it was a pdf, try the alternate resource_type
                if res.get('result') != 'ok' and file_url.lower().endswith('.pdf'):
                    alt_type = 'raw' if resource_type == 'image' else 'image'
                    alt_public_id = after_upload if alt_type == 'raw' else after_upload.rsplit('.', 1)[0]
                    cloudinary.uploader.destroy(alt_public_id, resource_type=alt_type, invalidate=True)

                print(f"Purged {public_id} from Cloudinary")
        except Exception as e:
            print(f"Error deleting file from Cloudinary: {e}")

