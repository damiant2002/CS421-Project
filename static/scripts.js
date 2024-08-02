function acceptRequest(requestId) {
    fetch(`/update_request/${requestId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: 'accepted' })
    }).then(response => {
        if (response.ok) {
            document.getElementById(`request-${requestId}`).style.backgroundColor = 'lightgreen';
        }
    });
}

function denyRequest(requestId) {
    fetch(`/update_request/${requestId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: 'denied' })
    }).then(response => {
        if (response.ok) {
            document.getElementById(`request-${requestId}`).style.backgroundColor = 'lightcoral';
        }
    });
}
