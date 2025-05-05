import streamlit as st


THREAT_OPTIONS = ["SQL Injection", "Ransomware", "Insider Threat", "DoS", "Phishing", "Malware", "Other"]

def get_threat_selection():
    """Handles threat vector selection with conditionally enabled custom input"""
    # Create the selectbox
    threat_selection = st.selectbox(
        "Threat Vector",
        options=THREAT_OPTIONS,
        index=None,
        key="threat_select"
    )
        
    # Always show the text input but disable it when not needed
    custom_threat = st.text_input(
        "Specify Threat",
        value="",
        placeholder="Enter custom threat...",
        disabled=(threat_selection != "Other"),
        key="custom_threat_input"
    )
        
    # Return logic
    if threat_selection == "Other":
        return custom_threat if custom_threat else "Other"
    return threat_selection