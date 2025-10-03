import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

# Retrieve credentials securely from Streamlit secrets
EMAIL_ADDRESS = st.secrets.get("email", {}).get("address")
EMAIL_PASSWORD = st.secrets.get("email", {}).get("password")

def send_email(to_address, subject, content):
    """
    Sends an email using the configured SMTP server and credentials.
    """
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        st.warning("⚠️ Email credentials not set in secrets.toml. Email not sent.")
        return
    
    # 1. Build the message
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(content, "plain"))
    
    # 2. Send the message
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        st.success(f"Confirmation email successfully sent to {to_address}.") 
    except Exception as e:
        st.error(f"Failed to send confirmation email. Please check your internet connection or App Password/security settings: {e}")
