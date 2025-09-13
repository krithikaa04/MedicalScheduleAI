import streamlit as st # type: ignore
import json
from datetime import datetime, timedelta
import uuid
import os

# File to store data (in a real app, use a proper database)
DATA_DIR = "data"
USER_FILE = os.path.join(DATA_DIR, "users.json")
MEDICATION_FILE = os.path.join(DATA_DIR, "medications.json")

def initialize_database():
    """
    Initialize database files if they don't exist
    """
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Initialize users file
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump([], f)
    
    # Initialize medications file
    if not os.path.exists(MEDICATION_FILE):
        with open(MEDICATION_FILE, 'w') as f:
            json.dump([], f)

def user_exists(username):
    """
    Check if a user exists
    
    Args:
        username (str): Username to check
        
    Returns:
        bool: True if user exists, False otherwise
    """
    try:
        with open(USER_FILE, 'r') as f:
            users = json.load(f)
            return any(user['username'] == username for user in users)
    except Exception as e:
        st.error(f"Error checking if user exists: {str(e)}")
        return False

def verify_credentials(username, password_hash):
    """
    Verify user credentials
    
    Args:
        username (str): Username
        password_hash (str): Hashed password
        
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    try:
        with open(USER_FILE, 'r') as f:
            users = json.load(f)
            for user in users:
                if user['username'] == username and user['password'] == password_hash:
                    return True
            return False
    except Exception as e:
        st.error(f"Error verifying credentials: {str(e)}")
        return False

def create_user(username, password_hash, name, age, phone, email, blood_type, allergies):
    """
    Create a new user
    
    Args:
        username (str): Username
        password_hash (str): Hashed password
        name (str): Full name
        age (int): Age
        phone (str): Phone number
        email (str): Email address
        blood_type (str): Blood type
        allergies (str): Allergies
        
    Returns:
        bool: True if user was created successfully, False otherwise
    """
    try:
        with open(USER_FILE, 'r') as f:
            users = json.load(f)
        
        # Check if username already exists
        if any(user['username'] == username for user in users):
            return False
        
        # Create new user
        new_user = {
            'username': username,
            'password': password_hash,
            'name': name,
            'age': age,
            'phone': phone,
            'email': email,
            'blood_type': blood_type,
            'allergies': allergies,
            'emergency_contacts': []
        }
        
        users.append(new_user)
        
        with open(USER_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return False

def get_user_profile(username):
    """
    Get user profile information
    
    Args:
        username (str): Username
        
    Returns:
        dict: User profile information
    """
    try:
        with open(USER_FILE, 'r') as f:
            users = json.load(f)
            for user in users:
                if user['username'] == username:
                    # Return a copy of the user data without password
                    user_copy = user.copy()
                    user_copy.pop('password', None)
                    return user_copy
            return None
    except Exception as e:
        st.error(f"Error getting user profile: {str(e)}")
        return None

def update_user_profile(username, name, age, phone, email, blood_type, allergies):
    """
    Update user profile
    
    Args:
        username (str): Username
        name (str): Full name
        age (int): Age
        phone (str): Phone number
        email (str): Email address
        blood_type (str): Blood type
        allergies (str): Allergies
        
    Returns:
        bool: True if profile was updated successfully, False otherwise
    """
    try:
        with open(USER_FILE, 'r') as f:
            users = json.load(f)
        
        for user in users:
            if user['username'] == username:
                user['name'] = name
                user['age'] = age
                user['phone'] = phone
                user['email'] = email
                user['blood_type'] = blood_type
                user['allergies'] = allergies
                
                with open(USER_FILE, 'w') as f:
                    json.dump(users, f, indent=2)
                return True
        
        return False
    except Exception as e:
        st.error(f"Error updating user profile: {str(e)}")
        return False

def add_emergency_contact(username, name, relationship, phone, email):
    """
    Add emergency contact for a user
    
    Args:
        username (str): Username
        name (str): Contact name
        relationship (str): Relationship to user
        phone (str): Contact phone
        email (str): Contact email
        
    Returns:
        bool: True if contact was added successfully, False otherwise
    """
    try:
        with open(USER_FILE, 'r') as f:
            users = json.load(f)
        
        for user in users:
            if user['username'] == username:
                if 'emergency_contacts' not in user:
                    user['emergency_contacts'] = []
                
                # Create new emergency contact
                new_contact = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'relationship': relationship,
                    'phone': phone,
                    'email': email
                }
                
                user['emergency_contacts'].append(new_contact)
                
                with open(USER_FILE, 'w') as f:
                    json.dump(users, f, indent=2)
                return True
        
        return False
    except Exception as e:
        st.error(f"Error adding emergency contact: {str(e)}")
        return False

def get_emergency_contacts(username):
    """
    Get emergency contacts for a user
    
    Args:
        username (str): Username
        
    Returns:
        list: List of emergency contacts
    """
    try:
        with open(USER_FILE, 'r') as f:
            users = json.load(f)
            for user in users:
                if user['username'] == username:
                    return user.get('emergency_contacts', [])
            return []
    except Exception as e:
        st.error(f"Error getting emergency contacts: {str(e)}")
        return []

def add_medication(username, medication_data):
    """
    Add medication for a user
    
    Args:
        username (str): Username
        medication_data (dict): Medication information
        
    Returns:
        bool: True if medication was added successfully, False otherwise
    """
    try:
        with open(MEDICATION_FILE, 'r') as f:
            medications = json.load(f)
        print("HIIII")
        # Create n  ew medication entry
        new_medication = {
            'id': str(uuid.uuid4()),
            'username': username,
            'medicine_name': medication_data['medicine_name'],
            'dosage': medication_data['dosage'],
            'frequency': medication_data['frequency'],
            'timing': medication_data['timing'],
            'duration': medication_data['duration'],
            'instructions': medication_data['instructions'],
            'start_date': medication_data['start_date'],
            'end_date': medication_data['end_date'],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        medications.append(new_medication)
        
        with open(MEDICATION_FILE, 'w') as f:
            json.dump(medications, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error adding medication: {str(e)}")
        return False

def get_medications(username):
    """
    Get all medications for a user
    
    Args:
        username (str): Username
        
    Returns:
        list: List of medications
    """
    try:
        with open(MEDICATION_FILE, 'r') as f:
            medications = json.load(f)
            return [med for med in medications if med['username'] == username]
    except Exception as e:
        st.error(f"Error getting medications: {str(e)}")
        return []

def delete_medication(medication_id):
    """
    Delete a medication
    
    Args:
        medication_id (str): Medication ID
        
    Returns:
        bool: True if medication was deleted successfully, False otherwise
    """
    try:
        with open(MEDICATION_FILE, 'r') as f:
            medications = json.load(f)
        
        # Filter out the medication to delete
        updated_medications = [med for med in medications if med['id'] != medication_id]
        
        with open(MEDICATION_FILE, 'w') as f:
            json.dump(updated_medications, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error deleting medication: {str(e)}")
        return False

def mark_medication_taken(medication_id):
    """
    Mark a medication as taken
    
    Args:
        medication_id (str): Medication ID
        
    Returns:
        bool: True if medication was marked as taken successfully, False otherwise
    """
    try:
        with open(MEDICATION_FILE, 'r') as f:
            medications = json.load(f)
        
        for med in medications:
            if med['id'] == medication_id:
                # Add or update taken status
                med['taken'] = True
                med['taken_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(MEDICATION_FILE, 'w') as f:
                    json.dump(medications, f, indent=2)
                return True
        
        return False
    except Exception as e:
        st.error(f"Error marking medication as taken: {str(e)}")
        return False
