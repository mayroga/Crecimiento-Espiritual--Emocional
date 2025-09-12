async function sendMessage() {
    const messageInput = document.getElementById("message");
    const chatBox = document.getElementById("chat-box");
    const audioPlayer = document.getElementById("audio-player");

    const msg = messageInput.value;
    if (!msg) return;

    chatBox.innerHTML += `<div><b>Tú:</b> ${msg}</div>`;
    messageInput.value = "";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: msg})
        });
        const data = await res.json();

        chatBox.innerHTML += `<div><b>Asistente:</b> ${data.reply}</div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        audioPlayer.src = `data:audio/mp3;base64,${data.audio}`;
        audioPlayer.style.display = "block";
        audioPlayer.play();
    } catch (err) {
        chatBox.innerHTML += `<div><b>Error:</b> No se pudo conectar al servidor.</div>`;
    }
}
