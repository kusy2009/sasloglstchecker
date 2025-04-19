"""
Modified configuration for cloud deployment.
"""
import os

# Application settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'log', 'lst', 'zip'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload size

# Processing settings
LOG_PATTERNS = {
    'ERROR': {'pattern': 'ERROR:', 'color': '#FF0000'},
    'WARNING': {'pattern': 'WARNING:', 'color': '#A05000'},
    'ALERT': {'pattern': 'ALERT:', 'color': '#0000FF'},
    'UNINITIALIZED': {'pattern': 'uninitialized', 'color': '#FF6600'},
    'MERGE': {'pattern': 'MERGE statement has more than one data set', 'color': '#FF6600'},
    'MISSING': {'pattern': 'Missing values were generated', 'color': '#FF6600'},
    'CHARACTER': {'pattern': 'Character values', 'color': '#FF6600'},
    'NUMERIC': {'pattern': 'Numeric values', 'color': '#FF6600'},
    'OVERWRITTEN': {'pattern': 'will be overwritten by', 'color': '#FF6600'},
    'DEFAULT_LENGTH': {'pattern': 'Character variables have defaulted to a length of 200', 'color': '#FF6600'},
    'NOT_FOUND': {'pattern': 'was not found or could not be loaded', 'color': '#FF6600'},
    'MATH_ERROR': {'pattern': 'Mathematical operations could not', 'color': '#FF6600'},
    'WHERE_REPLACED': {'pattern': 'WHERE clause has been replaced', 'color': '#FF6600'},
    'FORMAT': {'pattern': 'W.D format', 'color': '#FF6600'},
    'AXIS_RANGE': {'pattern': 'outside the axis range', 'color': '#FF6600'},
}

LST_COMPARE_PATTERNS = {
    'COMPARE_PROC': 'COMPARE Procedure',
    'EQUAL_VALUES': 'NOTE: No unequal values were found. All values compared are exactly equal.',
    'UNEQUAL_VARS_ZERO': 'Number of Variables Compared with Some Observations Unequal: 0.',
    'UNEQUAL_VALUES_ZERO': 'Total Number of Values which Compare Unequal: 0.',
    'CRITERION': 'Criterion='
}
