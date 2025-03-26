

from twilio.rest import Client
import os

# Twilio credentials (replace with yours)


print("TWILIO_SID:", os.getenv("TWILIO_SID"))  # Debugging
print("TWILIO_AUTH_TOKEN:", os.getenv("TWILIO_AUTH_TOKEN"))  # Debugging
print("TWILIO_PHONE_NUMBER:", os.getenv("TWILIO_PHONE_NUMBER"))  # Debugging

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_sms(user_phone, message):
    sms = client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=user_phone
    )
    return sms.sid  # Returns SMS ID (for tracking)

# Test sending SMS
send_sms("+917386858392", "Welcome! Reply 'JOIN' to start earning.")


from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['POST'])
def sms_reply():
    incoming_msg = request.form.get('Body').strip().lower()
    user_phone = request.form.get('From')

    response = MessagingResponse()

    if incoming_msg == "join":
        response.message("Welcome! You can now start earning by completing tasks. Reply 'TASK' to begin.")
    elif incoming_msg == "task":
        response.message("Your first task: Label an image. Click here: https://yourwebsite.com/tasks")
    else:
        response.message("Invalid response. Reply 'JOIN' to start.")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
