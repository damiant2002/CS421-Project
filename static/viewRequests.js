document.addEventListener('DOMContentLoaded', () => {
    const requestsList = document.getElementById('requestsList');

    fetch('/view_requests')
        .then(response => response.json())
        .then(requests => {
            requests.forEach((request, index) => {
                // Create list item for each request
                const listItem = document.createElement('li');
                
                // Add request details and delete button
                listItem.innerHTML = `
                    ${request.name} - ${request.date}: ${request.reason} 
                    <button class="delete-button" data-id="${index}">Delete</button>`;
                
                // Append the list item to the requests list
                requestsList.appendChild(listItem);
            });
            document.querySelectorAll('.delete-button').forEach(button => {
                button.addEventListener('click', (event) => {
                    const id = event.target.getAttribute('data-id');
                    console.log('Deleting request with ID:', id); // Debugging line
                    
                    fetch('/delete_request', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: new URLSearchParams({ 'id': id })
                    })
                    .then(response => {
                        if (response.ok) {
                            location.reload();
                        } else {
                            console.error('Error deleting request:', response.statusText);
                        }
                    })
                    .catch(error => console.error('Error deleting request:', error));
                });
                
            });
        })
        .catch(error => console.error('Error fetching requests:', error));
});
