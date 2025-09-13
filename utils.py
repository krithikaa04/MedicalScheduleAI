import streamlit as st
import time
import re
from datetime import datetime

def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email address
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_phone(phone):
    """
    Validate phone number format
    
    Args:
        phone (str): Phone number
        
    Returns:
        bool: True if phone number is valid, False otherwise
    """
    numeric_phone = re.sub(r'\D', '', phone)
    return 8 <= len(numeric_phone) <= 15

def format_time_ago(timestamp_str):
    """
    Format a timestamp as a human-readable "time ago" string
    
    Args:
        timestamp_str (str): Timestamp string in format "YYYY-MM-DD HH:MM:SS"
        
    Returns:
        str: Human-readable time difference
    """
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    diff = datetime.now() - timestamp
    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minute{'s' if seconds // 60 != 1 else ''} ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hour{'s' if seconds // 3600 != 1 else ''} ago"
    elif seconds < 604800:
        return f"{int(seconds / 86400)} day{'s' if seconds // 86400 != 1 else ''} ago"
    elif seconds < 2592000:
        return f"{int(seconds / 604800)} week{'s' if seconds // 604800 != 1 else ''} ago"
    elif seconds < 31536000:
        return f"{int(seconds / 2592000)} month{'s' if seconds // 2592000 != 1 else ''} ago"
    else:
        return f"{int(seconds / 31536000)} year{'s' if seconds // 31536000 != 1 else ''} ago"

def get_greeting():
    """
    Get a time-appropriate greeting
    
    Returns:
        str: Greeting based on time of day
    """
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 18:
        return "Good afternoon"
    return "Good evening"

def parse_medication_time(timing_str):
    """
    Parse medication timing into a more structured format
    
    Args:
        timing_str (str): Timing string (e.g., "in the morning", "after breakfast")
        
    Returns:
        dict: Structured timing information
    """
    timing_str = timing_str.lower()
    result = {"period": None, "relation": None, "event": None}

    if "morning" in timing_str:
        result["period"] = "morning"
    elif "afternoon" in timing_str:
        result["period"] = "afternoon"
    elif "evening" in timing_str:
        result["period"] = "evening"
    elif "night" in timing_str or "bedtime" in timing_str:
        result["period"] = "night"

    if "before" in timing_str:
        result["relation"] = "before"
    elif "after" in timing_str:
        result["relation"] = "after"
    elif "with" in timing_str:
        result["relation"] = "with"

    if "meal" in timing_str:
        result["event"] = "meals"
    elif "breakfast" in timing_str:
        result["event"] = "breakfast"
    elif "lunch" in timing_str:
        result["event"] = "lunch"
    elif "dinner" in timing_str:
        result["event"] = "dinner"
    elif "food" in timing_str:
        result["event"] = "food"
    elif "bedtime" in timing_str:
        result["event"] = "bedtime"

    return result
