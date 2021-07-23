const socket = io();

let fileArea;
let fileAreaText;
let fileInput;

window.onload = function() {
    fileArea = document.getElementById("fileArea");
    fileAreaText = document.getElementById("fileAreaText");
    fileInput = document.getElementById("fileInput");

    fileArea.onclick = () => fileInput.click();
    fileArea.ondragover = event => event.preventDefault();
    fileArea.ondrop = setFile;
    document.getElementById("register").onclick = sendRegisterReq;
}

function setFile(event) {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files.length == 1) {
        const file = files[0];
        if (!file.type.startsWith("image")) {
            alert("그림 파일을 선택해 주세요");
        } else {
            fileInput.files = files;
            fileAreaText.innerText = `선택된 파일: ${file.name}`;
        }
    } else if (files.length > 1) {
        alert("파일 하나만 선택해 주세요");
    } else {
        alert("선택된 파일이 없습니다.");
    }
}

function sendRegisterReq() {
    if (!document.getElementById("username").checkValidity()) {
        alert("아이디를 확인해 주세요");
        return;
    }
    if (!document.getElementById("nickname").checkValidity()) {
        alert("닉네임을 확인해 주세요");
        return;
    }
    if (fileInput.files.length == 0) {
        alert("파일이 선택되지 않았습니다");
        return;
    }

    formData = new FormData(document.getElementById("registerData"));
    sha256(formData.get("password")).then(
        password => {
            formData.set("password", password);
        
            let request = new XMLHttpRequest();
            request.open('POST', '/register');
            request.onerror = event => {
                alert("처리 중 오류가 발생했습니다\n다시 시도해주세요");
            }
            request.onload = event => {
                data = JSON.parse(request.responseText);
                if (!data.success) {
                    alertOnFail(data);
                } else {
                    alert("요청 성공하였습니다");
                    window.location.href = "/";
                }
            }
            request.send(formData);
        }
    );
}

function afterRegisterReq(data) {
    if (!data.success) {
        alertOnFail(data);
    } else {
        window.location.href = "/";
    }
}
