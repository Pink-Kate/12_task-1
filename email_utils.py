import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import secrets
import string

def generate_verification_token(length: int = 32) -> str:
    """Generate a random verification token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def send_verification_email(email: str, token: str) -> bool:
    """Send verification email to user"""
    if not all([settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.FROM_EMAIL]):
        # In development, just print the token
        print(f"Verification token for {email}: {token}")
        return True
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Підтвердження email адреси"
        message["From"] = settings.FROM_EMAIL
        message["To"] = email

        # Create the plain-text and HTML version of your message
        text = f"""
        Вітаємо!
        
        Для підтвердження вашої email адреси, перейдіть за посиланням:
        http://localhost:8000/verify-email?token={token}
        
        Якщо ви не реєструвались в нашому сервісі, проігноруйте це повідомлення.
        
        З повагою,
        Команда Contacts API
        """

        html = f"""
        <html>
        <body>
            <h2>Вітаємо!</h2>
            <p>Для підтвердження вашої email адреси, натисніть на кнопку нижче:</p>
            <a href="http://localhost:8000/verify-email?token={token}" 
               style="background-color: #4CAF50; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px;">
                Підтвердити email
            </a>
            <p>Або перейдіть за посиланням: <a href="http://localhost:8000/verify-email?token={token}">http://localhost:8000/verify-email?token={token}</a></p>
            <p>Якщо ви не реєструвались в нашому сервісі, проігноруйте це повідомлення.</p>
            <br>
            <p>З повагою,<br>Команда Contacts API</p>
        </body>
        </html>
        """

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, email, message.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False 