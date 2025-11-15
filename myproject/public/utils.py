from django.core.mail import send_mail
from django.conf import settings
from sysadmin.models import Notification
import threading


def _send_email_sync(user, appointment, subject, message, from_email):
    """Internal function to send email synchronously"""
    try:
        print(f"[EMAIL THREAD] Attempting to send email to {user.email}")
        print(f"[EMAIL THREAD] Email settings - Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}, Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}, TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}, Timeout: {getattr(settings, 'EMAIL_TIMEOUT', 'Not set')}")
        print(f"[EMAIL THREAD] From: {from_email}, To: {user.email}, Subject: {subject}")
        
        # Try to get more detailed error information
        from django.core.mail import get_connection, EmailMessage
        connection = None
        try:
            connection = get_connection(
                fail_silently=False,  # Don't fail silently to catch errors
            )
            print(f"[EMAIL THREAD] Connection created: {type(connection)}")
            
            email_message = EmailMessage(
                subject=subject,
                body=message,
                from_email=from_email,
                to=[user.email],
            )
            
            result = connection.send_messages([email_message])
            
            print(f"[EMAIL THREAD] send_messages returned: {result}")
            
            if result and result > 0:
                print(f"SUCCESS: Email sent successfully to {user.email} ({result} message(s))")
                return True
            else:
                print(f"WARNING: Email sending returned {result} for {user.email}")
                return False
                
        except Exception as conn_error:
            error_msg = str(conn_error)
            print(f"[EMAIL THREAD] EXCEPTION during email connection/send: {error_msg}")
            import traceback
            print(f"[EMAIL THREAD] Traceback: {traceback.format_exc()}")
            
            # Check for network unreachable error (common on Render free tier)
            if "Network is unreachable" in error_msg or "Errno 101" in error_msg:
                print(f"[EMAIL THREAD] ERROR: Render free tier blocks outbound SMTP connections.")
                print(f"[EMAIL THREAD] To fix: Use an email API service (SendGrid, Mailgun, AWS SES) or upgrade Render plan.")
                print(f"[EMAIL THREAD] The appointment was confirmed successfully, but email could not be sent.")
            
            return False
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass
        
    except Exception as send_error:
        print(f"[EMAIL THREAD] EXCEPTION in _send_email_sync: {str(send_error)}")
        import traceback
        print(f"[EMAIL THREAD] Traceback: {traceback.format_exc()}")
        return False


