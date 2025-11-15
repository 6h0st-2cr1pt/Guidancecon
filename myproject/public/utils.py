from django.core.mail import send_mail
from django.conf import settings
from sysadmin.models import Notification
import threading


def _send_email_sync(user, appointment, subject, message, from_email):
    """Internal function to send email synchronously using Mailjet API"""
    try:
        print(f"[EMAIL THREAD] Attempting to send email to {user.email} via Mailjet API")
        
        # Check if Mailjet is configured
        mailjet_api_key = getattr(settings, 'MAILJET_API_KEY', '')
        mailjet_api_secret = getattr(settings, 'MAILJET_API_SECRET', '')
        
        if not mailjet_api_key or not mailjet_api_secret:
            print(f"[EMAIL THREAD] ERROR: Mailjet API credentials not configured")
            print(f"[EMAIL THREAD] Please set MAILJET_API_KEY and MAILJET_API_SECRET environment variables")
            return False
        
        # Get from email address and name from settings
        from_email_address = getattr(settings, 'FROM_EMAIL_ADDRESS', 'powerpuffgirls6112@gmail.com')
        from_email_name = getattr(settings, 'FROM_EMAIL_NAME', 'CHMSU Guidance Connect')
        
        # Extract email from from_email if it has display name format
        if '<' in from_email and '>' in from_email:
            from_email_address = from_email.split('<')[1].split('>')[0].strip()
        elif '@' in from_email:
            from_email_address = from_email
        
        print(f"[EMAIL THREAD] From: {from_email_name} <{from_email_address}>, To: {user.email}, Subject: {subject}")
        
        try:
            from mailjet_rest import Client
            
            # Initialize Mailjet client
            mailjet = Client(auth=(mailjet_api_key, mailjet_api_secret), version='v3.1')
            
            # Prepare email data
            email_data = {
                'Messages': [{
                    'From': {
                        'Email': from_email_address,
                        'Name': from_email_name
                    },
                    'To': [{
                        'Email': user.email,
                        'Name': user.get_full_name() or user.username or 'Student'
                    }],
                    'Subject': subject,
                    'TextPart': message,
                    'HTMLPart': message.replace('\n', '<br>')  # Simple HTML conversion
                }]
            }
            
            print(f"[EMAIL THREAD] Sending email via Mailjet API...")
            result = mailjet.send.create(data=email_data)
            
            # Check response
            if result.status_code == 200:
                response_data = result.json()
                print(f"[EMAIL THREAD] Mailjet API response: {response_data}")
                
                # Mailjet v3.1 API returns messages in 'Messages' array
                if 'Messages' in response_data and len(response_data['Messages']) > 0:
                    message_status = response_data['Messages'][0]
                    
                    # Check if message was sent successfully
                    # Mailjet returns 'To' array with message details
                    if 'To' in message_status and len(message_status['To']) > 0:
                        to_status = message_status['To'][0]
                        if 'MessageID' in to_status or 'MessageUUID' in to_status:
                            message_id = to_status.get('MessageID') or to_status.get('MessageUUID', 'N/A')
                            print(f"SUCCESS: Email sent successfully to {user.email} via Mailjet")
                            print(f"[EMAIL THREAD] Mailjet MessageID: {message_id}")
                            return True
                        else:
                            # Check for errors in the To array
                            if 'Errors' in to_status:
                                print(f"WARNING: Mailjet returned errors: {to_status['Errors']}")
                                return False
                    
                    # Fallback: check for errors at message level
                    if 'Errors' in message_status and len(message_status['Errors']) > 0:
                        print(f"WARNING: Mailjet returned errors: {message_status['Errors']}")
                        return False
                    
                    # If we have Messages but no clear success indicator, assume success
                    print(f"SUCCESS: Email sent successfully to {user.email} via Mailjet (status code 200)")
                    return True
                else:
                    print(f"WARNING: Unexpected Mailjet response format: {response_data}")
                    return False
            else:
                print(f"ERROR: Mailjet API returned status code {result.status_code}")
                try:
                    error_data = result.json()
                    print(f"[EMAIL THREAD] Error response: {error_data}")
                except:
                    print(f"[EMAIL THREAD] Response text: {result.text}")
                return False
                
        except ImportError:
            print(f"[EMAIL THREAD] ERROR: mailjet-rest package not installed")
            print(f"[EMAIL THREAD] Please install it: pip install mailjet-rest")
            return False
        except Exception as mailjet_error:
            error_msg = str(mailjet_error)
            print(f"[EMAIL THREAD] EXCEPTION during Mailjet API call: {error_msg}")
            import traceback
            print(f"[EMAIL THREAD] Traceback: {traceback.format_exc()}")
            return False
        
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
        
        # Send email (asynchronously to avoid blocking the request)
        print(f"Sending email - From: {from_email}, To: {user.email}, Subject: {subject}")
        print(f"Using Mailjet API for email delivery")
        
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

