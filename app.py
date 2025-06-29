from flask import Flask, render_template, request
import re

app = Flask(__name__)

# Trusted email domains (real company domains)
official_domains = [
    "gmail.com", "yahoo.com", "outlook.com", "airindia.com", "spicejet.com",
    "indigo.in", "goindigo.in", "airvistara.com", "jetairways.com"
]

# Translations dictionary (same as you provided)
translations = {
    'en': {
        'tool_name': "JHORAR AI – Scam Detector",  # ENGLISH में
        'header_tagline': "Online scams are smarter than ever—but so are we. Get an advanced, AI-powered anti-scam tool that follows all rules and policies.",  # ENGLISH में
        'input_label': "Enter email, number, or link",
        'submit': "Check",
        'result': "Result",
        'cybercrime_info': "🚨 If this appears suspicious, report to Cyber Crime India:\nPhone: 1930\nEmail: cybercrime.gov@nic.in\nWebsite: https://www.cybercrime.gov.in/",
        'result_verified': "✅ This is a verified official email domain.",
        'result_suspicious': "⚠️ This looks like a suspicious domain similar to official one.",
        'result_fake': "❌ This email is likely FAKE. Do not trust. This is an AI-based tool. Please double check before final decision.",
        'result_valid_number': "✅ This appears to be a valid Indian WhatsApp number.",
        'result_invalid_number': "⚠️ This number is not in valid Indian WhatsApp format.",
        'result_verified_social': "✅ This may be a verified social profile.",
        'result_suspicious_social': "⚠️ This social link may be suspicious or unverified.",
        'result_invalid': "⚠️ Unrecognized format. Please enter a valid email, number, or link.",
        'benefits_title': "Benefits of Using JHORAR AI",
        'benefit_1': "✔️ Real-time scam detection",
        'benefit_2': "✔️ Multi-language awareness",
        'benefit_3': "✔️ 100% free educational tool",
        'benefit_4': "✔️ No user data stored",
        'benefit_5': "✔️ WhatsApp, email, and link scanner",
        'benefit_6': "✔️ Cybercrime info if fraud found",
        'benefit_7': "✔️ Compliant with all policies",
        'other_tools_title': "Other AI Scam Detection Tools",
        'tool_1': "🛡️ ScamAdviser",
        'tool_2': "🛡️ Norton Safe Web",
        'tool_3': "🛡️ VirusTotal",
        'footer_disclaimer': "This tool provides basic scam detection and does not store any user data.",
        'founder_line': "Founder: Manju Jhorar | Created: 2025 | Contact: 8930765334 | Email: rjhorar514@gmail.com"
    },
    'hi': {
        'tool_name': "झोरड़ एआई – स्कैम डिटेक्टर",
        'header_tagline': "ऑनलाइन ठगी पहले से ज्यादा होशियार है—but अब हम भी। यह एक AI आधारित टूल है जो सभी नियमों का पालन करता है।",
        'input_label': "ईमेल, नंबर, या लिंक दर्ज करें",
        'submit': "जांचें",
        'result': "परिणाम",
        'cybercrime_info': "🚨 यदि यह संदिग्ध लगे, तो साइबर क्राइम इंडिया में रिपोर्ट करें:\nफोन: 1930\nईमेल: cybercrime.gov@nic.in\nवेबसाइट: https://www.cybercrime.gov.in/",
        'result_verified': "✅ यह एक सत्यापित आधिकारिक ईमेल डोमेन है।",
        'result_suspicious': "⚠️ यह डोमेन किसी आधिकारिक डोमेन जैसा दिख रहा है, लेकिन संदिग्ध हो सकता है।",
        'result_fake': "❌ यह ईमेल शायद फेक है। कृपया विश्वास न करें। यह एक एआई आधारित टूल है, कृपया अंतिम निर्णय से पहले डबल चेक करें।",
        'result_valid_number': "✅ यह एक वैध भारतीय व्हाट्सएप नंबर प्रतीत होता है।",
        'result_invalid_number': "⚠️ यह नंबर भारतीय व्हाट्सएप फॉर्मेट में नहीं है।",
        'result_verified_social': "✅ यह एक सत्यापित सोशल प्रोफाइल हो सकती है।",
        'result_suspicious_social': "⚠️ यह सोशल लिंक संदिग्ध या असत्यापित हो सकती है।",
        'result_invalid': "⚠️ अमान्य प्रारूप। कृपया एक वैध ईमेल, नंबर या लिंक दर्ज करें।",
        'benefits_title': "झोरड़ एआई के लाभ",
        'benefit_1': "✔️ रियल-टाइम स्कैम डिटेक्शन",
        'benefit_2': "✔️ बहुभाषा समर्थन",
        'benefit_3': "✔️ 100% मुफ्त शैक्षिक टूल",
        'benefit_4': "✔️ कोई उपयोगकर्ता डेटा संग्रहीत नहीं किया जाता",
        'benefit_5': "✔️ व्हाट्सएप, ईमेल और लिंक स्कैनर",
        'benefit_6': "✔️ फ्रॉड मिलने पर साइबर क्राइम जानकारी",
        'benefit_7': "✔️ सभी नीतियों का पालन करता है",
        'other_tools_title': "अन्य एआई स्कैम डिटेक्शन टूल",
        'tool_1': "🛡️ स्कैमएडवाइज़र",
        'tool_2': "🛡️ नॉर्टन सेफ वेब",
        'tool_3': "🛡️ वायरस टोटल",
        'footer_disclaimer': "यह टूल मूलभूत स्कैम डिटेक्शन प्रदान करता है और आपका डेटा संग्रहीत नहीं करता।",
        'founder_line': "संस्थापक: मंजू झोरड़ | निर्माण वर्ष: 2025 | संपर्क: 8930765334 | ईमेल: rjhorar514@gmail.com"
    },
    'ha': {
        'tool_name': "झोरड़ एआई – ठगी पकड़न वाला टूल",
        'header_tagline': "ऑनलाइन चोर अब चालाक हो लिए—but यो टूल और चालाक सै। ये AI टूल कानून के पूरे नियम मानै सै।",
        'input_label': "ईमेल, नंबर या लिंक डालो",
        'submit': "जांच करो",
        'result': "नतीजा",
        'cybercrime_info': "🚨 यो संदिग्ध लागे तो साइबर क्राइम इंडिया म रिपोर्ट करो:\nफोन: 1930\nईमेल: cybercrime.gov@nic.in\nवेबसाइट: https://www.cybercrime.gov.in/",
        'result_verified': "✅ यो एकदम सच्चा ऑफिशियल ईमेल लागे स।",
        'result_suspicious': "⚠️ यो डोमेन ऑफिशियल जैसां लागे स, पर थोडा संदिग्ध स।",
        'result_fake': "❌ यो ईमेल फर्जी स। भरोसा मत करियो। यो एक AI टूल स, पक्का करले पहले।",
        'result_valid_number': "✅ यो एक सही इंडियन WhatsApp नंबर लागे स।",
        'result_invalid_number': "⚠️ यो नंबर इंडिया वाला WhatsApp फॉर्मेट में ना स।",
        'result_verified_social': "✅ यो प्रोफाइल असली लागे स।",
        'result_suspicious_social': "⚠️ यो लिंक संदिग्ध हो सके स।",
        'result_invalid': "⚠️ यो सही फॉर्मेट में ना स। सही ईमेल, नंबर या लिंक डालो।",
        'benefits_title': "झोरड़ एआई के फायदे",
        'benefit_1': "✔️ झटपट स्कैम पकड़ण",
        'benefit_2': "✔️ कई भाषा में चलण",
        'benefit_3': "✔️ बिलकुल फ्री टूल",
        'benefit_4': "✔️ यूजर का डाटा स्टोर ना होवे",
        'benefit_5': "✔️ WhatsApp, email, link जांचण वाला",
        'benefit_6': "✔️ धोखा मिलते ही Cybercrime की जानकारी",
        'benefit_7': "✔️ सारे कानून और नीति फॉलो करै",
        'other_tools_title': "दुसरे स्कैम पकड़न वाले एआई टूल",
        'tool_1': "🛡️ स्कैम एडवाइजर",
        'tool_2': "🛡️ नॉर्टन सेफ वेब",
        'tool_3': "🛡️ वायरस टोटल",
        'footer_disclaimer': "यो टूल बेसिक स्कैम डिटेक्शन देवे सै, और डेटा सेव ना करे सै।",
        'founder_line': "फाउंडर: मंजू झोरड़ | बणया गया: 2025 | कॉन्टैक्ट: 8930765334 | ईमेल: rjhorar514@gmail.com"
    }
}

