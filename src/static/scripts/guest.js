const socket = io();

window.onload = function() {
    const anonType = document.getElementById("anonType");
    const anonName = document.getElementById("anonName");
    
    document.getElementById("login").onclick = function() {
        if (anonName.value.length == 0) {
            alert("이름을 입력해 주세요");
        } else if (anonName.value.length < 4) {
            alert("더 긴 이름을 지어 주세요.");
        } else if (anonName.value.length > 10) {
            alert("더 짧은 이름을 지어 주세요.");
        } else if (anonName.checkValidity()) {
            sendEnterReq();
        } else {
            alert("올바른 이름을 입력해 주세요.");
        };
    };
    
    function sendEnterReq() {
        const data = {
            uniqueid: getUID(),
            usertype: anonType.selectedOptions[0].value,
            anonname: anonName.value,
            useragent: navigator.userAgent
        }
        console.log(data);
        
        socket.emit("guest_auth", data, receiveEnterReq);
    };
};

function receiveEnterReq(data) {
    if (!data.success) {
        alertOnFail(data)
    } else {
        window.location.href = "/chat";
    }
}
