const socket = io();
const decoder = new TextDecoder();

window.onload = function() {
    socket.on('uniqueid', function(response) {
        document.cookie = "chat_hys_uid=" + response.uniqueid + ';SameSite=Lax';
    });
    socket.emit('uniqueid');
};