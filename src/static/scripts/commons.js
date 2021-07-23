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

async function sha256(text) {
    // sniffet from developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/digest (Public Domain)
    const encodedMessage = new TextEncoder().encode(text);
    const hashBuf = await crypto.subtle.digest('SHA-256', encodedMessage);
    const hashArr = Array.from(new Uint8Array(hashBuf));
    const hashStr = hashArr.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashStr;
}
