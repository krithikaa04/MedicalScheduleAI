import streamlit as st # type: ignore
import speech_recognition_helper as sr_helper
import nlp_processor
import database
import datetime
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
from datetime import datetime, timedelta
import calendar
from speech_to_text.test_system import test_system, test_audio_live
import random

def add_medication_page():
    """
    Page for adding new medications with both voice and text input options
    """
    st.header("Add New Medication")
    tab1, tab2 = st.tabs(["Text Input", "Voice Input"])
    with tab1:
        text_input_section()
    with tab2:
        voice_input_section()

def voice_input_section():
    """
    Section for adding medications through voice input
    """
    st.subheader("Voice Input")
    display_voice_input_instructions()
    audio_mode = st.radio("Choose an audio mode:", ("Real-Time Audio", "Simulated Audio"))
    handle_audio_input(audio_mode)

def display_voice_input_instructions():
    """
    Display instructions for voice input
    """
    st.write("Please speak clearly about your medication. Include details such as:")
    st.write("- Name of the medicine")
    st.write("- Dosage amount")
    st.write("- How often to take it")
    st.write("- When to take it")
    st.write("- How long to continue taking it")
    st.write("- Any special instructions")
    with st.expander("Example of what to say"):
        st.write("*I need to take Lisinopril 10mg once daily in the morning for my blood pressure.*")

def handle_audio_input(audio_mode):
    """
    Handle audio input based on the selected mode
    """
    if audio_mode == "Real-Time Audio":
        handle_real_time_audio()
    elif audio_mode == "Simulated Audio":
        handle_simulated_audio()

def handle_real_time_audio():
    """
    Handle real-time audio input
    """
    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button("🎤 Start Recording", key="start_voice", use_container_width=True)
    with col2:
        stop_button = st.button("⏹️ Stop Recording", key="stop_voice", use_container_width=True)

    if "transcribed_text" not in st.session_state:
        st.session_state.transcribed_text = ""

    if start_button:
        process_real_time_audio()

    if st.session_state.transcribed_text:
        display_transcribed_text(st.session_state.transcribed_text)

def process_real_time_audio():
    """
    Process real-time audio input
    """
    with st.spinner("Recording and processing your voice input..."):
        try:
            text = test_audio_live(duration=5, sample_rate=16000)
            text = text.lower()
            if text:
                st.session_state.transcribed_text = text
                st.success("Voice recorded and transcribed successfully!")
            else:
                st.error("Could not understand audio. Please try again.")
        except Exception as e:
            st.error(f"An error occurred while processing audio: {e}")

def handle_simulated_audio():
    """
    Handle simulated audio input
    """
    st.session_state.transcribed_text = ""
    with st.spinner("Processing simulated audio..."):
        random_number = random.randint(2, 207)
        audio_path = f"speech_to_text/preprocessed-data/audio_{random_number}.npy"
        print("audio path:", audio_path)
        text = test_system(audio_path)
        text = text.lower()
        if text:
            st.session_state.transcribed_text = text
            st.success("Simulated audio processed successfully!")
        else:
            st.error("Could not process simulated audio. Please try again.")

    if st.session_state.transcribed_text:
        display_transcribed_text(st.session_state.transcribed_text)

def display_transcribed_text(transcribed_text):
    """
    Display the transcribed text and process it
    """
    st.subheader("Transcribed Text")
    st.write(transcribed_text)
    with st.spinner("Analyzing medication details..."):
        medication_info = nlp_processor.extract_medication_info(transcribed_text)
        display_and_confirm_medication(medication_info, "voice")

def text_input_section():
    """
    Section for adding medications through text input
    """
    st.subheader("Text Input")
    st.write("Please enter details about your medication:")
    with st.expander("Example of what to write"):
        st.write("*I need to take Lisinopril 10mg once daily in the morning for my blood pressure.*")
    medication_text = st.text_area("Medication Instructions", height=150, placeholder="Enter medication details here...")
    if st.button("Process Text Input", key="process_text", use_container_width=True):
        process_text_input(medication_text)

def process_text_input(medication_text):
    """
    Process text input for medication details
    """
    if not medication_text:
        st.error("Please enter some text about your medication.")
        return
    with st.spinner("Analyzing medication details..."):
        medication_info = nlp_processor.extract_medication_info(medication_text)
        print(medication_info)
        display_and_confirm_medication(medication_info, "text")

