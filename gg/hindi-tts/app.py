from flask import Flask, render_template, request, jsonify, send_file
import asyncio
import edge_tts
import os
import shutil
from pathlib import Path
import time
from datetime import datetime, timedelta
import threading
import subprocess
import sys

app = Flask(__name__)

# Check if pydub is available
PYDUB_AVAILABLE = True
try:
    from pydub import AudioSegment
except ImportError:
    PYDUB_AVAILABLE = False

# Configuration
OUTPUT_FOLDER = 'static/output'
MAX_CHARS = 10000
CHUNK_SIZE = 500  # Chunk size for audio generation
TEMP_FOLDER = 'temp_audio'
CLEANUP_INTERVAL = 3600  # Cleanup every 1 hour

VOICE_MAP = {
    'Deep Male': 'hi-IN-MadhurNeural',
    'Natural Male': 'hi-IN-MadhurNeural',
    'Professional Male': 'hi-IN-MadhurNeural',
    'Soft Female': 'hi-IN-SwaraNeural',
    'Natural Female': 'hi-IN-SwaraNeural',
    'Professional Female': 'hi-IN-SwaraNeural',
}

SPEED_MAP = {
    # edge-tts expects rate as a percent change like "-20%" or "+20%".
    # "0%" can be rejected by some versions, so we map Normal to "+0%".
    'Slow': '-20%',
    'Normal': '+0%',
    'Fast': '+20%',
}

DEFAULT_VOICE = 'hi-IN-SwaraNeural'
DEFAULT_SPEED = '+0%'

PREVIEW_SAMPLE_TEXT = 'यह आवाज़ नमूना है। कृपया सुनें।'

# Ensure output folders exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)


def cleanup_old_files():
    """Remove files older than 24 hours"""
    def _cleanup():
        while True:
            try:
                time.sleep(CLEANUP_INTERVAL)
                now = time.time()
                for folder in [OUTPUT_FOLDER, TEMP_FOLDER]:
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        # Remove files older than 24 hours
                        if os.path.getmtime(file_path) < now - 86400:
                            try:
                                if os.path.isfile(file_path):
                                    os.remove(file_path)
                                elif os.path.isdir(file_path):
                                    shutil.rmtree(file_path)
                            except:
                                pass
            except:
                pass

    thread = threading.Thread(target=_cleanup, daemon=True)
    thread.start()


def split_text_into_chunks(text, chunk_size=CHUNK_SIZE):
    """Split text into manageable chunks"""
    sentences = text.split('। ')  # Split by Hindi period
    if len(sentences) == 1:
        # If no Hindi period, split by regular period
        sentences = text.split('. ')
    if len(sentences) == 1:
        # If still no period, split by lines
        sentences = text.split('\n')
    if len(sentences) == 1:
        # Last resort: character-based split
        sentences = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= chunk_size:
            current_chunk += sentence + "। "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + "। "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


async def save_edge_tts_audio(text, voice, rate, output_path):
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.save(output_path)


def generate_edge_tts_file(text, voice, rate, output_path):
    try:
        asyncio.run(save_edge_tts_audio(text, voice, rate, output_path))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(save_edge_tts_audio(text, voice, rate, output_path))
        loop.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/install-ffmpeg')
