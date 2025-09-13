import streamlit as st
import database
import hashlib

def login_page():
    """
    Display the login page interface
    """
    st.header("Login")
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        login_button = st.button("Login", use_container_width=True, key="login_button")
    
    # Process login when button is clicked
    if login_button:
        if not username or not password:
            st.error("Please enter both username and password.")
            return
        
        # Hash the password before checking
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check credentials
        if database.verify_credentials(username, hashed_password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "dashboard"
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password. Please try again.")

def register_page():
    """
    Display the registration page interface
    """
    st.header("Register New User")
    
    # Personal Information
    st.subheader("Personal Information")
    name = st.text_input("Full Name", key="reg_name")
    age = st.number_input("Age", min_value=60, max_value=120, value=65, key="reg_age")
    phone = st.text_input("Phone Number", key="reg_phone")
    email = st.text_input("Email", key="reg_email")
    
    # Medical Information
    st.subheader("Medical Information")
    blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"], key="reg_blood_type")
    allergies = st.text_area("Allergies (if any)", key="reg_allergies")
    
    # Account Information
    st.subheader("Account Information")
    username = st.text_input("Choose a Username", key="reg_username")
    password = st.text_input("Choose a Password", type="password", key="reg_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
    
    # Emergency Contact
    st.subheader("Emergency Contact (Required)")
    ec_name = st.text_input("Emergency Contact Name", key="reg_ec_name")
    ec_relation = st.text_input("Relationship", key="reg_ec_relation")
    ec_phone = st.text_input("Emergency Contact Phone", key="reg_ec_phone")
    ec_email = st.text_input("Emergency Contact Email", key="reg_ec_email")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        register_button = st.button("Register", use_container_width=True, key="register_button")
    
    # Process registration when button is clicked
    if register_button:
        # Validate inputs
        if not all([name, age, phone, email, username, password, confirm_password, ec_name, ec_relation, ec_phone]):
            st.error("Please fill in all required fields.")
            return
        
        if password != confirm_password:
            st.error("Passwords do not match.")
            return
        
        # Check if username already exists
        if database.user_exists(username):
            st.error("Username already exists. Please choose a different username.")
            return
        
        # Hash the password for secure storage
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Create the user account
        success = database.create_user(
            username, hashed_password, name, age, phone, email,
            blood_type, allergies
        )
        
        if success:
            # Add emergency contact
            database.add_emergency_contact(
                username, ec_name, ec_relation, ec_phone, ec_email
            )
            
            st.success("Registration successful! You can now log in.")
            # Automatically switch to login view
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Error creating account. Please try again.")

def logout():
    """
    Log out the current user
    """
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.page = "login"
