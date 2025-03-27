from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import translate_v2 as translate
from twilio.rest import Client
import os
import json

# ✅ Load Firebase credentials
firebase_json = os.getenv("FIREBASE_KEY")
cred_dict = json.loads(firebase_json)
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ✅ Load Google Cloud credentials
google_credentials = json.loads(os.getenv("GOOGLE_CRED"))
with open("service-account-key.json", "w") as f:
    json.dump(google_credentials, f)
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
    user_phone = request.form.get('From')

    # ✅ Ensure it's a WhatsApp message
    if not user_phone.startswith("whatsapp:"):
        return str(MessagingResponse())  # Ignore non-WhatsApp messages

    user_phone = user_phone.replace("whatsapp:", "").strip()
    incoming_msg = request.form.get('Body').strip()

    response = MessagingResponse()
    user_data = get_user_data(user_phone)

    # ✅ Detect language for new users
    if not user_data:
        detected_lang = translate_client.detect_language(incoming_msg)['language']
        
        # ✅ Ensure only supported Indian languages are used
        supported_languages = ["hi", "bn", "ta", "te", "mr", "gu", "ml", "kn", "pa", "ur"]
        if detected_lang not in supported_languages:
            detected_lang = "hi"  # Default to Hindi if not supported

        user_data = {"language": detected_lang, "earnings": 0}
        set_user_data(user_phone, user_data)

        translated_msg = translate_client.translate(
            "Your language has been set. Reply with 'TASK' to earn!", target_language=detected_lang
        )['translatedText']
        
        response.message(translated_msg)
        return str(response)

    lang = user_data["language"]

    # ✅ Process user commands
    if incoming_msg.lower() == "task":
        task_text = "Here is your simple task: Solve 5 + 3 = ?"
        translated_task = translate_client.translate(task_text, target_language=lang)['translatedText']
        response.message(translated_task)

    elif incoming_msg.lower() == "balance":
        balance_text = f"Your total earnings: ₹{user_data['earnings']}."
        translated_balance = translate_client.translate(balance_text, target_language=lang)['translatedText']
        response.message(translated_balance)

    else:
        invalid_text = "Invalid response. Reply 'TASK' to start."
        translated_msg = translate_client.translate(invalid_text, target_language=lang)['translatedText']
        response.message(translated_msg)

    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
