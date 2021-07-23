const socket = io();
let username;
let password;

window.onload = function() {
    username = document.getElementById("username");
    password = document.getElementById("password");
    document.getElementById("login").onclick = sendLoginReq;
};

function sendLoginReq() {
    sha256(password.value).then(
        function (passhash) {
            const data = {
                uniqueid: getUID(),
                username: username.value,
                password: passhash,
                useragent: navigator.userAgent
            }
            socket.emit("user_auth", data, receiveLoginReq);
        }
    )
};

function receiveLoginReq(data) {
    if (!data.success) {
        alertOnFail(data)
    } else {
        window.location.href = "/chat";
    }
}