def display_and_confirm_medication(medication_info, input_type):
    """
    Display extracted medication information and ask for confirmation
    
    Args:
        medication_info (dict): The extracted medication details
        input_type (str): Either "voice" or "text" to identify the source
    """
    st.subheader("Extracted Medication Information")
    
    # Display the extracted information with editable fields
    medicine_name = st.text_input("Medicine Name", value=medication_info.get("medicine_name", ""), key=f"medicine_name_{input_type}")
    dosage = st.text_input("Dosage", value=medication_info.get("dosage", ""), key=f"dosage_{input_type}")
    frequency = st.text_input("Frequency", value=medication_info.get("frequency", ""), key=f"frequency_{input_type}")
    timing = st.text_input("Timing", value=medication_info.get("timing", ""), key=f"timing_{input_type}")
    duration = st.text_input("Duration", value=medication_info.get("duration", ""), key=f"duration_{input_type}")
    instructions = st.text_area("Special Instructions", value=medication_info.get("instructions", ""), key=f"instructions_{input_type}")
    
    # Date inputs for start and end dates
    start_date = st.date_input("Start Date", value=datetime.now(), key=f"start_date_{input_type}")
    
    # Calculate default end date
    default_days = 30
    duration_text = medication_info.get("duration", "").lower()
    if "day" in duration_text:
        try:
            default_days = int(''.join(filter(str.isdigit, duration_text)))
        except:
            pass
    elif "week" in duration_text:
        try:
            default_days = int(''.join(filter(str.isdigit, duration_text))) * 7
        except:
            pass
    elif "month" in duration_text:
        try:
            default_days = int(''.join(filter(str.isdigit, duration_text))) * 30
        except:
            pass
    
    end_date = st.date_input("End Date", value=datetime.now() + timedelta(days=default_days), key=f"end_date_{input_type}")
    print("input type:", input_type)
    print("session state:", st.session_state)
    
    
    # Confirm and save
    col1, col2 = st.columns(2)
    with col1:
        save_clicked = st.button("Save Medication", key=f"save_{input_type}", use_container_width=True)
        st.session_state[f"save_clicked_{input_type}"] = True
        print("save clicked:", save_clicked)
        
        if st.session_state[f"save_clicked_{input_type}"]:
            
            if not medicine_name.strip():
                st.error("Medicine name is required.")
                st.session_state[f"save_clicked_{input_type}"] = False
                return
            
            # Format the medication data
            print("medicine name:", medicine_name.strip())
            medication_data = {
                "medicine_name": medicine_name.strip(),
                "dosage": dosage.strip(),
                "frequency": frequency.strip(),
                "timing": timing.strip(),
                "duration": duration.strip(),
                "instructions": instructions.strip(),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            }
            
            # Save to database
            success = database.add_medication(st.session_state.username, medication_data)
            if success:
                st.success("Medication added successfully!")
                if input_type == "voice":
                    st.session_state.transcribed_text = ""
                st.session_state[f"save_clicked_{input_type}"] = False
                st.session_state.page = "medication_schedule"
                st.rerun()
            else:
                st.error("Failed to save medication. Please try again.")
                st.session_state[f"save_clicked_{input_type}"] = False
    
    with col2:
        if st.button("Cancel", key=f"cancel_{input_type}", use_container_width=True):
            if input_type == "voice":
                st.session_state.transcribed_text = ""
            st.rerun()

