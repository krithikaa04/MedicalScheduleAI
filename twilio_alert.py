# twilio_alert.py

from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your actual Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def call_emergency_contacts(emergency_contacts, message="This is an emergency alert. Please check on your loved one."):
    """
    Call all emergency contacts with a voice message using Twilio

    Args:
        emergency_contacts (list): List of emergency contact dicts
        message (str): Message to be converted to speech in the call
    """
    for contact in emergency_contacts:
        try:
            call = client.calls.create(
                to=contact["phone"],
                from_=TWILIO_PHONE_NUMBER,
                twiml=f'<Response><Say>{message}</Say></Response>'
            )
            print(f"Calling {contact['name']} at {contact['phone']}: Call SID {call.sid}")
        except Exception as e:
            print(f"Failed to call {contact['phone']}: {e}")
