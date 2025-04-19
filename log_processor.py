"""
Log file processing module for the SAS Log and LST Check Web Application.
Implements the logic from the chklog SAS macro.
"""
import os
import re
import pandas as pd
from config import LOG_PATTERNS

class LogProcessor:
    """Process SAS log files and identify issues based on patterns."""
    
    def __init__(self, custom_keyword=None):
        """Initialize the log processor with optional custom keyword."""
        self.patterns = LOG_PATTERNS.copy()
        if custom_keyword:
            self.patterns['CUSTOM'] = {'pattern': custom_keyword, 'color': '#0000FF'}
    
    def process_file(self, file_path):
        """Process a single log file and return the results."""
        filename = os.path.basename(file_path)
        issues = []
        
        # Initialize counters for each pattern
        pattern_counts = {pattern_key: 0 for pattern_key in self.patterns.keys()}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                for line_num, line in enumerate(f, 1):
                    for pattern_key, pattern_info in self.patterns.items():
                        if pattern_info['pattern'] in line:
                            issues.append({
                                'type': pattern_key,
                                'message': line.strip(),
                                'line_number': line_num,
                                'color': pattern_info['color']
                            })
                            pattern_counts[pattern_key] += 1
        except Exception as e:
            issues.append({
                'type': 'PROCESSING_ERROR',
                'message': f"Error processing file: {str(e)}",
                'line_number': 0,
                'color': '#FF0000'
            })
        
        # Determine overall status
        if sum(pattern_counts.values()) == 0:
            status = 'CLEAN'
            status_color = '#00FF00'
        elif pattern_counts.get('ERROR', 0) > 0:
            status = 'ERROR'
            status_color = '#FF0000'
        elif pattern_counts.get('WARNING', 0) > 0:
            status = 'WARNING'
            status_color = '#A05000'
        else:
            status = 'ISSUE'
            status_color = '#FF6600'
        
        return {
            'filename': filename,
            'issues': issues,
            'status': status,
            'status_color': status_color,
            'summary': {
                'error_count': pattern_counts.get('ERROR', 0),
                'warning_count': pattern_counts.get('WARNING', 0),
                'alert_count': pattern_counts.get('ALERT', 0) + pattern_counts.get('CUSTOM', 0) if 'CUSTOM' in pattern_counts else pattern_counts.get('ALERT', 0),
                'other_count': sum(count for key, count in pattern_counts.items() 
                                  if key not in ['ERROR', 'WARNING', 'ALERT', 'CUSTOM']),
                'total_issues': sum(pattern_counts.values())
            }
        }
    
    def process_directory(self, directory):
        """Process all log files in a directory and return the results."""
        results = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.log'):
                    file_path = os.path.join(root, file)
                    result = self.process_file(file_path)
                    results.append(result)
        
        return results
    
    def generate_summary(self, results):
        """Generate a summary of all processed log files."""
        total_files = len(results)
        clean_files = sum(1 for r in results if r['status'] == 'CLEAN')
        error_files = sum(1 for r in results if r['status'] == 'ERROR')
        warning_files = sum(1 for r in results if r['status'] == 'WARNING')
        issue_files = sum(1 for r in results if r['status'] == 'ISSUE')
        
        total_errors = sum(r['summary']['error_count'] for r in results)
        total_warnings = sum(r['summary']['warning_count'] for r in results)
        total_alerts = sum(r['summary']['alert_count'] for r in results)
        total_others = sum(r['summary']['other_count'] for r in results)
        
        return {
            'total_files': total_files,
            'clean_files': clean_files,
            'error_files': error_files,
            'warning_files': warning_files,
            'issue_files': issue_files,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'total_alerts': total_alerts,
            'total_others': total_others,
            'total_issues': total_errors + total_warnings + total_alerts + total_others
        }
    
    def to_dataframe(self, results):
        """Convert results to a pandas DataFrame for easier manipulation."""
        data = []
        
        for result in results:
            row = {
                'filename': result['filename'],
                'status': result['status'],
                'error_count': result['summary']['error_count'],
                'warning_count': result['summary']['warning_count'],
                'alert_count': result['summary']['alert_count'],
                'other_count': result['summary']['other_count'],
                'total_issues': result['summary']['total_issues']
            }
            data.append(row)
        
        return pd.DataFrame(data)
