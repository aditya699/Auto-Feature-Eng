document.getElementById('file-upload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    document.getElementById('status').textContent = 'Uploading and processing...';
    document.getElementById('error-message').textContent = '';
    showLoading();

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        document.getElementById('status').textContent = 'Dashboard generated!';
        console.log('Received D3.js code:', data.d3_code);

        // Clear previous dashboard and filter
        document.getElementById('dashboard').innerHTML = '';
        document.getElementById('filter').innerHTML = '';

        // Create a script element and append the D3.js code
        const script = document.createElement('script');
        script.textContent = data.d3_code;
        document.body.appendChild(script);

        // Check if the dashboard was actually created
        setTimeout(() => {
            if (document.getElementById('dashboard').children.length === 0) {
                throw new Error('Dashboard was not created. Check the console for D3.js errors.');
            }
        }, 1000);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('status').textContent = 'Error generating dashboard. Please try again.';
        document.getElementById('error-message').textContent = error.message || 'An unexpected error occurred.';
    })
    .finally(() => {
        hideLoading();
    });
});

function showLoading() {
    const loading = document.createElement('div');
    loading.className = 'loading';
    document.body.appendChild(loading);
}

function hideLoading() {
    const loading = document.querySelector('.loading');
    if (loading) {
        loading.remove();
    }
}