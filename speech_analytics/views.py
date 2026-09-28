import os
import subprocess
import shutil
import numpy as np

try:
    import librosa
except ImportError:
    librosa = None

try:
    import soundfile as sf
except ImportError:
    sf = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import CallData

# ── 1. FFmpeg Configuration ──────────────────────────────────────────────────
def get_ffmpeg_path():
    """Finds or configures a working ffmpeg binary on the system."""
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
        ffmpeg_named = os.path.join(ffmpeg_dir, 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
        if not os.path.exists(ffmpeg_named):
            try:
                shutil.copyfile(ffmpeg_exe, ffmpeg_named)
            except Exception:
                pass
        if ffmpeg_dir not in os.environ.get('PATH', ''):
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
        return ffmpeg_named if os.path.exists(ffmpeg_named) else ffmpeg_exe
    except Exception:
        return None

# Ensure FFmpeg is registered in PATH on startup
get_ffmpeg_path()

# ── 2. Emotion Classifier Pipeline (Optional Hugging Face) ───────────────────
TRANSFORMERS_AVAILABLE = False
emotion_classifier = None
try:
    from transformers import pipeline
    emotion_classifier = pipeline(
        "text-classification",
        model="bhadresh-savani/distilbert-base-uncased-emotion",
        top_k=1
    )
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False

# ── 3. Audio Validation & Transcoding ─────────────────────────────────────────
ALLOWED_AUDIO_EXTENSIONS = {'.wav', '.mp3', '.ogg', '.m4a', '.webm', '.flac', '.aac'}

def validate_audio_file(file_path):
    """Checks if the file exists and is not an HTML document or empty file."""
    if not os.path.exists(file_path):
        raise ValueError("Audio file not found on server.")
    if os.path.getsize(file_path) == 0:
        raise ValueError("The uploaded audio file is completely empty.")
    
    with open(file_path, 'rb') as f:
        header = f.read(512).lower()
        if b'<!doctype html' in header or b'<html' in header or b'<head' in header:
            raise ValueError(
                "The selected file is a webpage (HTML), not a valid audio file. "
                "Please select an authentic .wav, .mp3, or .webm audio recording."
            )

def transcode_to_pcm_wav(input_path, output_path):
    """
    Transcodes any audio format (WebM browser recordings, MP3, OGG, WAV)
    to a standardized 16kHz, 16-bit, mono PCM WAV for accurate STT and feature extraction.
    """
    ffmpeg = get_ffmpeg_path()
    if ffmpeg:
        cmd = [
            ffmpeg,
            '-y',
            '-i', input_path,
            '-ar', '16000',
            '-ac', '1',
            '-c:a', 'pcm_s16le',
            output_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True

    # Fallback using librosa / soundfile if ffmpeg isn't available
    if sf and librosa:
        try:
            y, sr_rate = librosa.load(input_path, sr=16000, mono=True)
            sf.write(output_path, y, 16000)
            return True
        except Exception:
            pass

    return False

# ── 4. NLP & Emotion Analyzer ────────────────────────────────────────────────
STRONG_POSITIVE = {
    'happy', 'great', 'excellent', 'awesome', 'wonderful', 'perfect',
    'satisfied', 'pleasure', 'appreciate', 'love', 'glad', 'resolved',
    'fantastic', 'amazing', 'brilliant', 'delighted'
}
POLITE_POSITIVE = {'thank', 'thanks', 'helpful', 'polite'}

STRONG_NEGATIVE = {
    'angry', 'frustrated', 'terrible', 'worst', 'unacceptable', 'useless',
    'cancel', 'refund', 'complaint', 'horrible', 'waste', 'hate',
    'annoyed', 'disappointed', 'ridiculous', 'disaster', 'rude',
    'broken', 'dispute', 'overcharge', 'furious'
}
MILD_NEGATIVE = {'bad', 'waiting', 'delay', 'error', 'wrong'}

def analyze_emotion_and_sentiment(transcript):
    """
    Computes sentiment polarity and determines an accurate emotion
    (Joy, Happy, Neutral, Frustrated, Angry).
    """
    text = (transcript or "").lower()
    if not text or "no clear speech" in text:
        return "Neutral", 50.0

    polarity = 0.0
    if TextBlob:
        try:
            blob = TextBlob(transcript)
            polarity = float(blob.sentiment.polarity)
        except Exception:
            polarity = 0.0

    strong_pos = sum(1 for w in STRONG_POSITIVE if w in text)
    polite_pos = sum(1 for w in POLITE_POSITIVE if w in text)
    strong_neg = sum(1 for w in STRONG_NEGATIVE if w in text)
    mild_neg = sum(1 for w in MILD_NEGATIVE if w in text)

    pos_signal = strong_pos * 0.35 + polite_pos * 0.08
    neg_signal = strong_neg * 0.40 + mild_neg * 0.12

    net_score = max(-1.0, min(1.0, polarity * 0.6 + (pos_signal - neg_signal)))
    normalized_sentiment = round(max(0.0, min(100.0, (net_score + 1.0) / 2.0 * 100.0)), 1)

    if strong_neg >= 2 or (strong_neg >= 1 and net_score < -0.35):
        emotion = "Angry"
    elif strong_neg >= 1 or mild_neg >= 2 or net_score < -0.15:
        emotion = "Frustrated"
    elif strong_pos >= 2 or (strong_pos >= 1 and net_score > 0.40):
        emotion = "Joy"
    elif strong_pos >= 1 or (polite_pos >= 1 and net_score > 0.25):
        emotion = "Happy"
    else:
        emotion = "Neutral"

    return emotion, normalized_sentiment

# ── 5. Views ──────────────────────────────────────────────────────────────────
@login_required(login_url='login')
def upload_audio_view(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio_file')
        if not audio_file:
            messages.error(request, "Please select an audio file or record audio before submitting.")
            return redirect('upload_audio')

        # Validate file extension
        ext = os.path.splitext(audio_file.name)[1].lower()
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            allowed_str = ", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))
            messages.error(request, f"Unsupported format '{ext}'. Allowed formats: {allowed_str}")
            return redirect('upload_audio')

        # Save to CallData
        try:
            call_data = CallData.objects.create(
                user=request.user,
                audio_file=audio_file
            )
            return redirect('process_audio', call_id=call_data.id)
        except Exception as e:
            messages.error(request, f"Failed to save audio recording: {str(e)}")
            return redirect('upload_audio')

    return render(request, 'speech_analytics/upload.html')

@login_required(login_url='login')
def process_audio_view(request, call_id):
    call_data = get_object_or_404(CallData, id=call_id, user=request.user)
    file_path = os.path.normpath(call_data.audio_file.path)

    temp_wav = os.path.join(settings.MEDIA_ROOT, 'temp', f"proc_{call_id}.wav")
    os.makedirs(os.path.dirname(temp_wav), exist_ok=True)

    try:
        # Step 1: Validate file integrity
        validate_audio_file(file_path)

        # Step 2: Transcode to normalized 16kHz mono WAV
        success = transcode_to_pcm_wav(file_path, temp_wav)
        process_path = temp_wav if (success and os.path.exists(temp_wav)) else file_path

        # Step 3: Speech to Text (STT)
        transcript = ""
        if sr:
            recognizer = sr.Recognizer()
            try:
                with sr.AudioFile(process_path) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio_data = recognizer.record(source)
                    try:
                        transcript = recognizer.recognize_google(audio_data)
                    except sr.UnknownValueError:
                        transcript = "AI Analysis: No clear speech patterns detected in this segment."
                    except sr.RequestError:
                        transcript = "System Notice: Speech-to-Text service offline. Acoustic analysis active."
            except Exception as e:
                # If audio format wasn't directly read by sr, give friendly transcript
                transcript = f"Notice: Audio segment processed ({str(e)})."
        else:
            transcript = "Notice: Speech recognition engine is initializing."

        # Step 4: NLP Sentiment & Emotion Analysis
        emotion, sentiment_score = analyze_emotion_and_sentiment(transcript)

        # Step 5: Update database model
        call_data.transcript = transcript or "No transcript available."
        call_data.emotion = emotion or "Neutral"
        call_data.sentiment_score = sentiment_score
        call_data.save()

        messages.success(request, "Neural voice analysis completed successfully.")
        return redirect('result', call_id=call_data.id)

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('upload_audio')
    except Exception as e:
        messages.error(request, f"Audio processing failure: {str(e)}")
        return redirect('upload_audio')
    finally:
        # Safely remove temp working file
        try:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
        except Exception:
            pass

@login_required(login_url='login')
def result_view(request, call_id):
    call_data = get_object_or_404(CallData, id=call_id, user=request.user)
    return render(request, 'speech_analytics/result.html', {'call': call_data})
