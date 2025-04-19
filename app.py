"""
Main Flask application for the SAS Log and LST Check Web Application.
"""
import os
import json
from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, url_for, session
from werkzeug.utils import secure_filename
import pandas as pd

from config import DEBUG, SECRET_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
from file_utils import save_uploaded_file, extract_zip, get_files_by_extension, cleanup_temp_files, create_result_id, process_directory_path
from log_processor import LogProcessor
from lst_processor import LstProcessor

# Initialize Flask application
app = Flask(__name__)
app.config['DEBUG'] = DEBUG
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage for processing results
# In a production app, this would be a database
processing_results = {}

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and process them."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    custom_keyword = request.form.get('custom_keyword', 'ALERT')
    
    # Save the uploaded file
    file_path = save_uploaded_file(file)
    if not file_path:
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Process the file based on its type
    result_id = create_result_id()
    
    try:
        if file_path.lower().endswith('.zip'):
            # Extract the zip file
            extract_dir = extract_zip(file_path)
            
            # Process log files
            log_processor = LogProcessor(custom_keyword=custom_keyword)
            log_results = log_processor.process_directory(extract_dir)
            log_summary = log_processor.generate_summary(log_results)
            
            # Process lst files
            lst_processor = LstProcessor()
            lst_results = lst_processor.process_directory(extract_dir)
            lst_summary = lst_processor.generate_summary(lst_results)
            
            # Store results
            processing_results[result_id] = {
                'log_results': log_results,
                'log_summary': log_summary,
                'lst_results': lst_results,
                'lst_summary': lst_summary
            }
            
            # Clean up temporary files
            cleanup_temp_files(extract_dir)
            os.remove(file_path)
            
        elif file_path.lower().endswith('.log'):
            # Process single log file
            log_processor = LogProcessor(custom_keyword=custom_keyword)
            log_result = log_processor.process_file(file_path)
            log_results = [log_result]
            log_summary = {
                'total_files': 1,
                'clean_files': 1 if log_result['status'] == 'CLEAN' else 0,
                'error_files': 1 if log_result['status'] == 'ERROR' else 0,
                'warning_files': 1 if log_result['status'] == 'WARNING' else 0,
                'issue_files': 1 if log_result['status'] == 'ISSUE' else 0,
                'total_errors': log_result['summary']['error_count'],
                'total_warnings': log_result['summary']['warning_count'],
                'total_alerts': log_result['summary']['alert_count'],
                'total_others': log_result['summary']['other_count'],
                'total_issues': log_result['summary']['total_issues']
            }
            
            # Store results
            processing_results[result_id] = {
                'log_results': log_results,
                'log_summary': log_summary,
                'lst_results': [],
                'lst_summary': {
                    'total_files': 0,
                    'pass_files': 0,
                    'not_pass_files': 0,
                    'no_compare_files': 0,
                    'error_files': 0
                }
            }
            
            # Clean up temporary files
            os.remove(file_path)
            
        elif file_path.lower().endswith('.lst'):
            # Process single lst file
            lst_processor = LstProcessor()
            lst_result = lst_processor.process_file(file_path)
            lst_results = [lst_result]
            lst_summary = {
                'total_files': 1,
                'pass_files': 1 if lst_result['status'] == 'PASS' else 0,
                'not_pass_files': 1 if lst_result['status'] == 'NOT PASS' else 0,
                'no_compare_files': 1 if lst_result['status'] == 'NO COMPARE' else 0,
                'error_files': 1 if lst_result['status'] == 'ERROR' else 0
            }
            
            # Store results
            processing_results[result_id] = {
                'log_results': [],
                'log_summary': {
                    'total_files': 0,
                    'clean_files': 0,
                    'error_files': 0,
                    'warning_files': 0,
                    'issue_files': 0,
                    'total_errors': 0,
                    'total_warnings': 0,
                    'total_alerts': 0,
                    'total_others': 0,
                    'total_issues': 0
                },
                'lst_results': lst_results,
                'lst_summary': lst_summary
            }
            
            # Clean up temporary files
            os.remove(file_path)
        
        return jsonify({
            'success': True,
            'result_id': result_id,
            'redirect': url_for('results', result_id=result_id)
        })
        
    except Exception as e:
        # Clean up any temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({'error': str(e)}), 500

@app.route('/process_directory', methods=['POST'])
def process_directory():
    """Process all files in a specified directory path."""
    # Get directory path and custom keyword from request
    data = request.json
    if not data or 'directory_path' not in data:
        return jsonify({'error': 'No directory path provided'}), 400
    
    directory_path = data['directory_path']
    custom_keyword = data.get('custom_keyword', 'ALERT')
    
    # Create a result ID
    result_id = create_result_id()
    
    try:
        # Process the directory
        temp_dir, log_count, lst_count = process_directory_path(directory_path)
        
        if log_count == 0 and lst_count == 0:
            cleanup_temp_files(temp_dir)
            return jsonify({'error': 'No .log or .lst files found in the specified directory'}), 400
        
        # Process log files
        log_processor = LogProcessor(custom_keyword=custom_keyword)
        log_results = log_processor.process_directory(temp_dir)
        log_summary = log_processor.generate_summary(log_results)
        
        # Process lst files
        lst_processor = LstProcessor()
        lst_results = lst_processor.process_directory(temp_dir)
        lst_summary = lst_processor.generate_summary(lst_results)
        
        # Store results
        processing_results[result_id] = {
            'log_results': log_results,
            'log_summary': log_summary,
            'lst_results': lst_results,
            'lst_summary': lst_summary
        }
        
        # Clean up temporary files
        cleanup_temp_files(temp_dir)
        
        return jsonify({
            'success': True,
            'result_id': result_id,
            'redirect': url_for('results', result_id=result_id),
            'log_count': log_count,
            'lst_count': lst_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<result_id>')
def results(result_id):
    """Display processing results."""
    if result_id not in processing_results:
        return redirect(url_for('index'))
    
    return render_template('results.html', result_id=result_id)

@app.route('/api/results/<result_id>')
def api_results(result_id):
    """API endpoint to get processing results."""
    if result_id not in processing_results:
        return jsonify({'error': 'Result not found'}), 404
    
    return jsonify(processing_results[result_id])

@app.route('/api/log_details/<result_id>/<filename>')
def api_log_details(result_id, filename):
    """API endpoint to get detailed log results for a specific file."""
    if result_id not in processing_results:
        return jsonify({'error': 'Result not found'}), 404
    
    log_results = processing_results[result_id]['log_results']
    for result in log_results:
        if result['filename'] == filename:
            return jsonify(result)
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/lst_details/<result_id>/<filename>')
def api_lst_details(result_id, filename):
    """API endpoint to get detailed lst results for a specific file."""
    if result_id not in processing_results:
        return jsonify({'error': 'Result not found'}), 404
    
    lst_results = processing_results[result_id]['lst_results']
    for result in lst_results:
        if result['filename'] == filename:
            return jsonify(result)
    
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
