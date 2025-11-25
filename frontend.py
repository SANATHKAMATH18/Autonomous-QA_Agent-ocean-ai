import streamlit as st
import requests
import pandas as pd
import json

# --- CONFIGURATION ---
# Ensure this matches your running FastAPI port
API_BASE_URL = "http://35.200.159.55:8000/"
# API_BASE_URL = "http://localhost:8000/"

st.set_page_config(
    page_title="Ocean AI QA Agent",
    page_icon="🌊",
    layout="wide"
)

# --- SESSION STATE MANAGEMENT ---
if "kb_id" not in st.session_state:
    st.session_state.kb_id = None
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []
if "selenium_script" not in st.session_state:
    st.session_state.selenium_script = ""

# --- SIDEBAR: CONFIG & UPLOADS ---
with st.sidebar:
    st.header("📂 Knowledge Base")
    
    uploaded_files = st.file_uploader(
        "Upload Project Docs (PDF, TXT, MD, JSON)", 
        accept_multiple_files=True
    )
    
    if st.button("Upload & Build KB", type="primary"):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                try:
                    # Prepare files for multipart/form-data upload
                    files_payload = [
                        ("files", (file.name, file.getvalue(), file.type)) 
                        for file in uploaded_files
                    ]
                    
                    response = requests.post(f"{API_BASE_URL}/upload-docs", files=files_payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.kb_id = data["kb_id"]
                        st.success(f"KB Built! ID: {data['kb_id']}")
                        st.info(data["message"])
                    else:
                        st.error(f"Error: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to Backend. Is FastAPI running?")
        else:
            st.warning("Please select files first.")

    if st.session_state.kb_id:
        st.success(f"Active KB: `{st.session_state.kb_id}`")
        if st.button("Clear Session"):
            st.session_state.kb_id = None
            st.session_state.test_cases = []
            st.session_state.selenium_script = ""
            st.rerun()

# --- MAIN PAGE ---
st.title("🌊 Ocean AI: QA Automation Agent")
st.markdown("---")

# STEP 1: GENERATE TEST CASES
st.header("1️⃣ Generate Test Cases")

if not st.session_state.kb_id:
    st.info("👈 Please upload documents in the sidebar to begin.")
else:
    query = st.text_input(
        "Describe the feature or requirement:", 
        placeholder="e.g., Generate positive and negative test cases for the login page discount code field."
    )
    
    if st.button("Generate Test Cases"):
        if query:
            with st.spinner("Analyzing docs and generating cases..."):
                try:
                    payload = {"kb_id": st.session_state.kb_id, "query": query}
                    response = requests.post(f"{API_BASE_URL}/generate-test-cases", json=payload)
                    
                    if response.status_code == 200:
                        st.session_state.test_cases = response.json()["test_cases"]
                        st.rerun()
                    else:
                        st.error(f"Failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a query.")

# STEP 2: DISPLAY & SELECT
if st.session_state.test_cases:
    st.subheader("📋 Generated Test Cases")
    
    # Display as DataFrame for easy reading
    df = pd.DataFrame(st.session_state.test_cases)
    st.dataframe(df, use_container_width=True)
    
    st.header("2️⃣ Generate Selenium Script")
    
    # Dropdown to select a specific test case
    tc_options = {f"{tc.get('Test_ID', 'N/A')}: {tc.get('Test_Scenario', 'N/A')}": tc for tc in st.session_state.test_cases}
    selected_option = st.selectbox("Select a Test Case to Automate:", list(tc_options.keys()))
    selected_test_case = tc_options[selected_option]

    # Display selected details
    with st.expander("View Selected Test Case Details"):
        st.json(selected_test_case)

    # Input HTML
    html_content = st.text_area(
        "Paste relevant HTML snippet (required for selectors):",
        height=200,
        placeholder="<div id='login-form'><input id='username' ...></div>"
    )

    if st.button("Generate Python Selenium Code"):
        if html_content:
            with st.spinner("Writing automation script..."):
                try:
                    payload = {
                        "test_case": selected_test_case,
                        "html_content": html_content
                    }
                    response = requests.post(f"{API_BASE_URL}/generate-selenium", json=payload)
                    
                    if response.status_code == 200:
                        st.session_state.selenium_script = response.json()["script"]
                    else:
                        st.error(f"Failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please paste the HTML content so the AI knows which selectors to use.")

# STEP 3: OUTPUT
if st.session_state.selenium_script:
    st.markdown("---")
    st.header("3️⃣ Final Script")
    st.code(st.session_state.selenium_script, language="python")
    
    st.download_button(
        label="Download Script",
        data=st.session_state.selenium_script,
        file_name="selenium_test.py",
        mime="text/x-python"
    )