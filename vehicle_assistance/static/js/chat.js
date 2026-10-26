document.addEventListener('DOMContentLoaded', function () {
    var toggle = document.getElementById('chatToggle');
    var panel = document.getElementById('chatWindow');
    var closeButton = document.getElementById('chatClose');
    var input = document.getElementById('chatInput');
    var sendButton = document.getElementById('chatSend');
    var messagesList = document.getElementById('chatMessages');
    var widget = document.getElementById('chatbotWidget');

    if (!toggle || !panel || !input || !sendButton || !messagesList) {
        return;
    }

    function getTimeLabel() {
        return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
    }

    function addMessage(text, senderType) {
        var quickReplies = messagesList.querySelector('.quick-replies');
        if (quickReplies) quickReplies.remove();

        var row = document.createElement('div');
        row.className = 'message ' + senderType + '-message';
        row.innerHTML = '<p>' + text + '</p><span class="message-time">' + getTimeLabel() + '</span>';
        messagesList.appendChild(row);
        messagesList.scrollTop = messagesList.scrollHeight;
    }

    function showTypingIndicator() {
        if (document.getElementById('typingIndicator')) return;
        var indicator = document.createElement('div');
        indicator.id = 'typingIndicator';
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';
        messagesList.appendChild(indicator);
        messagesList.scrollTop = messagesList.scrollHeight;
    }

    function hideTypingIndicator() {
        var indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }

    function closeChat() {
        panel.classList.remove('active');
    }

    async function sendMessage() {
        var message = input.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        input.value = '';
        showTypingIndicator();

        try {
            var response = await fetch('/user/send-message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message }),
            });

            hideTypingIndicator();
            var data = response.ok ? await response.json() : null;
            var botResponse = data && data.response ? data.response : 'Service is temporarily unavailable. Please try again.';
            addMessage(botResponse, 'bot');
        } catch (error) {
            hideTypingIndicator();
            addMessage('Service is temporarily unavailable. Please try again.', 'bot');
        }
    }

    toggle.addEventListener('click', function (event) {
        event.preventDefault();
        event.stopPropagation();
        panel.classList.toggle('active');
        if (panel.classList.contains('active')) input.focus();
    });

    if (closeButton) {
        closeButton.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            closeChat();
        });
    }

    sendButton.addEventListener('click', function (event) {
        event.preventDefault();
        sendMessage();
    });

    input.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });

    window.sendQuickReply = function (text) {
        input.value = text;
        sendMessage();
    };

    document.addEventListener('click', function (event) {
        if (widget && !widget.contains(event.target)) {
            closeChat();
        }
    });
});
