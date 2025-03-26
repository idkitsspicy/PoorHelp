

from twilio.rest import Client

# Twilio credentials (replace with yours)
TWILIO_SID = "ACbd3ded0f95fcf4ae58a1d510b533de51"
TWILIO_AUTH_TOKEN = "920dd511217f5f8cc5712597e5668b57"
TWILIO_PHONE_NUMBER = "+13092716987"

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_sms(user_phone, message):
    sms = client.messages.create(
        body=message,
        from_=+13092716987,
        to=+917386858392
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
    user_phone = request.form.get('from')

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
