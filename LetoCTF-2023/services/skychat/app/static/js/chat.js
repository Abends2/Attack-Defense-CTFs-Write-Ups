support_api_url = "http://94.154.11.78:31338/chat";
// support_admin_url = "http://94.154.11.78:31338/admin";
function b64EncodeUnicode(str) {
    return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
        function toSolidBytes(match, p1) {
            return String.fromCharCode('0x' + p1);
        }));
}

function b64DecodeUnicode(str) {
    return decodeURIComponent(atob(str).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
}

var chats_ul = document.getElementById("chats_list");
function addChat(id){
    var onlinei = document.createElement("i");
    onlinei.className = "fa fa-circle online";

    var div1 = document.createElement("div");
    div1.className = "status";
    div1.append(onlinei);
    div1.innerHTML += 'online';

    var div2 = document.createElement("div");
    div2.className = "name";
    div2.innerHTML += "Support agent " + id.toString();

    var div3 = document.createElement("div");
    div3.className = "about";
    div3.append(div2, div1);

    var img = document.createElement("img");
    img.src = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/195612/chat_avatar_09.jpg";

    var li = document.createElement("li");
    li.className = "clearfix chatroom";
    li.append(img, div3);
    li.setAttribute("onclick", `openChat(${id})`);

    chats_ul.append(li);
    let d = document.getElementById("new_chat_button");
    d.parentNode.appendChild(d);
}

var messages_ul = document.getElementById("messages");
function displayMessage(text, direction){
    var span = document.createElement("span");
    span.className = "message-data-name";
    span.innerHTML += direction ? 'Me' : 'Support';

    var div1 = document.createElement("div");
    div1.className = direction ? "message-data align-right" : 'message-data';
    div1.append(span);

    var div2 = document.createElement("div");
    div2.className = direction ? "message other-message float-right" : 'message my-message';
    div2.innerHTML += text;

    var li = document.createElement("li");
    if (direction) li.className = "clearfix";
    li.append(div1, div2);

    messages_ul.append(li);
    scroolMessagesWindow();
}

let opened_chat_id = -1;
function openChat(id){
    opened_chat_id = id;
    document.getElementById('messages').innerHTML = '';
    document.getElementById('chatname').innerHTML = 'Chat with Suppport agent ' + id.toString();
    mymsg_el.disabled=false;

    $.ajax({
        method: "GET",
        url: `/api/v1/chats/${id}`,
        headers: {"Authorization": "Basic " + btoa(localStorage.getItem('login') + ":" + localStorage.getItem('password'))},
        success: function (data, textStatus, jQxhr) {
            if (data["data"]){
                for (const message of data["data"]){
                    displayMessage(b64DecodeUnicode(message["text"]), message["direction"]);
                }
            }
        },
        error: function (jqXhr, textStatus, errorThrown) {
            alert("Some error occurred while getting messages!");
        }
    });
}

function saveMessage(message, direction){
    $.ajax({
        method: "POST",
        url: `/api/v1/chats/${opened_chat_id}`,
        headers: {"Authorization": "Basic " + btoa(localStorage.getItem('login') + ":" + localStorage.getItem('password'))},
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({"text": b64EncodeUnicode(message), "direction": direction}),
        error: function (jqXhr, textStatus, errorThrown) {
            alert("Some error occurred while sending message!");
            return false;
        }
    });
}

function setCompanionWritingState(state){
    if (state){
        var i1 = document.createElement("i");
        i1.className = "fa fa-circle online";

        var i2 = document.createElement("i");
        i2.className = "fa fa-circle online";
        i2.style.color = "#AED2A6";

        var i3 = document.createElement("i");
        i3.className = "fa fa-circle online";
        i3.style.color = "#DAE9DA";

        var li = document.createElement("li");
        li.id = "companion_writing";
        li.append(i1, i2, i3);

        messages_ul.append(li);
    }
    else{
        let elem = document.getElementById("companion_writing");
        elem.remove();
    }
}
setCompanionWritingState(false);

function scroolMessagesWindow(){
    let elem = document.getElementById("chat-history-window");
    elem.scrollTo(0, elem.scrollHeight);
}

let mymsg_el = document.getElementById("message-to-send");
mymsg_el.disabled=true;
function sendMyMessage(){
    let msg = mymsg_el.value;
    saveMessage(msg, true);
    displayMessage(msg, true);
    mymsg_el.value="";

    setCompanionWritingState(true);
    $.ajax({
        method: "POST",
        url: support_api_url,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({"request": msg, "chat_id": opened_chat_id +
                localStorage.getItem("login") + localStorage.getItem("user_id")}),
        success: function (data, textStatus, jQxhr) {
            saveMessage(data["response"], false);
            displayMessage(data["response"], false);
            setCompanionWritingState(false);
            scroolMessagesWindow();
        },
        error: function (jqXhr, textStatus, errorThrown) {
            alert("Some error occurred while getting response!");
        }
    });
}

function updateChatsList() {
    let chats_list = document.getElementById('chats_list');
    for (let i = chats_list.children.length - 1; i >= 0; i--){
        if (chats_list.children[i].id !== "new_chat_button"){
            chats_list.children[i].remove();
        }
    }
    $.ajax({
        method: "GET",
        url: "/api/v1/chats",
        headers: {"Authorization": "Basic " + btoa(localStorage.getItem('login') + ":" + localStorage.getItem('password'))},
        success: function (data, textStatus, jQxhr) {
            if (data["data"]) {
                for (const chat of data["data"]) {
                    addChat(chat["id"]);
                }
            }
        },
        error: function (jqXhr, textStatus, errorThrown) {
            alert("Some error occurred!");
        }
    });
}
updateChatsList();

function createChat(){
    $.ajax({
        method: "POST",
        url: "/api/v1/chats",
        headers: {"Authorization": "Basic " + btoa(localStorage.getItem('login') + ":" + localStorage.getItem('password'))},
        success: function (data, textStatus, jQxhr) {
            updateChatsList();
        },
        error: function (jqXhr, textStatus, errorThrown) {
            alert("Some error while creating chat!");
        }
    });
}

mymsg_el.addEventListener("keyup", (event) => {
    if (event.key === "Enter") {
        sendMyMessage();
    }
});

function logout(){
    localStorage.clear();
    location="/";
}

function deleteCurrentChat(){
    if (opened_chat_id < 0)
        return;
    $.ajax({
        method: "POST",
        url: "/api/v1/delete_chat",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        headers: {"Authorization": "Basic " + btoa(localStorage.getItem('login') + ":" + localStorage.getItem('password'))},
        data: JSON.stringify({"chat_id": opened_chat_id, "user_id": localStorage.getItem("user_id")}),
        success: function (data, textStatus, jQxhr) {
            opened_chat_id = -1;
            document.getElementById('messages').innerHTML = '';
            document.getElementById('chatname').innerHTML = 'Chat with Suppport';
            updateChatsList();
        },
        error: function (jqXhr, textStatus, errorThrown) {
            alert("Some error occurred while deleting chat!");
        }
    });
}
