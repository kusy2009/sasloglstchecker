"""
LST file processing module for the SAS Log and LST Check Web Application.
Implements the logic from the chklst SAS macro.
"""
import os
import re
import pandas as pd
from config import LST_COMPARE_PATTERNS

class LstProcessor:
    """Process SAS lst files and identify comparison results."""
    
    def __init__(self):
        """Initialize the lst processor."""
        self.patterns = LST_COMPARE_PATTERNS
    
    def process_file(self, file_path):
        """Process a single lst file and return the results."""
        filename = os.path.basename(file_path)
        has_compare = False
        status = "NO COMPARE"
        status_color = "#808080"  # Gray for no compare
        base_vars = None
        base_obs = None
        comp_vars = None
        comp_obs = None
        criterion = "N/A"
        messages = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
                # Check if file contains COMPARE Procedure
                if self.patterns['COMPARE_PROC'] in content:
                    has_compare = True
                    
                    # Extract criterion value if present
                    criterion_match = re.search(r'Criterion=([0-9.]+)', content)
                    if criterion_match:
                        criterion = criterion_match.group(1)
                    
                    # Check for equal values message
                    if self.patterns['EQUAL_VALUES'] in content:
                        status = "PASS"
                        status_color = "#00FF00"  # Green for pass
                        messages.append(self.patterns['EQUAL_VALUES'])
                    
                    # Check for unequal variables zero message
                    if self.patterns['UNEQUAL_VARS_ZERO'] in content:
                        if status != "PASS":
                            status = "PASS"
                            status_color = "#00FF00"
                        messages.append(self.patterns['UNEQUAL_VARS_ZERO'])
                    
                    # Check for unequal values zero message
                    if self.patterns['UNEQUAL_VALUES_ZERO'] in content:
                        if status != "PASS":
                            status = "PASS"
                            status_color = "#00FF00"
                        messages.append(self.patterns['UNEQUAL_VALUES_ZERO'])
                    
                    # If no pass messages found, mark as not pass
                    if status == "NO COMPARE":
                        status = "NOT PASS"
                        status_color = "#FF0000"  # Red for not pass
                    
                    # Try to extract base and comparison statistics
                    # This is a simplified version of the complex extraction in the SAS macro
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "Variables Summary" in line and i >= 4:
                            # Look for lines with statistics before the Variables Summary
                            for j in range(max(0, i-5), i):
                                if "Number of Variables" in lines[j] and "Number of Observations" in lines[j]:
                                    parts = lines[j].split()
                                    if len(parts) >= 6:
                                        try:
                                            if "Base Dataset" in lines[j-1]:
                                                base_vars = int(parts[-2])
                                                base_obs = int(parts[-1])
                                            elif "Compare Dataset" in lines[j-1]:
                                                comp_vars = int(parts[-2])
                                                comp_obs = int(parts[-1])
                                        except (ValueError, IndexError):
                                            pass
                else:
                    status = "NO COMPARE"
                    messages.append("No COMPARE Procedure found in file")
        
        except Exception as e:
            status = "ERROR"
            status_color = "#FF0000"
            messages.append(f"Error processing file: {str(e)}")
        
        return {
            'filename': filename,
            'has_compare': has_compare,
            'status': status,
            'status_color': status_color,
            'base_vars': base_vars,
            'base_obs': base_obs,
            'comp_vars': comp_vars,
            'comp_obs': comp_obs,
            'criterion': criterion,
            'messages': messages
        }
    
    def process_directory(self, directory):
        """Process all lst files in a directory and return the results."""
        results = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.lst'):
                    file_path = os.path.join(root, file)
                    result = self.process_file(file_path)
                    results.append(result)
        
        return results
    
    def generate_summary(self, results):
        """Generate a summary of all processed lst files."""
        total_files = len(results)
        pass_files = sum(1 for r in results if r['status'] == 'PASS')
        not_pass_files = sum(1 for r in results if r['status'] == 'NOT PASS')
        no_compare_files = sum(1 for r in results if r['status'] == 'NO COMPARE')
        error_files = sum(1 for r in results if r['status'] == 'ERROR')
        
        return {
            'total_files': total_files,
            'pass_files': pass_files,
            'not_pass_files': not_pass_files,
            'no_compare_files': no_compare_files,
            'error_files': error_files
        }
    
    def to_dataframe(self, results):
        """Convert results to a pandas DataFrame for easier manipulation."""
        data = []
        
        for result in results:
            row = {
                'filename': result['filename'],
                'has_compare': result['has_compare'],
                'status': result['status'],
                'base_vars': result['base_vars'],
                'base_obs': result['base_obs'],
                'comp_vars': result['comp_vars'],
                'comp_obs': result['comp_obs'],
                'criterion': result['criterion']
            }
            data.append(row)
        
        return pd.DataFrame(data)
