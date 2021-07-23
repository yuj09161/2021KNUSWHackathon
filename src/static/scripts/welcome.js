const socket = io();
const decoder = new TextDecoder();

window.onload = function() {
    socket.emit("uniqueid", response => {
        document.cookie = `chat_hys_uid=${response.uniqueid};SameSite=Lax`;
    });
};