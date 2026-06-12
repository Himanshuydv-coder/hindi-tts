// ===================== DOM Elements =====================

const textInput = document.getElementById('textInput');
const voiceSelect = document.getElementById('voiceSelect');
const speedSelect = document.getElementById('speedSelect');
const previewBtn = document.getElementById('previewBtn');
const generateBtn = document.getElementById('generateBtn');
const charCount = document.getElementById('charCount');
const maxChars = document.getElementById('maxChars');
const messageContainer = document.getElementById('messageContainer');
const loadingContainer = document.getElementById('loadingContainer');
const audioSection = document.getElementById('audioSection');
const audioPlayer = document.getElementById('audioPlayer');
const downloadBtn = document.getElementById('downloadBtn');
const newBtn = document.getElementById('newBtn');
const btnLoader = document.getElementById('btnLoader');
const btnText = document.querySelector('.btn-text');
const loadingText = document.getElementById('loadingText');

// ===================== Configuration =====================

const CONFIG = {
    MAX_CHARS: 10000,
    API_ENDPOINT: '/generate',
    DOWNLOAD_ENDPOINT: '/download/',
};

const STORAGE_KEYS = {
    TEXT: 'hindi_tts_text',
    VOICE: 'hindi_tts_voice',
    SPEED: 'hindi_tts_speed',
};

// ===================== Utility Functions =====================

/**
 * Show message to user
 */
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    messageContainer.innerHTML = '';
    messageContainer.appendChild(messageDiv);
    
    // Auto remove error/success messages after 5 seconds
    if (type !== 'info') {
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
}

/**
 * Clear all messages
 */
function clearMessages() {
    messageContainer.innerHTML = '';
}

/**
 * Show loading state
 */
function showLoading(show = true) {
    loadingContainer.classList.toggle('hidden', !show);
}

/**
 * Show audio section
 */
function showAudioSection(show = true) {
    audioSection.classList.toggle('hidden', !show);
}

/**
 * Set button state
 */
function setButtonState(disabled = false) {
    generateBtn.disabled = disabled;
    previewBtn.disabled = disabled;
    btnLoader.classList.toggle('hidden', !disabled);
    btnText.style.opacity = disabled ? '0.6' : '1';
}

/**
 * Reset form
 */
function resetForm() {
    textInput.value = '';
    updateCharCount();
    clearMessages();
    showAudioSection(false);
    showLoading(false);
    audioPlayer.src = '';
    setButtonState(false);
}

/**
 * Build request payload
 */
function buildRequestPayload(preview = false) {
    return {
        text: preview ? '' : textInput.value,
        voice: voiceSelect.value,
        speed: speedSelect.value,
        preview,
    };
}

/**
 * Update character counter
 */
function updateCharCount() {
    const count = textInput.value.length;
    charCount.textContent = count;
    
    // Show warning when reaching limit
    if (count > CONFIG.MAX_CHARS * 0.9) {
        charCount.parentElement.style.color = '#f59e0b';
    } else if (count > CONFIG.MAX_CHARS * 0.7) {
        charCount.parentElement.style.color = '#6366f1';
    } else {
        charCount.parentElement.style.color = 'var(--text-secondary)';
    }
}

/**
 * Validate input
 */
function validateInput(text) {
    if (!text.trim()) {
        showMessage('कृपया कुछ पाठ दर्ज करें', 'error');
        return false;
    }
    
    if (text.length > CONFIG.MAX_CHARS) {
        showMessage(`पाठ ${CONFIG.MAX_CHARS} वर्णों से अधिक नहीं हो सकता`, 'error');
        return false;
    }
    
    return true;
}

/**
 * Generate audio via API
 */
