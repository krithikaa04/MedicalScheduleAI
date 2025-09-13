import streamlit as st # type: ignore
import auth
import medication
import database
import utils
from datetime import datetime
import twilio_alert

# Initialize session state variables if they don't exist
def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "page" not in st.session_state:
        st.session_state.page = "login"

# Sidebar navigation for logged-in users
def render_sidebar():
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}")
        st.header("Navigation")
        if st.button("📋 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
        if st.button("💊 Add Medication", use_container_width=True):
            st.session_state.page = "add_medication"
        if st.button("🗓️ Medication Schedule", use_container_width=True):
            st.session_state.page = "medication_schedule"
        if st.button("👤 Profile", use_container_width=True):
            st.session_state.page = "profile"
        if st.button("❓ Help", use_container_width=True):
            st.session_state.page = "help"
        if st.button("🚪 Logout", use_container_width=True):
            auth.logout()
            st.rerun()

# Main content area based on selected page
def render_main_content():
    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "add_medication":
        medication.add_medication_page()
    elif st.session_state.page == "medication_schedule":
        medication.view_medication_schedule()
    elif st.session_state.page == "profile":
        show_profile()
    elif st.session_state.page == "help":
        show_help()

# Display medications for a specific time of day
def display_medications_by_time(meds, time_label, icon):
    if meds:
        with st.expander(f"{icon} {time_label} Medications", expanded=True):
            for med in meds:
                med_status = "✅ Taken" if med.get("taken", False) else "⏳ Pending"
                st.info(f"**{med['medicine_name']}** - {med['dosage']} - {med_status}")
                if not med.get("taken", False):
                    if st.button(f"Mark as taken: {med['medicine_name']}", key=f"take_{med['id']}"):
                        medication.mark_medication_taken(med['id'])
                        st.rerun()

# Dashboard page
def show_dashboard():
    st.header("Your Medication Dashboard")
    today = datetime.now().strftime("%A, %B %d, %Y")
    st.subheader(f"Today: {today}")
    todays_meds = medication.get_todays_medications(st.session_state.username)
    if todays_meds:
        st.write("### Today's Medications")
        display_medications_by_time(
            [med for med in todays_meds if "morning" in med["timing"].lower()], "Morning", "🌅"
        )
        display_medications_by_time(
            [med for med in todays_meds if "afternoon" in med["timing"].lower()], "Afternoon", "☀️"
        )
        display_medications_by_time(
            [med for med in todays_meds if "evening" in med["timing"].lower()], "Evening", "🌇"
        )
        display_medications_by_time(
            [med for med in todays_meds if "night" in med["timing"].lower()], "Night", "🌙"
        )
    else:
        st.info("No medications scheduled for today.")
    if st.button("➕ Add New Medication", use_container_width=True):
        st.session_state.page = "add_medication"
        st.rerun()
    st.subheader("Emergency Actions")
    if st.button("🚨 Trigger Emergency Call to Contacts", use_container_width=True):
        contacts = database.get_emergency_contacts(st.session_state.username)
        if contacts:
            twilio_alert.call_emergency_contacts(
                contacts,
                message=f"This is an emergency notification for {st.session_state.username}. Please check on them immediately."
            )
            st.success("Emergency calls initiated.")
        else:
            st.error("No emergency contacts found.")

def show_profile():
    st.header("Your Profile")
    
    # Get user profile information
    user_profile = database.get_user_profile(st.session_state.username)
    emergency_contacts = database.get_emergency_contacts(st.session_state.username)
    
    # Display user information
    if user_profile:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Personal Information")
            st.write(f"**Name:** {user_profile['name']}")
            st.write(f"**Age:** {user_profile['age']}")
            st.write(f"**Phone:** {user_profile['phone']}")
            st.write(f"**Email:** {user_profile['email']}")
        
        with col2:
            st.subheader("Medical Information")
            st.write(f"**Blood Type:** {user_profile.get('blood_type', 'Not specified')}")
            st.write(f"**Allergies:** {user_profile.get('allergies', 'None')}")
    
    # Emergency contacts
    st.subheader("Emergency Contacts")
    if emergency_contacts:
        for i, contact in enumerate(emergency_contacts, 1):
            with st.expander(f"Contact {i}: {contact['name']}"):
                st.write(f"**Relationship:** {contact['relationship']}")
                st.write(f"**Phone:** {contact['phone']}")
                st.write(f"**Email:** {contact['email']}")
    else:
        st.warning("No emergency contacts found. Please add at least one emergency contact.")
    
    # Edit profile section
    with st.expander("Edit Profile"):
        # Personal information form
        name = st.text_input("Full Name", value=user_profile.get('name', ''))
        age = st.number_input("Age", min_value=60, max_value=120, value=user_profile.get('age', 65))
        phone = st.text_input("Phone Number", value=user_profile.get('phone', ''))
        email = st.text_input("Email", value=user_profile.get('email', ''))
        
        # Medical information
        blood_type = st.selectbox(
            "Blood Type", 
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
            index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"].index(user_profile.get('blood_type', 'Unknown'))
        )
        allergies = st.text_area("Allergies", value=user_profile.get('allergies', ''))
        
        if st.button("Update Profile"):
            # Update profile in database
            success = database.update_user_profile(
                st.session_state.username,
                name, age, phone, email, blood_type, allergies
            )
            if success:
                st.success("Profile updated successfully!")
                st.rerun()
            else:
                st.error("Error updating profile. Please try again.")
    
    # Emergency contact form
    with st.expander("Add Emergency Contact"):
        contact_name = st.text_input("Contact Name")
        relationship = st.text_input("Relationship")
        contact_phone = st.text_input("Contact Phone")
        contact_email = st.text_input("Contact Email")
        
        if st.button("Add Contact"):
            success = database.add_emergency_contact(
                st.session_state.username,
                contact_name, relationship, contact_phone, contact_email
            )
            if success:
                st.success("Emergency contact added successfully!")
                st.rerun()
            else:
                st.error("Error adding emergency contact. Please try again.")

def show_help():
    st.header("Help & Information")
    
    st.subheader("About This Application")
    st.write("""
    This Medical Schedule Management System is designed to help elderly users manage their medications effectively 
    through simple voice interactions and text-based inputs. The system helps organize medication schedules and 
    provides timely reminders.
    """)
    
    with st.expander("Using Voice Input"):
        st.write("""
        The voice input feature allows you to speak your medication instructions naturally. The system will automatically 
        convert your speech to text and extract important medication details.
        
        **How to use it:**
        1. Click on the 'Add Medication' button in the sidebar
        2. Choose 'Voice Input' 
        3. Click 'Start Recording' and speak clearly about your medication
        4. Verify the extracted information and make any necessary corrections
        5. Click 'Save' to add the medication to your schedule
        
        **Example voice input:**
        *"I need to take Lisinopril 10mg once daily in the morning for my blood pressure."*
        """)
    
    with st.expander("Using Text Input"):
        st.write("""
        If you prefer typing your medication details, you can use the text input feature.
        
        **How to use it:**
        1. Click on the 'Add Medication' button in the sidebar
        2. Choose 'Text Input' 
        3. Type your medication instructions in the text box
        4. Verify the extracted information and make any necessary corrections
        5. Click 'Save' to add the medication to your schedule
        """)
    
    with st.expander("Viewing Your Medication Schedule"):
        st.write("""
        The medication schedule page displays all your medications in a calendar format, 
        making it easy to see what medications you need to take each day.
        
        **How to use it:**
        1. Click on 'Medication Schedule' in the sidebar
        2. View your medications organized by day and time
        3. You can mark medications as taken directly from this view
        """)
    
    with st.expander("Managing Your Profile"):
        st.write("""
        The Profile page allows you to update your personal information and manage your emergency contacts.
        It's important to keep this information up-to-date, especially the emergency contacts.
        
        **Emergency Contacts:** These contacts will be notified if you don't respond to medication reminders, 
        creating an important safety net while maintaining your independence.
        """)
    
    with st.expander("Need More Help?"):
        st.write("""
        If you need additional assistance with using this application, please:
        
        - Ask a family member or caregiver for help
        - Refer back to this help page for guidance
        - Make sure your emergency contacts are up-to-date
        """)

# Main function
def main():
    st.set_page_config(
        page_title="Elderly Care Medication Manager",
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    initialize_session_state()
    database.initialize_database()
    st.title("Medical Schedule Management System")
    st.subheader("Your voice-enabled medication assistant")
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            auth.login_page()
        with tab2:
            auth.register_page()
    else:
        render_sidebar()
        render_main_content()

if __name__ == "__main__":
    main()
