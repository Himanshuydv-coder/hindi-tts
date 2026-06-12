# 🎵 हिंदी टेक्स्ट टू स्पीच (Hindi TTS) Web App

एक उत्पादन-तैयार वेब अनुप्रयोग जो लंबे हिंदी पाठ को सुंदर MP3 ऑडियो में परिवर्तित करता है।

**[English]** A production-ready web application that converts long Hindi text into beautiful MP3 audio.

---

## 🌟 Features

✨ **सुंदर Dark Theme UI** - आधुनिक और प्रतिक्रियाशील डिजाइन
✨ **लंबा पाठ समर्थन** - 5000-10000+ शब्द तक
✨ **स्वचालित टेक्स्ट विभाजन** - छोटे चंकों में बड़े पाठ को विभाजित करता है
✨ **वास्तविक समय वर्ण गणना** - आप कितना टाइप कर रहे हैं ट्रैक करें
✨ **उन्नत ऑडियो मर्जिंग** - कई ऑडियो चंकों को एक MP3 में मर्ज करता है
✨ **बिल्ट-इन ऑडियो प्लेयर** - ब्राउज़र में सीधे सुनें
✨ **आसान डाउनलोड** - एक क्लिक में MP3 डाउनलोड करें
✨ **त्रुटि हैंडलिंग** - विस्तृत त्रुटि संदेश और सुरक्षित विफलता
✨ **LocalStorage सहायता** - आपके पाठ को स्वचालित रूप से सहेजता है
✨ **स्वचालित सफाई** - पुरानी फाइलों को स्वचालित रूप से हटाता है
✨ **AJAX लोडिंग** - कोई पृष्ठ रीफ्रेश नहीं
✨ **मोबाइल-अनुकूलित** - किसी भी डिवाइस पर काम करता है

---

## 📋 Requirements

- Python 3.7+
- pip (Python package manager)
- FFmpeg (for pydub audio processing)

---

## 🚀 Installation & Setup

### 1. **Clone या Project को डाउनलोड करें**

```bash
cd hindi-tts
```

### 2. **आवश्यक Packages इंस्टॉल करें**

```bash
pip install -r requirements.txt
```

**Windows पर FFmpeg के लिए:**
```bash
choco install ffmpeg
```

**macOS पर:**
```bash
brew install ffmpeg
```

**Linux पर:**
```bash
sudo apt-get install ffmpeg
```

### 3. **Flask ऐप चलाएं**

```bash
python app.py
```

### 4. **ब्राउज़र में खोलें**

```
http://localhost:5000
```

---

## 🎯 How to Use

1. **पाठ दर्ज करें** - बड़े टेक्स्ट को टेक्सटएरिया में पेस्ट करें
2. **ऑडियो उत्पन्न करें** - "ऑडियो उत्पन्न करें" बटन दबाएं
3. **प्रतीक्षा करें** - सिस्टम ऑडियो प्रक्रिया कर रहा है
4. **सुनें** - बिल्ट-इन प्लेयर में ऑडियो सुनें
5. **डाउनलोड करें** - MP3 फाइल डाउनलोड करें

---

## 📁 Project Structure

```
hindi-tts/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── README.md             # यह फाइल
├── templates/
│   └── index.html        # HTML template
├── static/
│   ├── style.css         # CSS styling
│   ├── script.js         # JavaScript functionality
│   └── output/           # Generated MP3 files
└── temp_audio/           # Temporary audio chunks
```

---

## 🛠️ Technical Details

### Backend (Python/Flask)

**Key Functions:**
- `split_text_into_chunks()` - बड़े पाठ को छोटे हिस्सों में विभाजित करता है
- `generate()` - `/generate` route - ऑडियो उत्पन्न करता है
- `download()` - `/download/<filename>` route - MP3 डाउनलोड करता है
- `cleanup_old_files()` - 24 घंटों के बाद पुरानी फाइलें हटाता है

**Features:**
- Thread-based cleanup system
- Automatic file management
- Error handling for invalid input
- Security measures against path traversal

### Frontend (HTML/CSS/JavaScript)

**Technologies:**
- Vanilla JavaScript (ES6+)
- CSS3 with animations
- HTML5
- AJAX for async requests

**Features:**
- Real-time character counter
- Loading spinner with animations
- Audio player integration
- LocalStorage support
- Network status detection
- Paste validation

### Audio Processing

- **gTTS** - Google Text-to-Speech API for Hindi TTS
- **pydub** - Audio file manipulation and merging
- **FFmpeg** - Audio encoding

---

## ⚙️ Configuration

Edit `app.py` to customize:

```python
MAX_CHARS = 10000          # Maximum characters
CHUNK_SIZE = 500           # Size of text chunks
CLEANUP_INTERVAL = 3600    # Cleanup interval in seconds
```

---

## 🔒 Security Features

✅ Input validation
✅ File path traversal protection
✅ Automatic cleanup of old files
✅ Error messages without system details
✅ Safe file handling
✅ Thread-safe operations

---

## 🐛 Troubleshooting

### **FFmpeg not found**
```bash
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### **Port 5000 already in use**
```bash
# Change port in app.py
if __name__ == '__main__':
    app.run(port=5001)  # Change to different port
```

### **ImportError: No module named 'gtts'**
```bash
pip install -r requirements.txt
```

### **Audio merge fails**
Ensure FFmpeg is properly installed and in PATH

### **Permission denied on output folder**
```bash
chmod 755 static/output
chmod 755 temp_audio
```

---

## 📊 Performance

- **Maximum Text**: 10,000 characters
- **Processing Time**: 30 seconds - 5 minutes (depends on text length)
- **Output Quality**: 192kbps MP3
- **File Cleanup**: Every 1 hour
- **Temp Files**: Cleaned up after processing

---

## 🌍 Deployment

### **Heroku के लिए:**

```bash
# Create Procfile
echo "web: python app.py" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### **PythonAnywhere के लिए:**

1. अपनी फाइलें अपलोड करें
2. Web app बनाएं
3. WSGI configuration सेट करें
4. Reload बटन दबाएं

### **AWS/DigitalOcean:**

1. Server सेट अप करें
2. Dependencies इंस्टॉल करें
3. Gunicorn का उपयोग करें:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📝 License

यह प्रोजेक्ट MIT License के अंतर्गत है।

---

## 👨‍💻 Developer

**Built with ❤️ using Python, Flask, and gTTS**

---

## 🤝 Contributing

योगदान स्वागत है! कृपया:

1. Repository को Fork करें
2. Feature branch बनाएं (`git checkout -b feature/amazing`)
3. Changes commit करें (`git commit -am 'Add amazing feature'`)
4. Branch को Push करें (`git push origin feature/amazing`)
5. Pull Request खोलें

---

## 📞 Support

समस्याओं के लिए:
- Issues tab खोलें
- विस्तृत विवरण प्रदान करें
- Error messages अनुलग्न करें

---

## 🙏 Credits

- **gTTS** - Google Text-to-Speech
- **Flask** - Web Framework
- **pydub** - Audio Processing
- **FFmpeg** - Audio Encoding

---

**हिंदी में लिखित टेक्स्ट को आसानी से सुंदर ऑडियो में बदलें!**

**Enjoy converting Hindi text to beautiful audio easily!** 🎵
