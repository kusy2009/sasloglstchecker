"""
Utility functions for file operations in the SAS Log and LST Check Web Application.
"""
import os
import re
import zipfile
import tempfile
import shutil
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Save an uploaded file to the upload folder."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filepath
    return None

def extract_zip(zip_path):
    """Extract a zip file to a temporary directory and return the path."""
    temp_dir = tempfile.mkdtemp(dir=UPLOAD_FOLDER)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    return temp_dir

def get_files_by_extension(directory, extension):
    """Get all files with a specific extension in a directory."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(f'.{extension}'):
                files.append(os.path.join(root, filename))
    return files

def cleanup_temp_files(directory):
    """Clean up temporary files and directories."""
    if os.path.exists(directory) and os.path.isdir(directory):
        shutil.rmtree(directory)

def get_relative_path(file_path, base_dir):
    """Get the relative path of a file from a base directory."""
    return os.path.relpath(file_path, base_dir)

def create_result_id():
    """Create a unique ID for a processing result."""
    import uuid
    return str(uuid.uuid4())

def process_directory_path(directory_path):
    """
    Process all files in a given directory path.
    Creates a temporary directory and copies all valid files to it.
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise ValueError(f"Invalid directory path: {directory_path}")
    
    # Create a temporary directory to store the files
    temp_dir = tempfile.mkdtemp(dir=UPLOAD_FOLDER)
    
    # Get all log and lst files in the directory
    log_files = get_files_by_extension(directory_path, 'log')
    lst_files = get_files_by_extension(directory_path, 'lst')
    
    # Copy files to the temporary directory
    for file_path in log_files + lst_files:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(temp_dir, filename)
        shutil.copy2(file_path, dest_path)
    
    return temp_dir, len(log_files), len(lst_files)
