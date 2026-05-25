/* =========================================================
   Wieder da — interaktive Erinnerung an dein Haustier
   ========================================================= */

const STORAGE_KEY = 'pet-memorial-config-v1';
const MODEL = 'claude-opus-4-7';
const MAX_HISTORY = 12;

const ACTIONS = [
    'idle', 'wag', 'run_to', 'sit', 'lay_down',
    'head_tilt', 'sleep', 'play', 'eat', 'look_around'
];
const SOUNDS = [
    'happy_bark', 'soft_woof', 'whine', 'pant', 'snore'
];

const state = {
    apiKey: '',
    pet: { name: '', species: '', personality: '', photoDataUrl: '' },
    history: [],
    availableClips: new Set(),
    availableSounds: new Set(),
    isRecording: false,
    isThinking: false,
    recognition: null,
    currentAudio: null,
};

/* ---------- DOM ---------- */
const $ = (id) => document.getElementById(id);
const setupView = $('setup-view');
const sceneView = $('scene-view');
const petVideo = $('pet-video');
const petPhoto = $('pet-photo-fallback');
const narrationEl = $('narration');
const micBtn = $('mic-btn');
const statusEl = $('status');
const statusName = $('status-name');
const transcriptEl = $('transcript');

/* =========================================================
   Setup & Persistence
   ========================================================= */

function loadConfig() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return;
        const cfg = JSON.parse(raw);
        state.apiKey = cfg.apiKey || '';
        state.pet = cfg.pet || state.pet;

        $('api-key').value = state.apiKey;
        $('pet-name').value = state.pet.name;
        $('pet-species').value = state.pet.species;
        $('pet-personality').value = state.pet.personality;
    } catch (e) {
        console.warn('Konnte Config nicht laden:', e);
    }
}

function saveConfig() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
        apiKey: state.apiKey,
        pet: state.pet,
    }));
}

async function handleStart() {
    state.apiKey = $('api-key').value.trim();
    state.pet.name = $('pet-name').value.trim() || 'mein Liebling';
    state.pet.species = $('pet-species').value.trim() || 'Hund';
    state.pet.personality = $('pet-personality').value.trim();

    if (!state.apiKey) {
        alert('Bitte gib einen Claude API-Key ein.');
        return;
    }

    const photoFile = $('pet-photo').files[0];
    if (photoFile) {
        state.pet.photoDataUrl = await fileToDataUrl(photoFile);
    }

    saveConfig();
    await enterScene();
}

