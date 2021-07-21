function getUID() {
    return document
           .cookie
           .split("; ")
           .find(cookie => cookie.startsWith("chat_hys_uid"))
           .split("=")[1]
}

function alertOnFail(data) {
    alert(data.message)
    if (data.redirect != undefined) {
        window.location.href = data.redirect;
    }
}
