# Add these imports at the top with your other imports
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import project_config


def generate_verification_code():
    """Generate a random 6-digit verification code"""
    return "".join(random.choices(string.digits, k=6))


def send_verification_email(email, verification_code, first_name):
    """Send verification email"""
    try:
        # Create message container
        msg = MIMEMultipart()
        msg["From"] = project_config.EMAIL_FROM
        msg["To"] = email
        msg["Subject"] = "Your Verification Code for ai_platform"

        # Create a simpler plain text body without HTML formatting
        plain_body = f"""Hello {first_name},

Thank you for using with our AI Platform. Your verification code is: {verification_code}

Please enter this code to complete your account setup.
This code will expire in 10 minutes.

Best regards,
AI Platform Team
"""
        # Add plain text body with utf-8 encoding
        msg.attach(MIMEText(plain_body, "plain", "utf-8"))

        # Setup SMTP server
        print(
            f"Connecting to SMTP server: {project_config.EMAIL_HOST}:{project_config.EMAIL_PORT}"
        )
        server = smtplib.SMTP(project_config.EMAIL_HOST, project_config.EMAIL_PORT)
        server.starttls()  # Secure the connection

        # Login with credentials
        username = project_config.EMAIL_USERNAME
        password = project_config.EMAIL_PASSWORD
        server.login(username, password)

        # Send email - FIXED THIS LINE
        server.send_message(msg)  # Only pass the message object

        print("Email sent successfully")
        server.quit()
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        import traceback

        traceback.print_exc()
        return False


def send_password_reset_email(email, verification_code):
    """
    Send a password reset email with verification code
    """
    """Send verification email"""
    try:
        # Create message container
        msg = MIMEMultipart()
        msg["From"] = project_config.EMAIL_FROM
        msg["To"] = email
        msg["Subject"] = "Password Reset Verification Code"

        # Create a simpler plain text body without HTML formatting
        plain_body = f"""
                You requested a password reset for your account. Please use the following verification code to reset your password:
                
                    {verification_code}

                This code will expire in 10 minutes.
                If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                Thank you, AI Platform Team
            """
        # Add plain text body with utf-8 encoding
        msg.attach(MIMEText(plain_body, "plain", "utf-8"))

        # Setup SMTP server
        print(
            f"Connecting to SMTP server: {project_config.EMAIL_HOST}:{project_config.EMAIL_PORT}"
        )
        server = smtplib.SMTP(project_config.EMAIL_HOST, project_config.EMAIL_PORT)
        server.starttls()  # Secure the connection

        # Login with credentials
        username = project_config.EMAIL_USERNAME
        password = project_config.EMAIL_PASSWORD
        server.login(username, password)

        # Send email - FIXED THIS LINE
        server.send_message(msg)  # Only pass the message object

        print("Email sent successfully")
        server.quit()
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        import traceback

        traceback.print_exc()
        return False