def view_medication_schedule():
    """
    Display the user's medication schedule in calendar format
    """
    st.header("Your Medication Schedule")
    
    # Get all medications for the user
    medications = database.get_medications(st.session_state.username)
    
    if not medications:
        st.info("You don't have any medications scheduled. Please add some medications.")
        return
    
    # Calendar view
    st.subheader("Calendar View")
    
    # Get current date and calculate start and end of week
    today = datetime.now().date()
    
    # Create date selection
    view_options = ["Day View", "Week View", "Month View"]
    selected_view = st.radio("Select View", view_options, horizontal=True)
    
    selected_date = st.date_input("Select Date", value=today)
    
    if selected_view == "Day View":
        display_day_view(selected_date, medications)
    elif selected_view == "Week View":
        display_week_view(selected_date, medications)
    else:  # Month View
        display_month_view(selected_date, medications)
    
    # List view of all medications
    st.subheader("All Medications")
    
    for med in medications:
        with st.expander(f"{med['medicine_name']} - {med['dosage']}"):
            st.write(f"**Frequency:** {med['frequency']}")
            st.write(f"**Timing:** {med['timing']}")
            st.write(f"**Duration:** {med['duration']}")
            st.write(f"**Start Date:** {med['start_date']}")
            st.write(f"**End Date:** {med['end_date']}")
            if med['instructions']:
                st.write(f"**Special Instructions:** {med['instructions']}")
            
            # Edit and delete buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit", key=f"edit_{med['id']}", use_container_width=True):
                    st.session_state.edit_medication_id = med['id']
                    st.session_state.page = "edit_medication"
                    st.rerun()
            
            with col2:
                if st.button("Delete", key=f"delete_{med['id']}", use_container_width=True):
                    if database.delete_medication(med['id']): 
                        st.success("Medication deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Error deleting medication.")

