# PyOTP - Multi-Factor Authentication Application

A secure web application built with FastAPI that implements user registration, authentication, and Google Authenticator MFA support.

## Features

- 🔐 **User Registration & Authentication**: Secure signup and login with email/password
- 📱 **Google Authenticator MFA**: Two-factor authentication using TOTP (Time-based One-Time Password)
- 💾 **SQLite Database**: Persistent user data storage
- 🎨 **Modern UI**: Responsive web interface with beautiful design
- 🔑 **JWT Tokens**: Secure session management
- 🛡️ **Password Hashing**: Bcrypt password encryption

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the application**:
   Open your browser and go to `http://localhost:8000`

## Usage

### 1. User Registration
- Navigate to the signup page
- Enter your email, name, and password
- Click "Create Account"

### 2. Setting Up MFA (Two-Factor Authentication)
- After logging in, click "Setup Two-Factor Authentication"
- Scan the QR code with your Google Authenticator app
- Or manually enter the secret key in your authenticator app
- Enter the 6-digit code from your app to verify and enable MFA

### 3. Logging In with MFA
- Enter your email and password
- If MFA is enabled, you'll be prompted for the 6-digit code
- Enter the code from your Google Authenticator app

### 4. Dashboard
- View your account information
- See MFA status
- Access security tips

## Google Authenticator Setup

1. **Download Google Authenticator**:
   - iOS: [App Store](https://apps.apple.com/app/google-authenticator/id388497605)
   - Android: [Google Play](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2)

2. **Add Account**:
   - Open Google Authenticator
   - Tap the "+" button
   - Choose "Scan a QR code" or "Enter a setup key"
   - Scan the QR code or enter the secret key from the setup page

3. **Verify Setup**:
   - Enter the 6-digit code shown in your app
   - Click "Enable Two-Factor Authentication"

## Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **JWT Tokens**: Secure session management with JSON Web Tokens
- **MFA Support**: Additional security layer with Google Authenticator
- **SQLite Database**: Local data storage (can be migrated to PostgreSQL/MySQL for production)
- **HTTPS Ready**: Configure SSL certificates for production deployment

## Project Structure

```
PyOTP/
├── main.py              # FastAPI application and routes
├── database.py          # Database configuration and models
├── auth.py              # Authentication utilities and MFA functions
├── models.py            # Pydantic models for validation
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── signup.html
│   ├── login.html
│   ├── dashboard.html
│   ├── setup_mfa.html
│   ├── mfa_verify.html
│   └── mfa_already_setup.html
└── static/             # Static files (CSS, JS, images)
```

## API Endpoints

- `GET /` - Home page
- `GET /signup` - Signup page
- `POST /signup` - User registration
- `GET /login` - Login page
- `POST /login` - User authentication
- `GET /dashboard` - User dashboard (protected)
- `GET /setup-mfa` - MFA setup page (protected)
- `POST /enable-mfa` - Enable MFA (protected)
- `GET /mfa-verify` - MFA verification page
- `POST /mfa-verify` - Verify MFA code
- `POST /logout` - User logout

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database
The application uses SQLite by default. The database file (`users.db`) will be created automatically when you first run the application.

### Environment Variables
For production deployment, consider setting these environment variables:
- `SECRET_KEY`: Change the JWT secret key in `auth.py`
- `DATABASE_URL`: Use a production database like PostgreSQL

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   uvicorn main:app --port 8001
   ```

2. **Dependencies not found**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database issues**:
   Delete `users.db` file and restart the application

4. **MFA code not working**:
   - Ensure your device time is synchronized
   - Check that you're using the correct secret key
   - Try generating a new MFA setup

## Production Deployment

For production deployment, consider:

1. **Use a production WSGI server** like Gunicorn
2. **Set up a reverse proxy** (Nginx/Apache)
3. **Use HTTPS** with SSL certificates
4. **Use a production database** (PostgreSQL/MySQL)
5. **Set secure environment variables**
6. **Implement rate limiting**
7. **Add logging and monitoring**

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!
