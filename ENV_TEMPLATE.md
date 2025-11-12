# Environment Variables Template

## For Local Development (.env file)

```env
# Django Settings
DJANGO_SECRET_KEY=your-local-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration - Option 1: Individual variables
DB_NAME=guidance
DB_USER=postgres
DB_PASSWORD=your-local-password
DB_HOST=localhost
DB_PORT=5432

# Database Configuration - Option 2: DATABASE_URL (for Render External Connection)
# DATABASE_URL=postgresql://user:password@host:port/database

# Email Configuration (Optional - leave empty to use console backend)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@guidanceconnect.com
ADMIN_EMAIL=admin@guidanceconnect.com
```

## For Render Deployment (Set in Render Dashboard)

### Required:
```
DJANGO_SECRET_KEY=<generate-new-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com,localhost,127.0.0.1
DATABASE_URL=<internal-database-url-from-render>
```

### Optional (for email):
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@guidanceconnect.com
ADMIN_EMAIL=admin@guidanceconnect.com
```

## Notes:

1. **Local Development**: Use individual DB variables OR DATABASE_URL (Render's External URL)
2. **Render Deployment**: Use DATABASE_URL (Render's Internal URL)
3. **Secret Key**: Generate a new one for production: 
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
4. **Email**: Optional - app works without it (uses console backend)

