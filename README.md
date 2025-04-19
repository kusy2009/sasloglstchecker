# SAS Log and LST Checker Web Application

A Python-based web application for analyzing SAS log and list files based on the logic from SAS macros.

## Features

- Upload and process SAS log (.log) and list (.lst) files
- Support for individual files or zip archives containing multiple files
- Analyze log files for errors, warnings, alerts, and other issues
- Analyze list files for COMPARE procedure results
- Interactive results display with filtering and sorting
- Detailed view of issues for each file
- Summary statistics and visualizations
- Responsive design for desktop and mobile devices

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository
```bash
https://github.com/kusy2009/sasloglstchecker.git
```

2. Navigate to the project directory
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

1. Navigate to the project directory
2. Start the Flask application:

```bash
python app.py
```

3. Open a web browser and go to `http://localhost:5000`

### Using the Application

1. **Upload Files**: 
   - Click the "Upload and Process" button to select SAS log (.log) and list (.lst) files
   - You can upload individual files or a zip archive containing multiple files
   - Optionally, specify a custom keyword to search for in log files (default: ALERT)

2. **View Results**:
   - After processing, you'll be redirected to the results page
   - The Summary tab shows overall statistics and charts
   - The Log Files tab shows details for each log file
   - The LST Files tab shows details for each list file

3. **Explore Details**:
   - Click the "View" button for any file to see detailed information
   - For log files, you'll see all issues found with line numbers
   - For list files, you'll see comparison results and statistics

## Implementation Details

### Backend

- Built with Flask (Python web framework)
- Log file processing based on the `%chklog` SAS macro
- LST file processing based on the `%chklst` SAS macro
- RESTful API endpoints for file upload and results retrieval

### Frontend

- Responsive design using Bootstrap 5
- Interactive charts with Chart.js
- Dynamic content loading with JavaScript
- Filtering and sorting capabilities

## Testing

The application includes a test script that verifies all functionality:

```bash
python test_app.py
```

This script:
- Creates sample log and lst files
- Tests file uploads (individual files and zip archives)
- Verifies API endpoints
- Checks results processing

## Deployment

For production deployment:

1. Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. Consider using a reverse proxy like Nginx for better performance and security

## File Structure

```
sas_checker/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── file_utils.py          # File handling utilities
├── log_processor.py       # Log file processing module
├── lst_processor.py       # LST file processing module
├── test_app.py            # Test script
├── static/                # Static files
│   ├── css/               # CSS stylesheets
│   │   └── styles.css     # Custom styles
│   └── js/                # JavaScript files
│       └── main.js        # Main JavaScript functionality
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page template
│   └── results.html       # Results page template
└── uploads/               # Upload directory for files
    ├── sample_log.log     # Sample log file for testing
    └── sample_lst.lst     # Sample list file for testing
```

## Customization

- Modify `config.py` to change application settings
- Add or modify patterns in `LOG_PATTERNS` and `LST_COMPARE_PATTERNS` to adjust detection logic
- Customize the UI by modifying the templates and CSS

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This application implements the logic from the following SAS macros developed by Wei Shao:
- `%chklog` - For checking SAS log files
- `%chklst` - For checking SAS list files
