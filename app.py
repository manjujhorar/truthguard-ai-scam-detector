from flask import Flask, render_template, request
from dotenv import load_dotenv
load_dotenv()
from translations import translations
import os
import re
import requests  # 🔧 MISSING IMPORT
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

google_api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'mp3', 'wav'}

official_domains = [
    "gmail.com", "yahoo.com", "outlook.com",
    "airindia.com", "spicejet.com", "indigo.in",
    "goindigo.in", "airvistara.com", "jetairways.com"
]

indian_number_pattern = re.compile(r'^(?:\+91|91|0)?[6-9]\d{9}$')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_number_validity(input_text):
    number_pattern = re.compile(r'(\+91)?[6-9]\d{9}')
    flagged_numbers = []

    for match in re.finditer(number_pattern, input_text):
        number = match.group()
        clean_number = number[-10:]
        if len(set(clean_number)) == 1:
            flagged_numbers.append((number, "⚠️ Repeated digits – possible spam"))
        else:
            flagged_numbers.append((number, "ℹ️ Please verify this number on Truecaller"))
    return flagged_numbers

def check_url_with_google_safe_browsing(api_key, url_to_check):
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    body = {
        "client": {
            "clientId": "truthguard-ai",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url_to_check}]
        }
    }

    try:
        response = requests.post(api_url, json=body)  # 🔧 FIXED VARIABLE NAME (was: safe_browsing_url)
        if response.status_code == 200:
            result = response.json()
            if "matches" in result:
                return "❌ This link is potentially dangerous (malware/phishing)."
            else:
                return "✅ This link appears safe."
        else:
            return "⚠️ Could not check the link. Try again."
    except Exception:
        return "⚠️ Error checking link with Google Safe Browsing."

def transcribe_audio(file_path):
    r = sr.Recognizer()
    audio = AudioSegment.from_file(file_path)
    audio.export("temp.wav", format="wav")
    with sr.AudioFile("temp.wav") as source:
        audio_data = r.record(source)
        try:
            return r.recognize_google(audio_data)
        except sr.UnknownValueError:
            return ""

@app.route('/', methods=['GET', 'POST'])
def home():
    lang = request.args.get('lang', 'en')
    labels = translations.get(lang, translations['en'])

    result = ""
    user_input = ""
    cybercrime_info = False
    offer_text = ""

    if request.method == 'POST':
        if 'email' in request.form:
            user_input = request.form['email'].strip()
            if '@' in user_input:
                domain = user_input.split('@')[-1]
                if domain in official_domains:
                    result = labels['result_verified']
                else:
                    result = labels['result_fake']
                    cybercrime_info = True
            elif indian_number_pattern.match(user_input):
                number_results = check_number_validity(user_input)
                result = "<br>".join(f"{num}: {note}" for num, note in number_results)
                cybercrime_info = any("⚠️" in note for _, note in number_results)
            else:
                result = labels['result_invalid_number']
                cybercrime_info = True

        if 'offer_file' in request.files:
            file = request.files['offer_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)

                extension = filename.rsplit('.', 1)[1].lower()
                suspicious_keywords = ['lottery', 'you have won', 'urgent', 'click here', 'verify now', 'limited offer']
                verified_keywords = ['thank you for your application', 'your interview is scheduled', 'we appreciate your interest']

                try:
                    if extension == "pdf":
                        images = convert_from_path(path)
                        for img in images:
                            offer_text += pytesseract.image_to_string(img)

                    elif extension in ['png', 'jpg', 'jpeg']:
                        img = Image.open(path)
                        offer_text = pytesseract.image_to_string(img)

                    elif extension in ['mp3', 'wav']:
                        offer_text = transcribe_audio(path)

                    if offer_text and any(word in offer_text.lower() for word in suspicious_keywords):
                        result = "❌ This file may contain SCAM content!"
                        cybercrime_info = True
                    elif offer_text and any(word in offer_text.lower() for word in verified_keywords):
                        result = labels['offer_real']
                    elif offer_text:
                        result = labels['offer_fake']
                        cybercrime_info = True
                    else:
                        result = "⚠️ Could not read the content. Try another file."
                        cybercrime_info = True

                except Exception:
                    result = labels['offer_error']
                    cybercrime_info = True

        if 'user_message' in request.form:
            message = request.form['user_message'].lower()
            suspicious_keywords = ['congratulations', 'lottery', 'click the link', 'urgent', 'bank account', 'you have won', 'limited offer', 'verify now']
            real_keywords = ['thank you for your application', 'your interview is scheduled', 'we appreciate your interest']

            url_pattern = re.compile(r'https?://[^\s]+')
            urls = url_pattern.findall(message)

            if urls:
                result = ""
                for url in urls:
                    result += check_url_with_google_safe_browsing(google_api_key, url) + "<br>"
                cybercrime_info = True
            elif any(word in message for word in suspicious_keywords):
                result = "❌ This message may be a SCAM. Be careful!"
                cybercrime_info = True
            elif any(word in message for word in real_keywords):
                result = "✅ This message seems genuine."
            else:
                result = "⚠️ Could not determine. Please verify manually."

    return render_template("index.html",
        labels=labels,
        lang=lang,
        result=result,
        user_input=user_input,
        cybercrime_info=cybercrime_info,
        offer_text=offer_text,
        download_poster="Download Poster",
        offer_result=result if 'offer_file' in request.files else "")

if __name__ == "__main__":
    app.run(debug=True)