def display_day_view(selected_date, medications):
    """
    Display medications for a specific day
    
    Args:
        selected_date (date): The date to display
        medications (list): List of medication dictionaries
    """
    st.write(f"### Medications for {selected_date.strftime('%A, %B %d, %Y')}")
    
    # Filter medications for the selected date
    day_meds = []
    for med in medications:
        start_date = datetime.strptime(med['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(med['end_date'], "%Y-%m-%d").date()
        
        if start_date <= selected_date <= end_date:
            day_meds.append(med)
    
    if not day_meds:
        st.info("No medications scheduled for this day.")
        return
    
    # Organize by time of day
    morning_meds = [med for med in day_meds if "morning" in med["timing"].lower()]
    afternoon_meds = [med for med in day_meds if "afternoon" in med["timing"].lower()]
    evening_meds = [med for med in day_meds if "evening" in med["timing"].lower()]
    night_meds = [med for med in day_meds if "night" in med["timing"].lower()]
    other_meds = [med for med in day_meds if not any(time in med["timing"].lower() for time in ["morning", "afternoon", "evening", "night"])]
    
    # Display medications by time
    if morning_meds:
        st.write("#### 🌅 Morning")
        for med in morning_meds:
            st.info(f"**{med['medicine_name']}** - {med['dosage']} - {med['instructions']}")
    
    if afternoon_meds:
        st.write("#### ☀️ Afternoon")
        for med in afternoon_meds:
            st.info(f"**{med['medicine_name']}** - {med['dosage']} - {med['instructions']}")
    
    if evening_meds:
        st.write("#### 🌇 Evening")
        for med in evening_meds:
            st.info(f"**{med['medicine_name']}** - {med['dosage']} - {med['instructions']}")
    
    if night_meds:
        st.write("#### 🌙 Night")
        for med in night_meds:
            st.info(f"**{med['medicine_name']}** - {med['dosage']} - {med['instructions']}")
    
    if other_meds:
        st.write("#### ⏰ Other Times")
        for med in other_meds:
            st.info(f"**{med['medicine_name']}** - {med['dosage']} - {med['timing']} - {med['instructions']}")

def display_week_view(selected_date, medications):
    """
    Display medications for a week
    
    Args:
        selected_date (date): A date in the week to display
        medications (list): List of medication dictionaries
    """
    # Calculate the start of the week (Monday)
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    
    # Get dates for the entire week
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    st.write(f"### Week of {start_of_week.strftime('%B %d')} - {(start_of_week + timedelta(days=6)).strftime('%B %d, %Y')}")
    
    # Create a heatmap-style calendar
    data = []
    
    # For each day in the week
    for date in week_dates:
        day_meds = []
        for med in medications:
            start_date = datetime.strptime(med['start_date'], "%Y-%m-%d").date()
            end_date = datetime.strptime(med['end_date'], "%Y-%m-%d").date()
            
            if start_date <= date <= end_date:
                day_meds.append(med)
        
        # Count medications by time of day
        morning_count = sum(1 for med in day_meds if "morning" in med["timing"].lower())
        afternoon_count = sum(1 for med in day_meds if "afternoon" in med["timing"].lower())
        evening_count = sum(1 for med in day_meds if "evening" in med["timing"].lower())
        night_count = sum(1 for med in day_meds if "night" in med["timing"].lower())
        
        # Add to data
        day_name = date.strftime("%a %m/%d")
        if morning_count > 0:
            data.append({"Day": day_name, "Time": "Morning", "Medications": morning_count})
        else:
            data.append({"Day": day_name, "Time": "Morning", "Medications": 0})
            
        if afternoon_count > 0:
            data.append({"Day": day_name, "Time": "Afternoon", "Medications": afternoon_count})
        else:
            data.append({"Day": day_name, "Time": "Afternoon", "Medications": 0})
            
        if evening_count > 0:
            data.append({"Day": day_name, "Time": "Evening", "Medications": evening_count})
        else:
            data.append({"Day": day_name, "Time": "Evening", "Medications": 0})
            
        if night_count > 0:
            data.append({"Day": day_name, "Time": "Night", "Medications": night_count})
        else:
            data.append({"Day": day_name, "Time": "Night", "Medications": 0})
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create heatmap
    fig = px.density_heatmap(
        df, 
        x="Day", 
        y="Time",
        z="Medications",
        color_continuous_scale="Blues",
        title="Weekly Medication Schedule"
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Allow viewing details for a specific day
    st.write("**Select a day to view details:**")
    
    # Buttons for each day
    cols = st.columns(7)
    for i, date in enumerate(week_dates):
        with cols[i]:
            day_name = date.strftime("%a")
            if st.button(day_name, key=f"day_{i}", use_container_width=True):
                display_day_view(date, medications)

def display_month_view(selected_date, medications):
    """
    Display medications for a month
    
    Args:
        selected_date (date): A date in the month to display
        medications (list): List of medication dictionaries
    """
    # Get the first day of the month
    first_day = selected_date.replace(day=1)
    
    # Get the last day of the month
    # Get the last day of the month
    if first_day.month == 12:
        last_day = first_day.replace(year=first_day.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = first_day.replace(month=first_day.month + 1, day=1) - timedelta(days=1)
    
    st.write(f"### {first_day.strftime('%B %Y')}")
    
    # Create calendar display
    cal = calendar.monthcalendar(first_day.year, first_day.month)
    
    # Display weekday headers
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day in enumerate(weekdays):
        with cols[i]:
            st.write(f"**{day}**")
    
    # Display calendar with medication counts
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")  # Empty cell
                else:
                    date = first_day.replace(day=day)
                    
                    # Count medications for this day
                    med_count = 0
                    for med in medications:
                        start_date = datetime.strptime(med['start_date'], "%Y-%m-%d").date()
                        end_date = datetime.strptime(med['end_date'], "%Y-%m-%d").date()
                        
                        if start_date <= date <= end_date:
                            med_count += 1
                    
                    # Style based on date and medication count
                    if date == datetime.now().date():
                        # Today's date
                        if med_count > 0:
                            st.markdown(f"<div style='text-align:center;background-color:#2E86C1;color:white;border-radius:5px;padding:5px'><b>{day}</b><br/>{med_count} meds</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align:center;background-color:#2E86C1;color:white;border-radius:5px;padding:5px'><b>{day}</b><br/>-</div>", unsafe_allow_html=True)
                    else:
                        # Regular date
                        if med_count > 0:
                            st.markdown(f"<div style='text-align:center;border:1px solid #ddd;border-radius:5px;padding:5px'>{day}<br/>{med_count} meds</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align:center;border:1px solid #ddd;border-radius:5px;padding:5px'>{day}<br/>-</div>", unsafe_allow_html=True)
                    
                    # Button to view day details
                    if st.button(f"View", key=f"view_day_{day}", use_container_width=True):
                        display_day_view(date, medications)

def get_todays_medications(username):
    """
    Get all medications scheduled for today
    
    Args:
        username (str): The username
    
    Returns:
        list: List of medication dictionaries for today
    """
    today = datetime.now().date()
    
    # Get all medications
    all_meds = database.get_medications(username)
    
    # Filter for today
    todays_meds = []
    for med in all_meds:
        start_date = datetime.strptime(med['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(med['end_date'], "%Y-%m-%d").date()
        
        if start_date <= today <= end_date:
            todays_meds.append(med)
    
    return todays_meds

def mark_medication_taken(medication_id):
    """
    Mark a medication as taken
    
    Args:
        medication_id (int): The medication ID
    
    Returns:
        bool: Success status
    """
    return database.mark_medication_taken(medication_id)
