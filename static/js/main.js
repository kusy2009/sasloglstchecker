// Main JavaScript file for SAS Log and LST Checker

document.addEventListener('DOMContentLoaded', function() {
    // File upload form handling
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        initializeUploadForm();
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Initialize the file upload form
function initializeUploadForm() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    const uploadButton = document.getElementById('uploadButton');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadError = document.getElementById('uploadError');
    const errorMessage = document.getElementById('errorMessage');
    
    // Add drag and drop functionality
    const uploadArea = uploadForm;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadArea.classList.add('border-primary');
    }
    
    function unhighlight() {
        uploadArea.classList.remove('border-primary');
    }
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            // Update file input label
            const fileName = fileInput.files[0].name;
            const fileLabel = document.querySelector('.form-file-text');
            if (fileLabel) {
                fileLabel.textContent = fileName;
            }
        }
    }
    
    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate file input
        if (fileInput.files.length === 0) {
            errorMessage.textContent = 'Please select a file to upload.';
            uploadError.classList.remove('d-none');
            return;
        }
        
        // Show progress and disable button
        uploadProgress.classList.remove('d-none');
        uploadButton.disabled = true;
        uploadError.classList.add('d-none');
        
        // Create FormData object
        const formData = new FormData(uploadForm);
        
        // Send AJAX request
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Redirect to results page
                window.location.href = data.redirect;
            } else {
                // Show error
                errorMessage.textContent = data.error || 'An error occurred during processing.';
                uploadError.classList.remove('d-none');
                uploadProgress.classList.add('d-none');
                uploadButton.disabled = false;
            }
        })
        .catch(error => {
            // Show error
            errorMessage.textContent = 'An error occurred during upload: ' + error.message;
            uploadError.classList.remove('d-none');
            uploadProgress.classList.add('d-none');
            uploadButton.disabled = false;
        });
    });
}

// Table sorting functionality
function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Get current sort direction
    const th = table.querySelector(`th:nth-child(${columnIndex + 1})`);
    const currentDirection = th.getAttribute('data-sort-direction') || 'asc';
    const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
    
    // Update all headers to remove sort indicators
    table.querySelectorAll('th').forEach(header => {
        header.removeAttribute('data-sort-direction');
        header.querySelector('.sort-icon')?.remove();
    });
    
    // Add sort indicator to current header
    th.setAttribute('data-sort-direction', newDirection);
    const sortIcon = document.createElement('span');
    sortIcon.className = 'sort-icon ms-1';
    sortIcon.innerHTML = newDirection === 'asc' ? '↑' : '↓';
    th.appendChild(sortIcon);
    
    // Sort the rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Check if values are numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return newDirection === 'asc' ? aNum - bNum : bNum - aNum;
        }
        
        // Sort as strings
        return newDirection === 'asc' 
            ? aValue.localeCompare(bValue) 
            : bValue.localeCompare(aValue);
    });
    
    // Reorder the rows
    rows.forEach(row => tbody.appendChild(row));
}

// Filter table rows based on search input
function filterTable(tableId, query) {
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    
    query = query.toLowerCase();
    
    // Start from index 1 to skip header row
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const text = row.textContent.toLowerCase();
        
        if (text.indexOf(query) > -1) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    }
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tr');
    
    // CSV content
    let csv = [];
    
    for (let i = 0; i < rows.length; i++) {
        const row = [], cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            // Get text content and handle special cases
            let text = cols[j].textContent.trim();
            
            // Replace commas and quotes to avoid CSV issues
            text = text.replace(/"/g, '""');
            
            // Add quotes around the field
            row.push('"' + text + '"');
        }
        
        csv.push(row.join(','));
    }
    
    // Download CSV file
    downloadCSV(csv.join('\n'), filename);
}

// Download CSV helper function
function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], {type: 'text/csv'});
    const downloadLink = document.createElement('a');
    
    // Set file name
    downloadLink.download = filename;
    
    // Create a link to the file
    downloadLink.href = window.URL.createObjectURL(csvFile);
    
    // Hide download link
    downloadLink.style.display = 'none';
    
    // Add the link to DOM
    document.body.appendChild(downloadLink);
    
    // Click download link
    downloadLink.click();
    
    // Clean up
    document.body.removeChild(downloadLink);
}
