// static/js/messages.js
function initializeMessages() {
    const messages = document.querySelectorAll('[id^="message-"]');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 3000);
    });
}

document.addEventListener('DOMContentLoaded', initializeMessages);