function fileToDataUrl(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

/* =========================================================
   Scene
   ========================================================= */

async function enterScene() {
    setupView.classList.add('hidden');
    sceneView.classList.remove('hidden');
    statusName.textContent = state.pet.name;

    await probeAvailableMedia();
    initRecognition();
    setupMicEvents();
    setIdleVisual();
}

async function probeAvailableMedia() {
    const probes = [];
    for (const action of ACTIONS) {
        probes.push(headExists(`clips/${action}.mp4`).then(ok => {
            if (ok) state.availableClips.add(action);
        }));
    }
    for (const sound of SOUNDS) {
        probes.push(headExists(`sounds/${sound}.mp3`).then(ok => {
            if (ok) state.availableSounds.add(sound);
        }));
    }
    await Promise.all(probes);
}

async function headExists(url) {
    try {
        const r = await fetch(url, { method: 'HEAD' });
        return r.ok;
    } catch {
        return false;
    }
}

function setIdleVisual() {
    if (state.availableClips.has('idle')) {
        showClip('idle');
    } else if (state.pet.photoDataUrl) {
        petVideo.classList.add('hidden');
        petPhoto.src = state.pet.photoDataUrl;
        petPhoto.classList.remove('hidden');
    } else {
        petVideo.classList.add('hidden');
        petPhoto.classList.add('hidden');
    }
}

function showClip(action) {
    if (!state.availableClips.has(action)) {
        // fall back to idle clip if available, else photo
        if (action !== 'idle' && state.availableClips.has('idle')) {
            showClip('idle');
        } else if (state.pet.photoDataUrl) {
            petVideo.classList.add('hidden');
            petPhoto.classList.remove('hidden');
        }
        return;
    }
    petPhoto.classList.add('hidden');
    petVideo.classList.remove('hidden');
    const newSrc = `clips/${action}.mp4`;
    if (!petVideo.src.endsWith(newSrc)) {
        petVideo.src = newSrc;
    }
    petVideo.loop = (action === 'idle' || action === 'sleep');
    petVideo.play().catch(() => {});
    if (!petVideo.loop) {
        petVideo.onended = () => {
            // return to idle after one-shot action
            setIdleVisual();
        };
    } else {
        petVideo.onended = null;
    }
}

function playSound(sound) {
    if (!sound || sound === 'none') return;
    if (!state.availableSounds.has(sound)) return;
    if (state.currentAudio) {
        state.currentAudio.pause();
    }
    const audio = new Audio(`sounds/${sound}.mp3`);
    audio.volume = 0.8;
    audio.play().catch(() => {});
    state.currentAudio = audio;
}

function showNarration(text) {
    if (!text) {
        narrationEl.classList.remove('visible');
        return;
    }
    narrationEl.textContent = text;
    narrationEl.classList.add('visible');
    clearTimeout(narrationEl._t);
    narrationEl._t = setTimeout(() => {
        narrationEl.classList.remove('visible');
    }, Math.max(4000, text.length * 70));
}

function setStatus(text) {
    statusEl.textContent = text;
}

function showTranscript(text) {
    if (!text) {
        transcriptEl.classList.add('hidden');
        return;
    }
    transcriptEl.textContent = `„${text}"`;
    transcriptEl.classList.remove('hidden');
    clearTimeout(transcriptEl._t);
    transcriptEl._t = setTimeout(() => {
        transcriptEl.classList.add('hidden');
    }, 6000);
}

/* =========================================================
   Speech Recognition (push-to-talk)
   ========================================================= */

function initRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
        setStatus('Dein Browser unterstützt keine Spracherkennung. Bitte Chrome/Edge nutzen.');
        micBtn.disabled = true;
        return;
    }
    const r = new SR();
    r.lang = 'de-DE';
    r.continuous = false;
    r.interimResults = false;
    r.maxAlternatives = 1;

    r.onresult = (e) => {
        const transcript = e.results[0][0].transcript.trim();
        if (transcript) {
            showTranscript(transcript);
            speakToPet(transcript);
        }
    };
    r.onerror = (e) => {
        console.warn('Speech error:', e.error);
        if (e.error === 'no-speech') {
            setStatus('Habe nichts gehört. Versuch es nochmal.');
        } else if (e.error === 'not-allowed') {
            setStatus('Mikrofon-Zugriff verweigert.');
        }
    };
    r.onend = () => {
        if (state.isRecording) stopRecording();
    };

    state.recognition = r;
}

function setupMicEvents() {
    const start = (e) => { e.preventDefault(); startRecording(); };
    const stop = (e) => { e.preventDefault(); stopRecording(); };

    micBtn.addEventListener('mousedown', start);
    micBtn.addEventListener('mouseup', stop);
    micBtn.addEventListener('mouseleave', () => { if (state.isRecording) stopRecording(); });
    micBtn.addEventListener('touchstart', start, { passive: false });
    micBtn.addEventListener('touchend', stop, { passive: false });

    $('settings-btn').addEventListener('click', () => {
        sceneView.classList.add('hidden');
        setupView.classList.remove('hidden');
    });
}

function startRecording() {
    if (state.isThinking || state.isRecording || !state.recognition) return;
    try {
        state.recognition.start();
        state.isRecording = true;
        micBtn.classList.add('active');
        setStatus('Höre zu...');
    } catch (e) {
        console.warn('Recognition start failed:', e);
    }
}

function stopRecording() {
    if (!state.isRecording) return;
    state.isRecording = false;
    micBtn.classList.remove('active');
    try { state.recognition.stop(); } catch {}
}

/* =========================================================
   Claude API
   ========================================================= */