def send_appointment_confirmation_email(user, appointment, async_send=True):
    """
    Send a confirmation email to the user about their appointment.
    If async_send=True, sends email in background thread (non-blocking).
    Returns True if email sending was initiated, False if validation fails.
    """
    try:
        # Validate user has email
        if not user.email:
            print(f"ERROR: User {user.username} (ID: {user.id}) does not have an email address")
            print(f"       Cannot send appointment confirmation email")
            return False
        
        print(f"Attempting to send email to {user.email} for user {user.username}")
        
        # Get appointment details safely
        counselor_name = appointment.counselor.get_full_name() or appointment.counselor.username or 'Counselor'
        
        # Safely get timeslot details
        if appointment.timeslot:
            try:
                date_str = appointment.timeslot.date.strftime('%B %d, %Y')
                time_str = appointment.timeslot.start_time.strftime('%I:%M %p')
            except Exception as e:
                print(f"Error formatting timeslot: {str(e)}")
                date_str = 'TBD'
                time_str = 'TBD'
        else:
            date_str = 'TBD'
            time_str = 'TBD'
        
        # Get status display safely
        try:
            status_display = appointment.get_status_display()
        except Exception:
            status_display = appointment.status.title()
        
        # Different subject and message based on appointment status
        if appointment.status == 'confirmed':
            subject = f'Appointment Confirmed - {counselor_name}'
            status_message = 'Your appointment has been confirmed by your counselor!'
        else:
            subject = f'Appointment Booking - {counselor_name}'
            status_message = 'Your appointment has been booked successfully!'
        
        user_name = user.get_full_name() or user.username or 'Student'
        
        message = f"""Hello {user_name},

{status_message}

Counselor: {counselor_name}
Date: {date_str}
Time: {time_str}
Status: {status_display}

Please check your appointments page for more details.

Thank you,
CHMSU Guidance Connect""".strip()
        
        # Extract email address from DEFAULT_FROM_EMAIL if it has display name format
        from_email = getattr(settings, 'EMAIL_HOST_USER', 'powerpuffgirls6112@gmail.com')
        if hasattr(settings, 'DEFAULT_FROM_EMAIL'):
            # Extract email from format like "Name <email@example.com>" or just "email@example.com"
            default_from = settings.DEFAULT_FROM_EMAIL
            if '<' in default_from and '>' in default_from:
                # Extract email from "Name <email@example.com>"
                from_email = default_from.split('<')[1].split('>')[0].strip()
            elif '@' in default_from:
                # It's already just an email address
                from_email = default_from
        
        # Ensure we have valid email settings
        if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
            print("Email host not configured")
            return False
        
        # Send email (asynchronously to avoid blocking the request)
        print(f"Sending email - From: {from_email}, To: {user.email}, Subject: {subject}")
        print(f"Email settings - Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}, Port: {getattr(settings, 'EMAIL_PORT', 'Not set')}, TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
        
        if async_send:
            # Send email in background thread to avoid blocking
            print(f"Starting email send in background thread for {user.email}")
            email_thread = threading.Thread(
                target=_send_email_sync,
                args=(user, appointment, subject, message, from_email),
                daemon=True  # Daemon thread so it doesn't prevent app shutdown
            )
            email_thread.start()
            print(f"Email thread started for {user.email} (non-blocking)")
            return True  # Return True immediately since we started the thread
        else:
            # Send synchronously (for testing)
            return _send_email_sync(user, appointment, subject, message, from_email)
            
    except Exception as e:
        # Log error but don't break the flow
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR sending email to {user.email if hasattr(user, 'email') and user.email else 'unknown'}: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Full traceback:")
        print(f"{error_details}")
        return False


def create_counselor_notification(counselor, appointment, notification_type):
    """
    Create a notification for the counselor about an appointment event.
    Returns the created Notification object or None if creation fails.
    """
    try:
        # Map notification types to titles and messages
        notification_titles = {
            'appointment_booked': 'New Appointment Booked',
            'appointment_confirmed': 'Appointment Confirmed',
            'appointment_cancelled': 'Appointment Cancelled',
            'appointment_rescheduled': 'Appointment Rescheduled',
            'appointment_reminder': 'Appointment Reminder',
        }
        
        notification_messages = {
            'appointment_booked': f'Student {appointment.student.get_full_name() or appointment.student.username} has booked an appointment with you.',
            'appointment_confirmed': f'Your appointment with {appointment.student.get_full_name() or appointment.student.username} has been confirmed.',
            'appointment_cancelled': f'Appointment with {appointment.student.get_full_name() or appointment.student.username} has been cancelled.',
            'appointment_rescheduled': f'Appointment with {appointment.student.get_full_name() or appointment.student.username} has been rescheduled.',
            'appointment_reminder': f'Reminder: You have an appointment with {appointment.student.get_full_name() or appointment.student.username} coming up.',
        }
        
        title = notification_titles.get(notification_type, 'Appointment Update')
        message = notification_messages.get(notification_type, 'You have an appointment update.')
        
        # Add appointment details to message if timeslot exists
        if appointment.timeslot:
            date_str = appointment.timeslot.date.strftime('%B %d, %Y')
            time_str = appointment.timeslot.start_time.strftime('%I:%M %p')
            message += f'\n\nDate: {date_str}\nTime: {time_str}'
        
        # Create notification
        notification = Notification.objects.create(
            counselor=counselor,
            title=title,
            message=message,
            notification_type=notification_type,
            appointment=appointment,
            is_read=False
        )
        
        return notification
    except Exception as e:
        # Log error but don't break the flow
        print(f"Error creating notification: {str(e)}")
        return None

