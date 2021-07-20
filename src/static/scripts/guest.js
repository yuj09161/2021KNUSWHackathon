const socket = io();

window.onload = function() {
    var anonType = document.getElementById("anonType");
    var anonName = document.getElementById("anonName");
    
    document.getElementById("login").onclick = function() {
        if (anonName.value.length == 0) {
            alert("이름을 입력해 주세요");
        } else if (anonName.checkValidity()) {
            sendEnterReq();
        } else {
            alert("올바른 이름을 입력해 주세요.");
        }
    };

    
    function sendEnterReq() {
        var data = JSON.stringify({
            uniqueid: document.cookie.split('; ').find(cookie => cookie.startsWith('chat_hys_uid')).split('=')[1],
            user_type: anonType.selectedOptions[0].value,
            anon_name: anonName.value,
            user_agent: navigator.userAgent
        });
        console.log(data);
        
        socket.emit('guest_auth', data);
    };
};

socket.on('auth_respond', receiveEnterReq);
function receiveEnterReq(data) {
    console.log(data)
    if (!data.success) {
        alert(data.message)
        window.location.href = data.redirect;
        return;
    }
    window.location.href = '/chat';
}