# Indian WhatsApp number pattern
whatsapp_pattern = re.compile(r'(\+91[\d]{10}|0[\d]{10}|[\d]{10})')

@app.route('/', methods=['GET', 'POST'])
def home():
    lang = request.args.get('lang', 'en')
    labels = translations.get(lang, translations['en'])

    result = ""
    user_input = ""
    cybercrime_info = False

    if request.method == 'POST':
        user_input = request.form['email']

        if '@' in user_input:
            domain = user_input.split('@')[-1]
            if domain in official_domains:
                result = labels['result_verified']
            elif any(org in domain for org in ["spicejet", "airindia", "indigo"]):
                result = labels['result_suspicious']
                cybercrime_info = True
            else:
                result = labels['result_fake']
                cybercrime_info = True

        elif whatsapp_pattern.match(user_input):
            if user_input.startswith("+91") or user_input.startswith("0") or len(user_input) == 10:
                result = labels['result_valid_number']
            else:
                result = labels['result_invalid_number']
                cybercrime_info = True

        elif "facebook.com" in user_input or "instagram.com" in user_input or "linkedin.com" in user_input:
            if "official" in user_input or "verified" in user_input:
                result = labels['result_verified_social']
            else:
                result = labels['result_suspicious_social']
                cybercrime_info = True
        else:
            result = labels['result_invalid']
            cybercrime_info = True

    return render_template("index.html",
                           result=result,
                           user_input=user_input,
                           cybercrime_info=cybercrime_info,
                           labels=labels,
                           lang=lang)

if __name__ == '__main__':
    app.run(debug=True)
