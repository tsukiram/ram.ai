document.getElementById('generate-form').addEventListener('submit', function(e) {
    e.preventDefault();
    let formData = new FormData(this);
    let progressBar = document.getElementById('progress-bar');
    let statusDiv = document.getElementById('status');
    let resultDiv = document.getElementById('result');
    let websiteName = document.getElementById('website-name');
    let description = document.getElementById('description');
    let downloadLink = document.getElementById('download-link');

    progressBar.style.width = '0%';
    statusDiv.innerHTML = '';
    resultDiv.style.display = 'none';
    downloadLink.style.display = 'none';

    fetch('/generate', {
        method: 'POST',
        body: formData
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        return reader.read().then(function processResult({ done, value }) {
            if (done) return;
            const chunk = decoder.decode(value, { stream: true });
            const data = JSON.parse(chunk.split("\n\n").filter(Boolean).pop().substring(5));
            if (data.step) {
                progressBar.style.width = (data.step * 20) + '%';
                statusDiv.innerHTML = data.message;
            } else if (data.website_name) {
                progressBar.style.width = '100%';
                websiteName.innerHTML = "Website Name: " + data.website_name;
                description.innerHTML = "Description: " + data.description;
                resultDiv.style.display = 'block';
                downloadLink.style.display = 'inline-block';
            }
            return reader.read().then(processResult);
        });
    }).catch(err => {
        statusDiv.innerHTML = 'Error occurred during generation.';
    });
});