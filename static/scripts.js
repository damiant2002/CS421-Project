document.addEventListener('DOMContentLoaded', function() {
    // Check the local storage for each request and update the UI
    document.querySelectorAll('li[id^="request-"]').forEach(item => {
        const id = item.id.replace('request-', '');
        const status = localStorage.getItem(`request-${id}-status`);
        
        if (status === 'accepted') {
            item.innerHTML += '<span class="accepted">Accepted</span>';
            hideButtons(item);
        } else if (status === 'denied') {
            item.innerHTML += '<span class="denied">Denied</span>';
            hideButtons(item);
        }
    });
});

function acceptRequest(id) {
    const requestItem = document.getElementById(`request-${id}`);
    if (requestItem) {
        
        requestItem.innerHTML += '<span style="color: green; font-weight: bold;">Accepted</span>';
        hideButtons(requestItem);
        localStorage.setItem(`request-${id}-status`, 'accepted');
    }
}

function denyRequest(id) {
    const requestItem = document.getElementById(`request-${id}`);
    if (requestItem) {
        
        requestItem.innerHTML += '<span style="color: red; font-weight: bold;">Denied</span>';
        hideButtons(requestItem);
        localStorage.setItem(`request-${id}-status`, 'denied');
    }
}

function hideButtons(element) {
    const acceptButton = element.querySelector('.accept-button');
    const denyButton = element.querySelector('.deny-button');
    if (acceptButton) acceptButton.style.display = 'none';
    if (denyButton) denyButton.style.display = 'none';
}
