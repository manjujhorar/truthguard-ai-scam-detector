import streamlit as st
import re
import whois
from langdetect import detect
from deep_translator import GoogleTranslator

def check_email(email):
    trusted_domains = ["gmail.com", "yahoo.com", "outlook.com"]
    if any(domain in email for domain in trusted_domains):
        return "✅ Common Email Domain - Likely Safe"
    elif ".gov" in email or ".edu" in email:
        return "✅ Likely Trusted"
    else:
        return "⚠️ Suspicious or Fake Email Domain"

def is_email_fake(email):
    flags = []
    if email.count("!") > 2:
        flags.append("Too many exclamation marks ❗")
    suspicious_keywords = ["lottery", "prize", "joboffers", "urgent", "free", "win"]
    found = [word for word in suspicious_keywords if word.lower() in email.lower()]
    if found:
        flags.append(f"Suspicious keywords found: {found}")
    if flags:
        return "⚠️ Suspicious", flags
    else:
        return "✅ Safe", []

def get_whois_info(domain):
    try:
        data = whois.whois(domain)
        return {
            "created": data.creation_date,
            "registrar": data.registrar,
            "country": data.country
        }
    except:
        return None

st.set_page_config(page_title="Jhorar AI – Scam Detector", layout="centered")
st.title("🔍 JHORAR AI – Scam Detector")
st.write("Multilingual Email Scam Detector with Cybercrime Help Section")

user_input = st.text_input("Enter an Email or Domain (e.g., hr@xyz.com):")

if st.button("Check Now") and user_input:
    lang = detect(user_input)
    if lang != 'en':
        prompt = GoogleTranslator(source='auto', target='en').translate(user_input)
    else:
        prompt = user_input

    result, reasons = is_email_fake(prompt)
    domain_status = check_email(prompt)
    domain_name = re.sub(r".*@", "", prompt) if "@" in prompt else prompt
    wi = get_whois_info(domain_name)

    def reply(text):
        return GoogleTranslator(source='en', target=lang).translate(text) if lang != 'en' else text

    st.markdown(f"### {reply('Scan Result')}: {reply(result)}")
    for r in reasons:
        st.write("•", reply(r))
    st.write(f"🌐 {reply('Domain Trust')}: {reply(domain_status)}")

    if wi:
        st.write("📅", reply("Registered On"), ":", wi.get("created"))
        st.write("🏢", reply("Registrar"), ":", wi.get("registrar"))
        st.write("🌍", reply("Country"), ":", wi.get("country"))

    if result.startswith("⚠️"):
        st.markdown("---")
        st.markdown(f"🚨 **{reply('This looks like a scam! You can report to Cyber Crime')}**")
        st.write("📞", reply("Helpline"), ": 1930")
        st.write("🌐", reply("Report Website"), ": cybercrime.gov.in")

st.write("© 2025 Jhorar AI | Designed with ❤️ by Founder Manju Jhorar")