function buildSystemPrompt() {
    return `Du bist ${state.pet.name}, ein verstorbenes Haustier, das dem Besitzer in einer liebevollen Erinnerung wieder begegnet. Du selbst sprichst NICHT — du bist ein Tier. Stattdessen reagierst du mit Aktionen, Lauten und Körpersprache.

ART: ${state.pet.species}
PERSÖNLICHKEIT & ERINNERUNGEN:
${state.pet.personality || '(Keine Angaben — sei ein liebevolles, ruhiges Tier.)'}

REGELN:
- Antworte IMMER mit dem Tool "react".
- Wähle EINE passende Aktion aus der Aktions-Liste.
- Wähle EINEN passenden Sound (oder "none").
- Die "narration" beschreibt in 1-2 kurzen, warmen Sätzen aus Beobachter-Sicht, was das Tier tut. Deutsch. Verwende den Namen "${state.pet.name}" sparsam.
- Sei subtil, ehrlich, nicht kitschig. Tiere reden nicht — beschreibe Bewegungen, Blicke, Gesten.
- Wenn der Besitzer das Tier ruft → meist "run_to" + "happy_bark".
- Wenn der Besitzer streichelt/leise spricht → "sit"/"lay_down" + "pant"/"soft_woof"/"none".
- Wenn der Besitzer Spielzeug erwähnt → "play" + "happy_bark".
- Wenn der Besitzer traurig klingt → "head_tilt" oder "lay_down" + "whine"/"none".
- Bei Stille/Verwirrung → "head_tilt" oder "look_around" + "none".

Reagiere jetzt auf die Worte des Besitzers.`;
}

const REACT_TOOL = {
    name: 'react',
    description: 'Reagiere als Tier auf die Worte des Besitzers mit Aktion, Sound und einer kurzen Beschreibung.',
    input_schema: {
        type: 'object',
        properties: {
            action: {
                type: 'string',
                enum: ACTIONS,
                description: 'Die körperliche Aktion des Tieres.'
            },
            sound: {
                type: 'string',
                enum: [...SOUNDS, 'none'],
                description: 'Der Laut des Tieres, oder "none" für still.'
            },
            narration: {
                type: 'string',
                description: 'Kurze, warme Beobachter-Beschreibung dessen, was das Tier tut. 1-2 Sätze, deutsch.'
            }
        },
        required: ['action', 'sound', 'narration']
    }
};

async function speakToPet(userText) {
    if (state.isThinking) return;
    state.isThinking = true;
    micBtn.classList.add('thinking');
    setStatus('Denkt nach...');

    state.history.push({ role: 'user', content: userText });
    if (state.history.length > MAX_HISTORY) {
        state.history = state.history.slice(-MAX_HISTORY);
    }

    try {
        const messages = state.history.map(m => ({
            role: m.role,
            content: m.content
        }));

        const body = {
            model: MODEL,
            max_tokens: 400,
            system: [
                {
                    type: 'text',
                    text: buildSystemPrompt(),
                    cache_control: { type: 'ephemeral' }
                }
            ],
            tools: [REACT_TOOL],
            tool_choice: { type: 'tool', name: 'react' },
            messages,
        };

        const res = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'content-type': 'application/json',
                'x-api-key': state.apiKey,
                'anthropic-version': '2023-06-01',
                'anthropic-dangerous-direct-browser-access': 'true',
            },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`API ${res.status}: ${errText}`);
        }

        const data = await res.json();
        const toolUse = (data.content || []).find(c => c.type === 'tool_use');
        if (!toolUse) throw new Error('Keine Reaktion erhalten.');

        const { action, sound, narration } = toolUse.input;

        // Save assistant turn into history as a short summary, so context is preserved
        state.history.push({
            role: 'assistant',
            content: `[${action}, ${sound}] ${narration}`
        });

        showClip(action);
        playSound(sound);
        showNarration(narration);
        setStatus(`Halte das Mikrofon und sprich mit ${state.pet.name}`);

    } catch (err) {
        console.error(err);
        setStatus('Etwas ist schiefgegangen. ' + err.message);
        showNarration(`${state.pet.name} schaut dich verwirrt an.`);
        showClip('head_tilt');
    } finally {
        state.isThinking = false;
        micBtn.classList.remove('thinking');
    }
}

/* =========================================================
   Init
   ========================================================= */

window.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    $('start-btn').addEventListener('click', handleStart);
});
