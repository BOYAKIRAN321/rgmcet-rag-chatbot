// ===============================
// ✍ CHATGPT STYLE TYPING EFFECT
// ===============================
function typeEffect(element, text, speed = 18) {
    let index = 0;
    function type() {
        if (index < text.length) {
            element.innerHTML = text.substring(0, index + 1) + "<span class='typing-cursor'>|</span>";
            index++;
            element.parentElement.scrollTop = element.parentElement.scrollHeight;
            setTimeout(type, speed);
        } else {
            element.innerHTML = text;
        }
    }
    type();
}

// ===============================
// 🔥 SEND QUERY FUNCTION - FIXED
// ===============================
async function sendQuery() {
    const input = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");
    const query = input.value.trim();
    if (!query) return;

    window.speechSynthesis.cancel();

    const userDiv = document.createElement("div");
    userDiv.className = "message user-message";
    userDiv.innerText = query;
    chatBox.appendChild(userDiv);

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    const loadingDiv = document.createElement("div");
    loadingDiv.className = "message bot-message";
    loadingDiv.innerHTML = `<div class="loading-container"><div class="spinner"></div><span>Thinking...</span></div>`;
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    input.disabled = true;

    try {
        // FIXED: Use relative path /ask, not absolute http://127.0.0.1:5000/ask (avoids CORS)
        const response = await fetch("https://rgmcet-rag-chatbot.onrender.com/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();
        loadingDiv.remove();

        const botDiv = document.createElement("div");
        botDiv.className = "message bot-message";
        chatBox.appendChild(botDiv);

        const textSpan = document.createElement("span");
        botDiv.appendChild(textSpan);
        typeEffect(textSpan, data.answer);

        const speakBtn = document.createElement("button");
        speakBtn.innerText = " 🔊";
        speakBtn.style.background = "none";
        speakBtn.style.border = "none";
        speakBtn.style.cursor = "pointer";
        speakBtn.style.fontSize = "16px";
        speakBtn.onclick = () => speakText(data.answer);
        botDiv.appendChild(speakBtn);

    } catch (error) {
        console.error(error);
        loadingDiv.remove();
        const errorDiv = document.createElement("div");
        errorDiv.className = "message bot-message";
        errorDiv.innerText = "⚠️ Server not responding! Check if Ollama is running.";
        chatBox.appendChild(errorDiv);
    }

    input.disabled = false;
    input.focus();
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ===============================
// 🎤 VOICE TO TEXT
// ===============================
let recognition;
let isListening = false;

function startListening() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("Speech recognition not supported. Use Google Chrome.");
        return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!recognition) {
        recognition = new SpeechRecognition();
        recognition.lang = "en-IN";
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.onresult = function (event) {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            document.getElementById("userInput").value = transcript;
        };
        recognition.onerror = function () { stopListeningUI(); isListening = false; };
        recognition.onend = function () {
            stopListeningUI(); isListening = false;
            const input = document.getElementById("userInput");
            if (input.value.trim() !== "") sendQuery();
        };
    }
    if (isListening) {
        recognition.stop(); isListening = false; stopListeningUI();
    } else {
        recognition.start(); isListening = true; startListeningUI();
    }
}

function startListeningUI() {
    const micButton = document.getElementById("micButton");
    const input = document.getElementById("userInput");
    micButton.classList.add("mic-listening");
    micButton.innerText = "🎙️";
    input.placeholder = "Listening... Speak clearly";
}
function stopListeningUI() {
    const micButton = document.getElementById("micButton");
    const input = document.getElementById("userInput");
    micButton.classList.remove("mic-listening");
    micButton.innerText = "🎤";
    input.placeholder = "Type or speak your message...";
}

document.getElementById("userInput").addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendQuery();
});

let currentUtterance = null;
function speakText(text) {
    if (!('speechSynthesis' in window)) { alert("Text-to-Speech not supported"); return; }
    if (window.speechSynthesis.speaking) { window.speechSynthesis.cancel(); currentUtterance = null; return; }
    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.lang = "en-US";
    currentUtterance.rate = 1;
    currentUtterance.pitch = 1;
    currentUtterance.onend = function () { currentUtterance = null; };
    currentUtterance.onerror = function () { currentUtterance = null; };
    window.speechSynthesis.speak(currentUtterance);
}

document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("themeToggle");
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") { document.body.classList.add("light-mode"); toggle.checked = true; }
    toggle.addEventListener("change", function () {
        if (this.checked) { document.body.classList.add("light-mode"); localStorage.setItem("theme", "light"); }
        else { document.body.classList.remove("light-mode"); localStorage.setItem("theme", "dark"); }
    });
});
