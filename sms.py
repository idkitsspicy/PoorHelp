from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import translate_v2 as translate
from twilio.rest import Client
import os
import json

# ✅ Load Firebase credentials from GitHub Secrets
firebase_config = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
}

# ✅ Initialize Firebase only once
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ Load Google Cloud Credentials from GitHub Secrets
google_credentials = json.loads(os.getenv("GOOGLE_CRED"))
# ✅ Save Google credentials as a temporary JSON file
with open("service-account-key.json", "w") as f:
    json.dump(google_credentials, f)

# ✅ Set the environment variable for Google API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account-key.json"

# ✅ Initialize Google Translate API
translate_client = translate.Client()

# ✅ Twilio Configuration
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# ✅ Flask App
app = Flask(__name__)

# 📌 Function to get user data from Firebase
def get_user_data(phone):
    doc = db.collection("users").document(phone).get()
    return doc.to_dict() if doc.exists else None

# 📌 Function to store/update user data
def set_user_data(phone, data):
    db.collection("users").document(phone).set(data, merge=True)

@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body').strip()
    user_phone = request.form.get('From')

    response = MessagingResponse()
    user_data = get_user_data(user_phone)

    # ✅ Detect language for new users
    if not user_data:
        detected_lang = translate_client.detect_language(incoming_msg)['language']
        user_data = {"language": detected_lang, "earnings": 0}
        set_user_data(user_phone, user_data)
        response.message(f"भाषा सेट हो गई: {detected_lang.upper()}! 'TASK' लिखें कमाने के लिए।")
        return str(response)

    lang = user_data["language"]

    # ✅ Process user commands
    if incoming_msg.lower() == "task":
        translated_task = translate_client.translate(
            "Here is your simple task: Solve 5 + 3 = ?", target_language=lang
        )['translatedText']
        response.message(translated_task)

    elif incoming_msg.lower() == "balance":
        response.message(f"आपकी कुल कमाई: ₹{user_data['earnings']}।")

    else:
        translated_msg = translate_client.translate(
            "Invalid response. Reply 'TASK' to start.", target_language=lang
        )['translatedText']
        response.message(translated_msg)

    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