async function submitAudio(preview = false) {
    if (!preview && !validateInput(textInput.value)) {
        return;
    }
    
    setButtonState(true);
    clearMessages();
    showLoading(true);
    showAudioSection(false);
    
    try {
        const response = await fetch(CONFIG.API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(buildRequestPayload(preview)),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'ऑडियो उत्पन्न करने में विफल');
        }
        
        if (data.success) {
            audioPlayer.src = data.download_url;
            showMessage(data.message, 'success');
            showAudioSection(true);
            downloadBtn.onclick = () => downloadAudio(data.filename);
            
            setTimeout(() => {
                audioSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        } else {
            throw new Error(data.error || 'कुछ गलत हुआ');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage(error.message || 'ऑडियो उत्पन्न करने में विफल', 'error');
    } finally {
        showLoading(false);
        setButtonState(false);
    }
}

async function generateAudio() {
    await submitAudio(false);
}

async function previewVoice() {
    await submitAudio(true);
}

/**
 * Download audio file
 */
function downloadAudio(filename) {
    const link = document.createElement('a');
    link.href = CONFIG.DOWNLOAD_ENDPOINT + filename;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ===================== Event Listeners =====================

/**
 * Text input event listener
 */
textInput.addEventListener('input', (e) => {
    updateCharCount();
    localStorage.setItem(STORAGE_KEYS.TEXT, textInput.value);
    
    if (textInput.value.length > 0 && !audioSection.classList.contains('hidden')) {
        // Optionally show a message or just keep it visible
    }
});

voiceSelect.addEventListener('change', () => {
    localStorage.setItem(STORAGE_KEYS.VOICE, voiceSelect.value);
});

speedSelect.addEventListener('change', () => {
    localStorage.setItem(STORAGE_KEYS.SPEED, speedSelect.value);
});

/**
 * Text input - Enter key to generate (Ctrl+Enter)
 */
textInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        generateAudio();
    }
});

/**
 * Generate button click
 */
generateBtn.addEventListener('click', generateAudio);
previewBtn.addEventListener('click', previewVoice);

/**
 * Download button click
 */
downloadBtn.addEventListener('click', () => {
    const filename = audioPlayer.src.split('/').pop();
    downloadAudio(filename);
    showMessage('डाउनलोड शुरू हो गया!', 'success');
});

/**
 * New button click
 */
newBtn.addEventListener('click', resetForm);

/**
 * Prevent text paste of very large content
 */
textInput.addEventListener('paste', (e) => {
    e.preventDefault();
    
    const text = (e.clipboardData || window.clipboardData).getData('text');
    
    if (text.length > CONFIG.MAX_CHARS) {
        showMessage(`पाठ बहुत बड़ा है। केवल ${CONFIG.MAX_CHARS} वर्ण तक की अनुमति है।`, 'error');
        return;
    }
    
    // Insert pasted text
    const start = textInput.selectionStart;
    const end = textInput.selectionEnd;
    const currentText = textInput.value;
    const resultText = currentText.substring(0, start) + text + currentText.substring(end);
    
    if (resultText.length > CONFIG.MAX_CHARS) {
        showMessage(`पाठ बहुत बड़ा है। केवल ${CONFIG.MAX_CHARS} वर्ण तक की अनुमति है।`, 'error');
        return;
    }
    
    textInput.value = resultText;
    textInput.selectionStart = textInput.selectionEnd = start + text.length;
    updateCharCount();
});

// ===================== Initialization =====================

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    maxChars.textContent = CONFIG.MAX_CHARS;
    updateCharCount();
    
    const savedVoice = localStorage.getItem(STORAGE_KEYS.VOICE);
    const savedSpeed = localStorage.getItem(STORAGE_KEYS.SPEED);
    if (savedVoice) voiceSelect.value = savedVoice;
    if (savedSpeed) speedSelect.value = savedSpeed;
    
    textInput.focus();
    showMessage('नमस्ते! हिंदी पाठ दर्ज करें और ऑडियो उत्पन्न करें।', 'info');
});

// ===================== Advanced Features =====================

/**
 * Load from localStorage on page load
 */
window.addEventListener('load', () => {
    const savedText = localStorage.getItem(STORAGE_KEYS.TEXT);
    const savedVoice = localStorage.getItem(STORAGE_KEYS.VOICE);
    const savedSpeed = localStorage.getItem(STORAGE_KEYS.SPEED);
    
    if (savedText) {
        textInput.value = savedText;
        updateCharCount();
    }
    if (savedVoice) {
        voiceSelect.value = savedVoice;
    }
    if (savedSpeed) {
        speedSelect.value = savedSpeed;
    }
});

/**
 * Warn before leaving page if generation in progress
 */
window.addEventListener('beforeunload', (e) => {
    if (!generateBtn.disabled) {
        return; // Allow navigation
    }
    e.preventDefault();
    e.returnValue = '';
});

/**
 * Handle network errors
 */
window.addEventListener('offline', () => {
    showMessage('इंटरनेट कनेक्शन खो गया। कृपया अपने कनेक्शन की जाँच करें।', 'error');
    setButtonState(false);
    showLoading(false);
});

window.addEventListener('online', () => {
    showMessage('इंटरनेट कनेक्शन बहाल हुआ।', 'success');
});
