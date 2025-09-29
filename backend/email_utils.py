import smtplib
from email.message import EmailMessage
import streamlit as st

def send_email(to_email, subject, content):
    try:
        email_address = st.secrets["email"]["address"]
        email_password = st.secrets["email"]["password"]
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["smtp_port"]

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = email_address
        msg["To"] = to_email
        msg.set_content(content)

        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(email_address, email_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False
