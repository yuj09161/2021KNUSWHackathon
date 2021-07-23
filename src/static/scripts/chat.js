const socket = io();
const chatRooms = {
    roomCnt: 0,
    currentRoom: -1
};
const USERTYPE_STRING = {
    "undergraduate": "학부생",
    "graduate": "대학원생",
    "professor": "교수"
};

let chatList;
let chatArea;
let chatPlaceHolder;
let chatInputArea;
let chatMsg;

window.onload = function() {
    document.getElementById("chatMsg").onkeyup
    = event => {if (event.key == "Enter") sendMsg();};

    chatList = document.getElementById("chatList");
    chatArea = document.getElementById("chatArea")
    chatPlaceHolder = document.getElementById("chatBubbles_placeHolder");
    chatInputArea = document.getElementById("chatInputArea");
    chatMsg = document.getElementById("chatMsg");

    socket.emit("retrieve_rooms", loadChatRooms);
}

window.addEventListener("beforeunload", event => {
    logout();
    // event.preventDefault();
    // event.returnValue = "false";
});

function logout() {
    socket.emit("logout", {
        uniqueid: document
        .cookie
        .split("; ")
        .find(cookie => cookie.startsWith("chat_hys_uid"))
        .split("=")[1]
    }, afterLogout);
};

function afterLogout(data) {
    if (data.success) {
        window.location.href = "/";
    } else {
        alertOnFail(data);
    };
};

function loadChatRooms(data) {
    if (data.success) {
        for (chatroom of data.chatrooms) {
            addChatRoom(chatroom);
        };
    } else {
        alertOnFail(data);
    }
};

function addChatRoom(chatRoomName) {
    const roomName = chatRoomName;
    const roomId = (chatRooms.roomCnt++).toString();

    const roomRoot = Object.assign(document.createElement("div"), {className: "anotherRoom"});
    chatList.appendChild(roomRoot);

    const linkToActive = Object.assign(document.createElement("a"), {
        className: "anotherRoom",
        textContent: roomName
    });
    linkToActive.onclick = event => changeChatRoom(roomId);
    roomRoot.appendChild(linkToActive);
    
    roomRoot.appendChild(
        Object.assign(document.createElement("span"), {className: "spacer"})
    );

    const displayArea = Object.assign(
        document.createElement("div"), {
            className: "anotherRoom",
            className: "chatBubbles",
            id: `chatBubbles_${roomId}`,
            style: "display: none"
        }
    );
    chatArea.insertBefore(displayArea, chatInputArea);

    chatRooms[roomId] = {
        roomRoot: roomRoot,
        linkToActive: linkToActive,
        displayArea: displayArea,
    };

    if (roomId == "0") changeChatRoom("0");
};

function changeChatRoom(roomId) {
    const currentRoomId = chatRooms.currentRoom;
    if (currentRoomId == roomId) return;
    if (currentRoomId >= 0) {
        const currentRoom = chatRooms[currentRoomId];
        currentRoom.roomRoot.className = "anotherRoom";
        currentRoom.linkToActive.className = "anotherRoom";
        currentRoom.displayArea.style = "display: none;";
    } else {
        chatPlaceHolder.style = "display: none;";
    };
    const nextRoom = chatRooms[roomId];
    nextRoom.roomRoot.className = "currentRoom";
    nextRoom.linkToActive.className = "currentRoom";
    nextRoom.displayArea.style = "";
    chatRooms.currentRoom = roomId;
};

function loadChats(chats) {
    for (chat of chats) {
        receiveMsg(chat);
    }
};

socket.on("chat", receiveMsg);
function receiveMsg(msg) {
    const roomId = msg.roomid;
    const sender = msg.sender;
    const isguest = sender.isguest;
    const usertype = sender.usertype;
    const username = sender.username;
    const message = msg.message;

    const chatBubbles = chatRooms[roomId].displayArea;

    const bubbleContainer = Object.assign(
        document.createElement("div"), {className: "bubbleContainer"}
    );

    const infoContainer = Object.assign(
        document.createElement("span"), {className: "userInfoDisplay"}
    );
    infoContainer.appendChild(Object.assign(
        document.createElement("span"), {className: "username", innerText: username}
    ));
    infoContainer.appendChild(Object.assign(
        document.createElement("span"), {
            className: "userinfo",
            innerText: `${isguest ? "게스트" : "인증됨"}·${USERTYPE_STRING[usertype]}`
        }
    ));
    bubbleContainer.appendChild(infoContainer);

    bubbleContainer.appendChild(
        Object.assign(document.createElement("span"), {className: "textBubble", innerText: message})
    );
    bubbleContainer.appendChild(
        Object.assign(document.createElement("span"), {className: "spacer"})
    );
    chatBubbles.appendChild(bubbleContainer);

    chatBubbles.scrollTop = chatBubbles.scrollHeight;
};

function sendMsg() {
    const roomId = chatRooms.currentRoom;
    const uid = getUID();
    const message = chatMsg.value;
    chatMsg.value = "";

    const chatBubbles = chatRooms[roomId].displayArea;

    const bubbleContainer = Object.assign(
        document.createElement("div"), {className: "bubbleContainer"}
    )
    chatBubbles.appendChild(bubbleContainer);
    bubbleContainer.appendChild(
        Object.assign(document.createElement("span"), {className: "spacer"})
    );
    bubbleContainer.appendChild(
        Object.assign(document.createElement("span"), {className: "textBubble", innerText: message})
    );
    
    chatBubbles.scrollTop = chatBubbles.scrollHeight;

    socket.emit("chat", {roomid: roomId, uniqueid: uid, message: message});
};
