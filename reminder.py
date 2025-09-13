import streamlit as st
import database
from datetime import datetime, timedelta
import utils

def check_medication_reminders(username):
    """
    Check for medication reminders that need to be sent
    
    Args:
        username (str): The username to check reminders for
        
    Returns:
        list: List of medication reminders that should be sent
    """
    # Get today's date
    today = datetime.now().date()
    current_time = datetime.now()
    
    # Get the user's medications
    medications = database.get_medications(username)
    
    # Filter for medications that should be active today
    active_medications = []
    for med in medications:
        start_date = datetime.strptime(med['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(med['end_date'], "%Y-%m-%d").date()
        
        if start_date <= today <= end_date:
            active_medications.append(med)
    
    # Determine which medications need reminders
    reminders_to_send = []
    for med in active_medications:
        # Parse the timing to determine when the medication should be taken
        timing_info = utils.parse_medication_time(med['timing'])
        
        # Check if medication has been taken today
        if med.get('taken', False):
            taken_time = datetime.strptime(med.get('taken_at', ''), "%Y-%m-%d %H:%M:%S").date()
            if taken_time == today:
                continue  # Skip if already taken today
        
        # Determine the time to send the reminder based on the timing information
        reminder_time = None
        
        if timing_info['period'] == 'morning':
            reminder_time = datetime.combine(today, datetime.strptime('08:00', '%H:%M').time())
        elif timing_info['period'] == 'afternoon':
            reminder_time = datetime.combine(today, datetime.strptime('12:00', '%H:%M').time())
        elif timing_info['period'] == 'evening':
            reminder_time = datetime.combine(today, datetime.strptime('18:00', '%H:%M').time())
        elif timing_info['period'] == 'night':
            reminder_time = datetime.combine(today, datetime.strptime('20:00', '%H:%M').time())
        else:
            # Default to a standard reminder time if period not specified
            reminder_time = datetime.combine(today, datetime.strptime('09:00', '%H:%M').time())
        
        # If the timing is related to a meal, adjust the reminder time
        if timing_info['event'] == 'breakfast':
            reminder_time = datetime.combine(today, datetime.strptime('07:30', '%H:%M').time())
        elif timing_info['event'] == 'lunch':
            reminder_time = datetime.combine(today, datetime.strptime('12:30', '%H:%M').time())
        elif timing_info['event'] == 'dinner':
            reminder_time = datetime.combine(today, datetime.strptime('18:30', '%H:%M').time())
        
        # If the relation is "before" or "after", adjust the time accordingly
        if timing_info['relation'] == 'before' and timing_info['event']:
            reminder_time -= timedelta(minutes=30)
        elif timing_info['relation'] == 'after' and timing_info['event']:
            reminder_time += timedelta(minutes=30)
        
        # Check if it's time to send the reminder (within 15 minutes of the scheduled time)
        time_diff = abs((current_time - reminder_time).total_seconds() / 60)
        
        if time_diff <= 15:
            reminders_to_send.append({
                'medication': med,
                'reminder_time': reminder_time,
                'timing_info': timing_info
            })
    
    return reminders_to_send

def send_reminder_notification(reminder):
    """
    Send a reminder notification
    
    Args:
        reminder (dict): The reminder information
    
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    # In a real application, this would send an actual notification
    # For this demo, we'll just return True
    return True

def check_missed_medications(username):
    """
    Check for medications that were missed
    
    Args:
        username (str): The username to check for missed medications
        
    Returns:
        list: List of medications that were missed
    """
    # Get today's date
    today = datetime.now().date()
    current_time = datetime.now()
    
    # Get the user's medications
    medications = database.get_medications(username)
    
    # Filter for medications that should be active today
    active_medications = []
    for med in medications:
        start_date = datetime.strptime(med['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(med['end_date'], "%Y-%m-%d").date()
        
        if start_date <= today <= end_date:
            active_medications.append(med)
    
    # Determine which medications were missed
    missed_medications = []
    for med in active_medications:
        # Parse the timing to determine when the medication should have been taken
        timing_info = utils.parse_medication_time(med['timing'])
        
        # Check if medication has been taken today
        if med.get('taken', False):
            taken_time = datetime.strptime(med.get('taken_at', ''), "%Y-%m-%d %H:%M:%S").date()
            if taken_time == today:
                continue  # Skip if already taken today
        
        # Determine the cutoff time for considering the medication missed
        cutoff_time = None
        
        if timing_info['period'] == 'morning':
            cutoff_time = datetime.combine(today, datetime.strptime('11:00', '%H:%M').time())
        elif timing_info['period'] == 'afternoon':
            cutoff_time = datetime.combine(today, datetime.strptime('15:00', '%H:%M').time())
        elif timing_info['period'] == 'evening':
            cutoff_time = datetime.combine(today, datetime.strptime('21:00', '%H:%M').time())
        elif timing_info['period'] == 'night':
            cutoff_time = datetime.combine(today, datetime.strptime('23:59', '%H:%M').time())
        else:
            # Default cutoff time if period not specified
            cutoff_time = datetime.combine(today, datetime.strptime('22:00', '%H:%M').time())
        
        # Check if the current time is past the cutoff time
        if current_time > cutoff_time:
            missed_medications.append({
                'medication': med,
                'cutoff_time': cutoff_time,
                'timing_info': timing_info
            })
    
    return missed_medications

def notify_emergency_contacts(username, missed_medication):
    """
    Notify emergency contacts about missed medications
    
    Args:
        username (str): The username
        missed_medication (dict): Information about the missed medication
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    # Get emergency contacts
    emergency_contacts = database.get_emergency_contacts(username)
    
    if not emergency_contacts:
        return False
    
    # In a real application, this would send an actual notification to the emergency contacts
    # For this demo, we'll just return True if there are emergency contacts
    return len(emergency_contacts) > 0

import twilio_alert

def trigger_emergency_alert(username):
    emergency_contacts = database.get_emergency_contacts(username)
    if not emergency_contacts:
        return False

    alert_message = f"This is an emergency notification for {username}. A scheduled medication was missed. Please check immediately."
    twilio_alert.call_emergency_contacts(emergency_contacts, alert_message)
    return True

