async function sendMessage(){
    const msgInput = document.getElementById("message");
    const msg = msgInput.value;
    if(!msg) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<p><b>Tú:</b> ${msg}</p>`;
    msgInput.value = "";

    const res = await fetch("/chat", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({message: msg})
    });
    const data = await res.json();

    chatBox.innerHTML += `<p><b>Guía:</b> ${data.reply}</p>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    // reproducir audio
    const audioPlayer = document.getElementById("audio-player");
    audioPlayer.src = "data:audio/mp3;base64," + data.audio;
    audioPlayer.style.display = "block";
    audioPlayer.play();
}
