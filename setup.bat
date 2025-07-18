@echo off
echo 🏥 Emergency Hospital Bed Booking System Setup
echo ==============================================

REM Create virtual environment
echo 📦 Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Setup environment file
echo ⚙️ Setting up environment configuration...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file from template
    echo ⚠️  Please edit .env with your actual configuration values
) else (
    echo ℹ️  .env file already exists
)

REM Setup config file
echo 🗄️ Setting up database configuration...
if not exist project\templates\config.json (
    copy project\templates\config.json.example project\templates\config.json
    echo ✅ Created config.json from template
    echo ⚠️  Please edit project\templates\config.json with your database credentials
) else (
    echo ℹ️  config.json file already exists
)

echo.
echo 🔥 Firebase Setup Required:
echo 1. Go to https://console.firebase.google.com/
echo 2. Create or select your project
echo 3. Go to Project Settings → Service Accounts
echo 4. Click 'Generate new private key'
echo 5. Save the downloaded file as: project\firebase-credentials.json
echo.
echo 📋 Next Steps:
echo 1. Edit .env with your configuration
echo 2. Edit project\templates\config.json with your database credentials
echo 3. Set up Firebase credentials as described above
echo 4. Create MySQL database: CREATE DATABASE emergency_bed;
echo 5. Run: python project\main.py
echo.
echo ⚠️  SECURITY REMINDER:
echo    Never commit .env, config.json, or firebase-credentials.json to version control!
echo.
echo ✅ Setup complete! Please follow the next steps above.
pause
