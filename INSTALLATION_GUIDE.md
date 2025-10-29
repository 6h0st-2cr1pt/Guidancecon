# Installation Guide - Reports & PDF Export

## Setting Up PDF Export Functionality

The Reports page includes PDF export functionality powered by WeasyPrint. Follow these steps to enable it:

### 1. Install Required Python Packages

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install WeasyPrint>=60.0
pip install Pillow>=10.0.0
```

### 2. Install System Dependencies

WeasyPrint requires certain system libraries. Install based on your OS:

#### Windows
- Download and install [GTK3 Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
- Or use the Microsoft C++ Build Tools if needed

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

#### macOS
```bash
brew install python3 cairo pango gdk-pixbuf libffi
```

### 3. Verify Installation

Test if WeasyPrint is working:

```python
python -c "from weasyprint import HTML; print('WeasyPrint is working!')"
```

### 4. Using the Reports Page

1. Navigate to **Reports** from the sidebar menu
2. Select date range and report type
3. Click **Generate Report** to view
4. Click **Print Report** for browser printing
5. Click **Export to PDF** to download as PDF

## Dedicated CSS Files

Each page now has its own CSS file for easier customization:

- `static/css/styles.css` - Base styles (shared across all pages)
- `static/css/dashboard.css` - Dashboard-specific styles
- `static/css/availability.css` - Availability page styles
- `static/css/analytics.css` - Analytics page styles
- `static/css/reports.css` - Reports page styles
- `static/css/notifications.css` - Notifications page styles

### How to Edit Page Styles

1. Open the dedicated CSS file for the page you want to customize
2. Add or modify styles
3. Refresh the page (hard refresh: Ctrl+Shift+R) to see changes
4. No need to edit the main `styles.css` file unless changing base styles

## Features Included

### Reports Page
- ✅ Date range filtering
- ✅ Summary and detailed report types
- ✅ Browser printing (Ctrl+P)
- ✅ PDF export with download
- ✅ Counselor performance statistics
- ✅ Program/issue breakdown
- ✅ Popular time slots analysis
- ✅ Student activity tracking
- ✅ Daily breakdown
- ✅ Print-optimized styling

### Report Data Includes
- Total appointments with status breakdown
- Completion and cancellation rates
- Per-counselor statistics
- Appointments by program/course
- Most popular booking times
- Top students by appointment count
- Day-by-day breakdown (for periods ≤31 days)
- Detailed appointment list (optional)

## Troubleshooting

### PDF Export Not Working
If you see an error about WeasyPrint:

1. Make sure WeasyPrint is installed: `pip install WeasyPrint`
2. Check system dependencies are installed (see above)
3. Restart the Django development server
4. If still not working, the system will show a friendly error message

### CSS Changes Not Showing
1. Hard refresh your browser: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
2. Clear browser cache
3. Check if the CSS file path is correct
4. Verify the version number in the URL (e.g., `?v=4.0`)

### Print Layout Issues
1. Use Print Preview in your browser first
2. Adjust margins in print settings
3. Select "Background graphics" option for colors
4. Consider using "Save as PDF" from browser print dialog as alternative

## Support
For issues or questions, contact the system administrator.

