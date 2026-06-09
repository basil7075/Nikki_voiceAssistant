const orb       = document.getElementById('orb');
const micBtn    = document.getElementById('micBtn');
const micHint   = document.getElementById('micHint');
const statusEl  = document.getElementById('status');
const transcriptInner = document.getElementById('transcriptInner');
const transcript      = document.getElementById('transcript');

// ── WebSocket ────────────────────────────────────────────────
const ws = new WebSocket(`ws://${location.host}/ws`);

ws.onopen = () => {
    statusEl.textContent = 'online';
    micBtn.disabled = false;
};

ws.onclose = () => {
    statusEl.textContent = 'disconnected';
    micBtn.disabled = true;
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === 'response') {
        addMessage('nikki', msg.text);
        playAudio(msg.audio);
    }

    if (msg.type === 'transcript') {
        addMessage('user', msg.text);
    }

    if (msg.type === 'error') {
        micHint.textContent = msg.text;
        setTimeout(() => micHint.textContent = 'hold to speak', 2000);
    }
};

// ── Orb ──────────────────────────────────────────────────────
function setOrbState(state) {
    orb.classList.remove('listening', 'speaking', 'idle');
    if (state) orb.classList.add(state);
}

// ── Audio playback ───────────────────────────────────────────
function playAudio(b64) {
    const binary = atob(b64);
    const bytes  = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);

    const blob = new Blob([bytes], { type: 'audio/mpeg' });
    const url  = URL.createObjectURL(blob);
    const audio = new Audio(url);

    setOrbState('speaking');
    audio.play();
    audio.onended = () => {
        setOrbState(null);
        URL.revokeObjectURL(url);
    };
}

// ── Transcript ───────────────────────────────────────────────
function addMessage(sender, text) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.innerHTML = `
        <span class="sender">${sender === 'nikki' ? 'Nikki' : 'You'}</span>
        <span class="text">${text}</span>
    `;
    transcriptInner.appendChild(div);
    transcript.scrollTop = transcript.scrollHeight;
}

// ── Push to talk (MediaRecorder → Groq Whisper) ─────────────
let mediaRecorder = null;
let audioChunks = [];

async function initMic() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    
    mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data);
    };
    
    mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        audioChunks = [];
        const arrayBuffer = await blob.arrayBuffer();
        const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
        ws.send(JSON.stringify({ type: 'audio', data: base64 }));
        micHint.textContent = 'processing...';
    };
    
    micBtn.disabled = false;
}

micBtn.addEventListener('mousedown', () => {
    if (!mediaRecorder) return;
    audioChunks = [];
    mediaRecorder.start();
    micBtn.classList.add('active');
    setOrbState('listening');
    micHint.textContent = 'listening...';
});

micBtn.addEventListener('mouseup', () => {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') return;
    mediaRecorder.stop();
    micBtn.classList.remove('active');
    setOrbState(null);
});

micBtn.addEventListener('mouseleave', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        micBtn.classList.remove('active');
        setOrbState(null);
    }
});

micBtn.addEventListener('touchstart', (e) => { e.preventDefault(); micBtn.dispatchEvent(new Event('mousedown')); });
micBtn.addEventListener('touchend',   (e) => { e.preventDefault(); micBtn.dispatchEvent(new Event('mouseup')); });

initMic().catch(() => {
    micHint.textContent = 'mic access denied';
    micBtn.disabled = true;
});