from flask import Flask, request, jsonify
import datetime
import time
import threading
import logging
import os
from dotenv import load_dotenv
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# In-memory storage for appointments (replace with a database in a real application)
appointments = []

def send_sms(patient_name, appointment_time, contact_number):
    """Sends an SMS reminder using Twilio."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=f"Reminder: {patient_name}, your appointment is at {appointment_time:%Y-%m-%d %H:%M}.",
            from_=TWILIO_PHONE_NUMBER,
            to=contact_number
        )
        logging.info(f"SMS sent to {patient_name} at {contact_number}. Message SID: {message.sid}")
    except Exception as e:
        logging.error(f"Error sending SMS to {patient_name}: {e}")

def send_whatsapp(patient_name, appointment_time, whatsapp_number):
    """Sends a WhatsApp reminder using Twilio."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=f"Reminder: {patient_name}, your appointment is at {appointment_time:%Y-%m-%d %H:%M}.",
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{whatsapp_number}"
        )
        logging.info(f"WhatsApp message sent to {patient_name} at {whatsapp_number}. Message SID: {message.sid}")
    except Exception as e:
        logging.error(f"Error sending WhatsApp message to {patient_name}: {e}")

def send_email(patient_name, appointment_time, email_address):
    """Sends an email reminder using SendGrid."""
    message = Mail(
        from_email='your_email@example.com',  # Replace with your SendGrid verified email
        to_emails=email_address,
        subject='Appointment Reminder',
        html_content=f'Dear {patient_name},<br><br>Your appointment is scheduled for {appointment_time:%Y-%m-%d %H:%M}.<br><br>Best regards,<br>Your Clinic'
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logging.info(f"Email sent to {patient_name} at {email_address}. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending email to {patient_name}: {e}")

def make_voice_call(patient_name, appointment_time, contact_number):
    """Makes a voice call reminder using Twilio."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        call = client.calls.create(
            twiml=f'<Response><Say>Hello {patient_name}, this is a reminder about your appointment at {appointment_time:%Y-%m-%d %H:%M}.</Say></Response>',
            to=contact_number,
            from_=TWILIO_PHONE_NUMBER
        )
        logging.info(f"Voice call made to {patient_name} at {contact_number}. Call SID: {call.sid}")
    except Exception as e:
        logging.error(f"Error making voice call to {patient_name}: {e}")

def send_reminder(patient_name, appointment_time, contact_number, whatsapp_number, email_address, preferred_channel):
    """Sends a reminder via the patient's preferred channel."""
    now = datetime.datetime.now()
    remind_time = appointment_time - datetime.timedelta(hours=24)  # Remind 24 hours before

    if remind_time > now:
        wait_time = (remind_time - now).total_seconds()
        logging.info(f"Reminder for {patient_name} scheduled to send in {wait_time} seconds.")
        time.sleep(wait_time)

        if preferred_channel == 'sms':
            send_sms(patient_name, appointment_time, contact_number)
        elif preferred_channel == 'whatsapp':
            send_whatsapp(patient_name, appointment_time, whatsapp_number)
        elif preferred_channel == 'email':
            send_email(patient_name, appointment_time, email_address)
        elif preferred_channel == 'voice':
            make_voice_call(patient_name, appointment_time, contact_number)
        else:
            logging.warning(f"Invalid preferred channel: {preferred_channel}. Sending SMS as default.")
            send_sms(patient_name, appointment_time, contact_number)
    else:
        logging.warning(f"Cannot send reminder for {patient_name}; appointment is too soon.")

@app.route('/schedule', methods=['POST'])
def schedule_appointment():
    """Schedules an appointment and sets up a reminder."""
    data = request.get_json()
    patient_name = data.get('patient_name')
    appointment_time_str = data.get('appointment_time')
    contact_number = data.get('contact_number')
    whatsapp_number = data.get('whatsapp_number')
    email_address = data.get('email_address')
    preferred_channel = data.get('preferred_channel', 'sms')  # Default to SMS

    try:
        appointment_time = datetime.datetime.fromisoformat(appointment_time_str)
    except ValueError:
        return jsonify({'message': 'Invalid appointment time format. Use ISO format (YYYY-MM-DDTHH:MM:SS).'}), 400

    appointment = {
        'patient_name': patient_name,
        'appointment_time': appointment_time,
        'contact_number': contact_number,
        'whatsapp_number': whatsapp_number,
        'email_address': email_address,
        'preferred_channel': preferred_channel
    }
    appointments.append(appointment)

    # Create a thread for sending the reminder
    reminder_thread = threading.Thread(target=send_reminder,
                                       args=(patient_name, appointment_time, contact_number, whatsapp_number, email_address, preferred_channel))
    reminder_thread.start()

    logging.info(f"Appointment scheduled for {patient_name} at {appointment_time}.")
    return jsonify({'message': f'Appointment scheduled for {patient_name} at {appointment_time}. Reminder set via {preferred_channel}.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
