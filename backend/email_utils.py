import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

EMAIL_ADDRESS = st.secrets.get("email", {}).get("address")
EMAIL_PASSWORD = st.secrets.get("email", {}).get("password")

def send_email(to_address, subject, content):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        st.warning("Email credentials not set. Email not sent.")
        return
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(content, "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        st.success(f"Email sent to {to_address}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")
