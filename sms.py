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
