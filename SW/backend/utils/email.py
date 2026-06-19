import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import datetime
import traceback

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")           # Your Outlook email
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")   # Your Outlook password
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)    # Sender address (defaults to SMTP_USER)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def _log_smtp_failure(to_email: str, smtp_err: Exception) -> None:
    err_log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "email_errors.log")
    err_entry = (
        f"\n================================================\n"
        f"❌ SMTP FAILURE (Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"
        f"To: {to_email}\n"
        f"SMTP_HOST: {SMTP_HOST}\n"
        f"SMTP_PORT: {SMTP_PORT}\n"
        f"SMTP_USER: {SMTP_USER}\n"
        f"Error Details: {str(smtp_err)}\n"
        f"Traceback:\n{traceback.format_exc()}"
        f"================================================\n"
    )
    try:
        with open(err_log_path, "a", encoding="utf-8") as f:
            f.write(err_entry)
    except Exception:
        pass


def send_reset_email(to_email: str, reset_token: str) -> None:
    """
    Send a password-reset email containing a secure link with the token.
    The link adapts automatically to local or production based on FRONTEND_URL.
    """
    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"

    # Check if we are using dummy/default credentials
    is_dummy = (
        not SMTP_USER or 
        "your_outlook_email" in SMTP_USER or 
        not SMTP_PASSWORD or 
        "your_outlook_password" in SMTP_PASSWORD
    )

    if is_dummy:
        # Write mock email info to the project root directory for easy local development testing
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        log_path = os.path.join(root_dir, "sent_emails.log")
        log_entry = (
            f"\n================================================\n"
            f"📨 LOCAL EMAIL MOCK (Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"
            f"To: {to_email}\n"
            f"Reset Link: {reset_link}\n"
            f"================================================\n"
        )
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print(f"[INFO] SMTP is not configured. Mocked email saved to {log_path}")
            print(f"[INFO] Mock Reset Link: {reset_link}")
        except Exception as log_err:
            print(f"[ERROR] Failed to write mock email log: {log_err}")
            print(f"[INFO] Mock Reset Link: {reset_link}")
        return

    # ---- Build email ----
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset Your Baseet Password"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    # Plain text fallback
    text_body = f"""
Hi,

You requested a password reset for your Baseet account.

Click the link below to set a new password (valid for 1 hour):
{reset_link}

If you did not request this, you can safely ignore this email.

— The Baseet Team
"""

    # HTML version
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body {{ font-family: 'Nunito', Arial, sans-serif; background: #FFF9E6; margin: 0; padding: 0; }}
    .wrapper {{ max-width: 520px; margin: 40px auto; background: #fff;
               border-radius: 24px; border: 3px solid #DFE6E9;
               box-shadow: 0 10px 0 #DFE6E9; overflow: hidden; }}
    .header {{ background: #6C63FF; padding: 32px 24px; text-align: center; }}
    .header h1 {{ color: #fff; font-size: 28px; margin: 0; letter-spacing: -0.5px; }}
    .header p {{ color: rgba(255,255,255,0.85); margin: 6px 0 0; font-size: 14px; }}
    .body {{ padding: 36px 32px; }}
    .body p {{ color: #2D3436; font-size: 15px; line-height: 1.6; margin: 0 0 16px; }}
    .btn-wrap {{ text-align: center; margin: 28px 0; }}
    .btn {{ display: inline-block; background: #6C63FF; color: #fff !important;
            font-size: 16px; font-weight: 700; padding: 14px 36px;
            border-radius: 16px; text-decoration: none;
            box-shadow: 0 6px 0 #4e46d4; letter-spacing: 0.3px; }}
    .note {{ font-size: 13px; color: #636E72; border-top: 2px solid #DFE6E9;
             padding-top: 16px; margin-top: 8px; }}
    .footer {{ background: #f8f4ff; padding: 20px; text-align: center;
               font-size: 12px; color: #636E72; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>🎓 Baseet</h1>
      <p>AI-Powered Learning Platform</p>
    </div>
    <div class="body">
      <p>Hi there 👋,</p>
      <p>We received a request to reset the password for your Baseet account.<br>
         Click the button below to choose a new password:</p>
      <div class="btn-wrap">
        <a href="{reset_link}" class="btn">🔑 Reset My Password</a>
      </div>
      <p>This link is valid for <strong>1 hour</strong>. After that, you'll need to request a new one.</p>
      <p class="note">
        If you didn't request a password reset, you can safely ignore this email —
        your account remains secure.
      </p>
    </div>
    <div class="footer">
      © 2024 Baseet · AI Learning Platform<br>
      <small>This is an automated message, please do not reply.</small>
    </div>
  </div>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # ---- Send via Outlook SMTP (STARTTLS on port 587) ----
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())
    except (ssl.SSLCertVerificationError, ssl.SSLError) as ssl_err:
        print(f"[WARN] SSL verification failed: {ssl_err}. Retrying with unverified SSL context...")
        try:
            unverified_context = ssl._create_unverified_context()
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
                server.ehlo()
                server.starttls(context=unverified_context)
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, to_email, msg.as_string())
        except Exception as retry_err:
            _log_smtp_failure(to_email, retry_err)
            raise retry_err
    except Exception as smtp_err:
        _log_smtp_failure(to_email, smtp_err)
        raise smtp_err

