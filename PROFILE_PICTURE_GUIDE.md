# Profile Picture Storage Guide

## Overview
Profile pictures for counselors are now stored as binary data (`bytea`) in the PostgreSQL database in the `auth_user` table's `image_data` column.

## How It Works

### 1. Uploading Profile Pictures
When a counselor signs up through the sysadmin signup form (`/sysadmin/signup/`), they can upload a profile picture. The image is:
- Read as binary data
- Stored directly in the `auth_user.image_data` column as `bytea`
- Automatically handled by the signup view

### 2. Retrieving Profile Pictures
Profile pictures are served through dedicated views:

#### For Sysadmin:
```
URL: /sysadmin/profile-picture/<user_id>/
View: sysadmin.views.profile_picture
```

#### For Public:
```
URL: /profile-picture/<user_id>/
View: public.views.profile_picture
```

### 3. Displaying Profile Pictures in Templates

#### Example 1: Static HTML Display
```html
<img src="{% url 'public:profile_picture' counselor.id %}" 
     alt="Profile Picture" 
     style="width: 80px; height: 80px; border-radius: 8px; object-fit: cover;">
```

#### Example 2: Dynamic JavaScript Display (Already Implemented)
The appointment booking page already implements dynamic profile picture loading:
- When a counselor is selected, the JavaScript `loadCounselorDetails()` function fetches their information
- The API endpoint `/counselor/<id>/availability/` returns a JSON response including `profile_picture` URL
- The JavaScript updates the `<img>` element's `src` attribute with this URL

#### Example 3: With Fallback Placeholder
```html
{% if counselor.has_image %}
    <img src="{% url 'sysadmin:profile_picture' counselor.id %}" 
         alt="Profile Picture">
{% else %}
    <div class="avatar-placeholder">👤</div>
{% endif %}
```

### 4. Adding Profile Pictures to Existing Counselors

To add a profile picture to an existing counselor account:

1. **Option A: Through pgAdmin or psql**
```sql
-- Read the image file and convert to bytea
UPDATE auth_user 
SET image_data = pg_read_binary_file('/path/to/image.jpg')::bytea 
WHERE id = <counselor_user_id>;
```

2. **Option B: Create an Update Form** (recommended)
Create a profile update page where counselors can upload their pictures after account creation.

### 5. Checking If a Counselor Has a Profile Picture

In your views, you can check if a counselor has a profile picture:
```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT image_data FROM auth_user WHERE id = %s", [user_id])
    row = cursor.fetchone()
    has_image = row[0] is not None if row else False
```

### 6. Image Format Support
The profile picture view automatically detects the image format:
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)

The correct MIME type is automatically set based on the image header.

### 7. Caching
Profile pictures are cached for 1 day (`Cache-Control: public, max-age=86400`) to improve performance.

## Database Schema

### auth_user table (extended)
| Column | Type | Description |
|--------|------|-------------|
| `image_data` | `bytea` | Binary data of the profile picture |
| `middle_initial` | `varchar(10)` | Middle initial |
| `assigned_college` | `varchar(255)` | Assigned college |
| `title` | `varchar(100)` | Title/Qualifications |
| `bio` | `text` | Bio/Description |

## Advantages of bytea Storage
1. **No File System Management**: No need to handle file uploads, storage, or cleanup
2. **Database Consistency**: Images are part of database backups
3. **Simplified Deployment**: No separate media file storage required
4. **Atomic Operations**: Image updates are transactional with other user data
5. **Easy Migration**: Database can be moved without worrying about media files

## Size Limit

Profile pictures are limited to **2 MB maximum**. This limit is enforced through:

### Server-Side Validation
The signup view checks the file size and returns an error if it exceeds 2 MB:
```python
if profile_picture.size > 2 * 1024 * 1024:  # 2 MB
    context['error'] = f'Profile picture is too large ({size_mb:.2f} MB). Maximum allowed size is 2 MB.'
```

### Client-Side Validation
The signup form includes JavaScript validation that:
- Checks file size immediately when a file is selected
- Displays the actual file size to the user
- Disables the submit button if file is too large
- Clears the file input automatically
- Shows a clear error message

## Considerations
1. **Size Limit**: Profile pictures are limited to 2 MB to ensure optimal performance and reasonable database size
2. **Performance**: The 2 MB limit helps maintain fast page loads and database backups
3. **Backup Size**: Profile pictures will increase database backup size proportionally
4. **Image Optimization**: Users should compress/resize images before upload if they exceed the limit

