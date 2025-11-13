"""
Test SMTP email configuration
Run with: python manage.py shell < test_smtp.py
Or: python manage.py shell, then copy-paste this code
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("Testing SMTP Email Configuration")
print("=" * 60)

# Test email details
test_email = "sabordojonald@gmail.com"
test_subject = "Test Email from CHMSU Guidance Connect"
test_message = """Hello,

This is a test email from CHMSU Guidance Connect to verify SMTP configuration.

If you receive this email, the SMTP settings are working correctly!

Email Configuration:
- Host: {host}
- Port: {port}
- TLS: {tls}
- From: {from_email}

Thank you,
CHMSU Guidance Connect
""".format(
    host=getattr(settings, 'EMAIL_HOST', 'Not set'),
    port=getattr(settings, 'EMAIL_PORT', 'Not set'),
    tls=getattr(settings, 'EMAIL_USE_TLS', 'Not set'),
    from_email=getattr(settings, 'EMAIL_HOST_USER', 'Not set')
)

# Get from_email
from_email = getattr(settings, 'EMAIL_HOST_USER', 'powerpuffgirls6112@gmail.com')
if hasattr(settings, 'DEFAULT_FROM_EMAIL'):
    default_from = settings.DEFAULT_FROM_EMAIL
    if '<' in default_from and '>' in default_from:
        from_email = default_from.split('<')[1].split('>')[0].strip()
    elif '@' in default_from:
        from_email = default_from

print(f"\nEmail Configuration:")
print(f"   Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
print(f"   Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
print(f"   TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
print(f"   From: {from_email}")
print(f"   To: {test_email}")
print(f"\nSending test email...")

try:
    result = send_mail(
        test_subject,
        test_message,
        from_email,
        [test_email],
        fail_silently=False,  # Raise exception if it fails
    )
    
    if result:
        print(f"SUCCESS: Email sent successfully!")
        print(f"   Result: {result}")
        print(f"   Check the inbox of {test_email} for the test email.")
    else:
        print(f"FAILED: Email sending returned False")
        print(f"   This usually means the email was not sent.")
        
except Exception as e:
    import traceback
    error_trace = traceback.format_exc()
    print(f"ERROR: Failed to send email")
    print(f"   Error: {str(e)}")
    print(f"   Error type: {type(e).__name__}")
    print(f"\n   Full traceback:")
    print(f"   {error_trace}")
    
    # Check for common issues
    print(f"\nTroubleshooting:")
    if "authentication failed" in str(e).lower():
        print(f"   - Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD")
        print(f"   - Make sure you're using an App Password, not your regular password")
    elif "connection" in str(e).lower():
        print(f"   - Check EMAIL_HOST and EMAIL_PORT")
        print(f"   - Make sure the SMTP server is accessible")
    elif "tls" in str(e).lower() or "ssl" in str(e).lower():
        print(f"   - Check EMAIL_USE_TLS setting")
        print(f"   - Try EMAIL_USE_SSL instead if TLS doesn't work")

print(f"\n" + "=" * 60)

