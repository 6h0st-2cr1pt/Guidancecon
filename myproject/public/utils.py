"""
Utility functions for the public app
"""
from django.utils import timezone


def create_counselor_notification(counselor, appointment, notification_type):
    """
    Create a notification for appointment-related events.
    
    Args:
        counselor: The counselor User object
        appointment: The Appointment object
        notification_type: Type of notification (e.g., 'appointment_confirmed', 'appointment_cancelled', 'appointment_rescheduled')
    """
    # This is a placeholder function for future notification system
    # You can extend this to create actual notifications for students
    
    notification_messages = {
        'appointment_confirmed': f'Your appointment with {counselor.get_full_name()} has been confirmed.',
        'appointment_cancelled': f'Your appointment with {counselor.get_full_name()} has been cancelled.',
        'appointment_rescheduled': f'Your appointment with {counselor.get_full_name()} has been rescheduled.',
    }
    
    # Log the notification (you can extend this to save to database or send emails)
    message = notification_messages.get(notification_type, 'Appointment status updated.')
    
    # Future implementation: Create a Notification model instance
    # For now, this prevents the import error
    pass


def get_time_ago(dt):
    """
    Convert datetime to human-readable time ago format.
    
    Args:
        dt: datetime object
        
    Returns:
        str: Human-readable time difference (e.g., "2 hours ago")
    """
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def format_appointment_time(appointment):
    """
    Format appointment date and time for display.
    
    Args:
        appointment: Appointment object
        
    Returns:
        str: Formatted string like "March 7, 2025 at 9:00 AM"
    """
    if appointment.timeslot:
        date_str = appointment.timeslot.date.strftime("%B %d, %Y")
        time_str = appointment.timeslot.start_time.strftime("%I:%M %p")
        return f"{date_str} at {time_str}"
    return "No time scheduled"


def get_counselor_full_name(counselor):
    """
    Get the full name of a counselor with middle initial if available.
    
    Args:
        counselor: User object
        
    Returns:
        str: Full name with middle initial
    """
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT middle_initial FROM auth_user WHERE id = %s", [counselor.id])
            row = cursor.fetchone()
            middle_initial = row[0] if row and row[0] else ''
        
        if middle_initial:
            return f"{counselor.first_name} {middle_initial}. {counselor.last_name}"
        return counselor.get_full_name() or counselor.username
    except:
        return counselor.get_full_name() or counselor.username

