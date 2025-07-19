// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize any other global JavaScript functionality
});

// Function to update 3D visualization based on filters
function updateRiskVisualization(filters) {
    // This would make an AJAX call to get updated data based on filters
    console.log("Updating visualization with filters:", filters);
    
    // In a real implementation, you would:
    // 1. Make an AJAX call to get updated data
    // 2. Update the Three.js scene with new data
}

// Function to handle form submissions asynchronously
function handleFilterFormSubmit(formId, callback) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const params = new URLSearchParams(formData);
        
        fetch(`${form.action}?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                if (callback && typeof callback === 'function') {
                    callback(data);
                }
            })
            .catch(error => console.error('Error:', error));
    });
}

// Example usage for the risk filter form
document.addEventListener('DOMContentLoaded', function() {
    handleFilterFormSubmit('risk-filter-form', function(data) {
        updateRiskVisualization(data.filters);
    });
    
    // Initialize any other page-specific JavaScript
});