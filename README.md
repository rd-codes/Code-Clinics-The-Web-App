# Code Clinic Web Application

A modern web application for managing code clinic sessions, allowing students to book one-on-one coding sessions with volunteers. The application features a clean, intuitive interface and seamless integration with Google Calendar.


https://github.com/user-attachments/assets/e6fba014-ebfc-48f6-9331-a8808a7330a8


## Features

### User Management
- User authentication with email and password
- Separate roles for students and volunteers
- Secure password handling
- User profile management

### Calendar Management
- Interactive calendar view of available sessions
- Google Calendar integration for automatic event creation
- Real-time slot availability updates
- Prevention of double bookings
- Volunteers cannot book their own slots

### Booking System
- Easy booking of available slots
- Booking cancellation functionality
- Automatic email notifications through Google Calendar
- View of upcoming and past bookings

### Volunteer Features
- Ability to create volunteer slots
- Management of created slots
- View of booked sessions
- Prevention of self-booking

### User Interface
- Modern, responsive design
- Bootstrap-based layout
- Interactive calendar interface
- Real-time form validation
- User-friendly notifications
- Mobile-friendly design

## Prerequisites

- Python 3.8 or higher
- Google Calendar API credentials
- SQLite (included with Python)
- Modern web browser

## Setup

1. Clone the repository:
```bash
git clone github.com/rd-codes/Code-Clinics-The-Web-App/
cd Code-Clinics-The-Web-App
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Calendar API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Calendar API
   - Create a service account and download the credentials
   - Save the credentials file as `credentials.json` in the project root

5. Create a `.env` file in the project root with:
```
SECRET_KEY=your-secret-key-here
```

6. Initialize the database:
```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

## Usage Guide

### For Students
1. Register with your email and password
2. Login to your account
3. View available sessions in the calendar
4. Click on a session to book it
5. Manage your bookings from the dashboard
6. Cancel bookings if needed

### For Volunteers
1. Register with your email and password, and check "I want to be a volunteer"
2. Login to your account
3. Click "Add Volunteer Slot" to create available time slots
4. Manage your volunteer slots from the dashboard
5. View your upcoming sessions
6. Cannot book your own volunteer slots

## Project Structure

```
code-clinics-the-web-app/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── credentials.json        # Google Calendar API credentials
├── .env                    # Environment variables
├── static/                 # Static files
│   ├── css/               # CSS stylesheets
│   │   └── style.css      # Main stylesheet
│   └── js/                # JavaScript files
│       └── main.js        # Main JavaScript file
└── templates/             # HTML templates
    ├── base.html          # Base template
    ├── index.html         # Home page
    ├── login.html         # Login page
    ├── register.html      # Registration page
    └── dashboard.html     # Dashboard page
```

## Security Features

- Password hashing for secure storage
- CSRF protection on all forms
- Secure session management
- Input validation and sanitization
- Protected routes with login requirements
- Environment variable for sensitive data

## Error Handling

- Form validation with user feedback
- Graceful error handling for API calls
- User-friendly error messages
- Database transaction management
- Google Calendar API error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team.

## Acknowledgments

- Flask web framework
- Bootstrap for UI components
- FullCalendar for calendar functionality
- Google Calendar API
- SQLAlchemy for database management
