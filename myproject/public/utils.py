from django.core.mail import send_mail
from django.conf import settings
from sysadmin.models import Notification


def send_appointment_confirmation_email(user, appointment):
    """
    Send a confirmation email to the user about their appointment.
    Returns True if email was sent successfully, False otherwise.
    """
    try:
        # Get appointment details
        counselor_name = appointment.counselor.get_full_name() or appointment.counselor.username
        date_str = appointment.timeslot.date.strftime('%B %d, %Y') if appointment.timeslot else 'TBD'
        time_str = appointment.timeslot.start_time.strftime('%I:%M %p') if appointment.timeslot else 'TBD'
        
        subject = f'Appointment Confirmation - {counselor_name}'
        message = f"""
Hello {user.get_full_name() or user.username},

Your appointment has been booked successfully!

Counselor: {counselor_name}
Date: {date_str}
Time: {time_str}
Status: {appointment.get_status_display()}

Please check your appointments page for more details.

Thank you,
CHMSU Guidance Connect
        """.strip()
        
        # Try to send email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@guidanceconnect.com',
            [user.email],
            fail_silently=True,  # Don't raise exception if email fails
        )
        return True
    except Exception as e:
        # Log error but don't break the flow
        print(f"Error sending email: {str(e)}")
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