def install_ffmpeg():
    """Provide FFmpeg installation instructions"""
    return jsonify({
        'title': 'FFmpeg इंस्टॉलेशन गाइड',
        'message': 'ऑडियो मर्ज करने के लिए FFmpeg की आवश्यकता है।',
        'instructions': {
            'windows': {
                'option1': 'विकल्प 1: Chocolatey से (यदि इंस्टॉल है)',
                'command1': 'choco install ffmpeg',
                'option2': 'विकल्प 2: सीधे डाउनलोड करें',
                'download_url': 'https://ffmpeg.org/download.html',
                'or': 'या यहाँ से डाउनलोड करें:',
                'github_url': 'https://github.com/BtbN/FFmpeg-Builds/releases'
            },
            'macos': {
                'command': 'brew install ffmpeg'
            },
            'linux': {
                'command': 'sudo apt-get install ffmpeg'
            }
        }
    })


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json or {}
        text = data.get('text', '').strip()
        selected_voice = data.get('voice', '').strip()
        selected_speed = data.get('speed', 'Normal').strip()
        preview = bool(data.get('preview', False))
        
        # Voice and speed selection
        voice = VOICE_MAP.get(selected_voice, DEFAULT_VOICE)
        speed = SPEED_MAP.get(selected_speed, DEFAULT_SPEED)
        
        if preview:
            text = text or PREVIEW_SAMPLE_TEXT
        else:
            if not text:
                return jsonify({'success': False, 'error': 'कृपया पाठ दर्ज करें'}), 400
            if len(text) > MAX_CHARS:
                return jsonify({'success': False, 'error': f'पाठ {MAX_CHARS} वर्णों से अधिक नहीं हो सकता'}), 400
        
        # Create unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        output_filename = f'hindi_tts_{timestamp}.mp3'
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Split text into chunks
        chunks = split_text_into_chunks(text)
        
        if not chunks:
            return jsonify({'success': False, 'error': 'पाठ को संसाधित नहीं किया जा सका'}), 400
        
        # Generate audio for each chunk
        audio_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_path = os.path.join(TEMP_FOLDER, f'chunk_{timestamp}_{i}.mp3')
            try:
                generate_edge_tts_file(chunk, voice, speed, chunk_path)
                audio_chunks.append(chunk_path)
            except Exception as e:
                for chunk_file in audio_chunks:
                    try:
                        os.remove(chunk_file)
                    except:
                        pass
                return jsonify({'success': False, 'error': f'ऑडियो उत्पन्न करने में विफल: {str(e)}'}), 500
        
        # Merge all chunks
        try:
            if PYDUB_AVAILABLE:
                try:
                    combined = AudioSegment.empty()
                    
                    for chunk_path in audio_chunks:
                        audio = AudioSegment.from_mp3(chunk_path)
                        combined += audio
                    
                    combined.export(output_path, format='mp3', bitrate='192k')
                    merge_success = True
                except Exception as pydub_error:
                    merge_success = False
                    pydub_error_msg = str(pydub_error)
            else:
                merge_success = False
            
            if not merge_success and len(audio_chunks) > 0:
                try:
                    concat_file = os.path.join(TEMP_FOLDER, f'concat_{timestamp}.txt')
                    
                    with open(concat_file, 'w', encoding='utf-8') as f:
                        for chunk_path in audio_chunks:
                            escaped_path = chunk_path.replace('\\', '/')
                            f.write(f"file '{escaped_path}'\n")
                    
                    cmd = [
                        'ffmpeg',
                        '-f', 'concat',
                        '-safe', '0',
                        '-i', concat_file,
                        '-c', 'copy',
                        '-y',
                        output_path
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        merge_success = True
                    else:
                        raise Exception(f"FFmpeg command failed: {result.stderr}")
                    
                    try:
                        os.remove(concat_file)
                    except:
                        pass
                    
                except FileNotFoundError:
                    try:
                        if len(audio_chunks) == 1:
                            shutil.copy(audio_chunks[0], output_path)
                            merge_success = True
                        else:
                            shutil.copy(audio_chunks[0], output_path)
                            merge_success = True
                    except Exception as e:
                        merge_success = False
                        raise Exception(f"सरल प्रतिलिपि विधि विफल: {str(e)}")
                except Exception as e:
                    merge_success = False
                    raise Exception(f"FFmpeg मर्ज विफल: {str(e)}")
            
            for chunk_path in audio_chunks:
                try:
                    os.remove(chunk_path)
                except:
                    pass
            
            if merge_success:
                response_message = 'ऑडियो सफलतापूर्वक उत्पन्न हुई!' if not preview else 'वॉइस प्रीव्यू तैयार है!'
                return jsonify({
                    'success': True,
                    'message': response_message,
                    'filename': output_filename,
                    'download_url': f'/download/{output_filename}'
                })
            else:
                raise Exception('मर्ज विधि विफल - FFmpeg स्थापित नहीं है')
        
        except Exception as e:
            for chunk_path in audio_chunks:
                try:
                    os.remove(chunk_path)
                except:
                    pass
            error_msg = str(e)
            if 'FFmpeg' in error_msg or 'ffmpeg' in error_msg or 'cannot find' in error_msg.lower():
                error_msg = 'FFmpeg इंस्टॉल नहीं है। कृपया /install-ffmpeg पर जाएं।'
            return jsonify({'success': False, 'error': f'ऑडियो मर्ज करने में विफल: {error_msg}'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'सर्वर त्रुटि: {str(e)}'}), 500


@app.route('/download/<filename>')
def download(filename):
    try:
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return 'Invalid filename', 400
        
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return 'File not found', 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='audio/mpeg'
        )
    except Exception as e:
        return f'Download error: {str(e)}', 500


if __name__ == '__main__':
    # Start cleanup thread
    cleanup_old_files()
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
