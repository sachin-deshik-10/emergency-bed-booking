# Emergency Hospital Bed Booking System

A comprehensive web-based application for managing emergency hospital bed reservations during critical situations. This system streamlines the process of finding and booking available beds across multiple hospitals in real-time.

## 🏥 Project Overview

The Emergency Hospital Bed Booking System is designed to address the critical need for efficient bed allocation during emergency situations. Built with Flask and modern web technologies, it provides a centralized platform for:

- **Hospitals** to manage and update their bed availability
- **Patients** to find and book available beds based on their requirements
- **Administrators** to oversee the entire system and manage hospital registrations

## ✨ Key Features

### 🔐 Multi-User Authentication System

- **Patient Login**: Secure registration and authentication for patients
- **Hospital Login**: Dedicated portal for hospital staff
- **Admin Dashboard**: Administrative access for system management

### 🛏️ Real-Time Bed Management

- **Live Bed Tracking**: Real-time updates of bed availability
- **Multiple Bed Types**:
  - Normal Beds
  - HICU (High Intensity Care Unit) Beds
  - ICU (Intensive Care Unit) Beds
  - Ventilator Beds
- **Hospital-wise Filtering**: Search and filter beds by hospital code

### 📊 Comprehensive Dashboard

- **Hospital Data Management**: Add, edit, and delete hospital information
- **Patient Details Tracking**: Complete patient information management
- **Operations Monitoring**: Track all bed allocation operations with timestamps

### 📁 Document Management

- **File Upload System**: Firebase-integrated file storage
- **PDF Report Viewing**: Direct PDF viewing capability for medical reports
- **Secure Document Access**: Role-based document access control

### 🌍 Enhanced User Experience

- **Responsive Design**: Bootstrap-powered responsive interface
- **Multi-language Support**: Google Translate integration
- **Mobile-Friendly**: Optimized for mobile devices
- **Real-time Notifications**: Flash messaging system for user feedback

## 🛠️ Technology Stack

### Backend

- **Framework**: Flask (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Session Management**: Flask sessions

### Frontend

- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5.3.2
- **Icons**: Bootstrap Icons, BoxIcons, FontAwesome
- **Animations**: AOS (Animate On Scroll)
- **UI Components**:
  - GLightbox for image/video lightbox
  - Swiper for carousels
  - PureCounter for animated counters

### Cloud Services

- **File Storage**: Firebase Storage
- **Authentication Service**: Firebase Admin SDK
- **Database**: MySQL (Local/Cloud compatible)

### Additional Libraries

- **AOS**: Smooth scroll animations
- **GLightbox**: Modern lightbox component
- **Swiper**: Modern touch slider
- **PureCounter**: Animated number counters

## 📋 Database Schema

### User Models

#### `User` (Patients)

```sql
- id (Primary Key)
- email (String, 50)
- dob (String, 1000)
```

#### `Hospitaluser` (Hospital Staff)

```sql
- id (Primary Key)
- hcode (String, 20) - Hospital Code
- email (String, 50)
- password (String, 1000) - Hashed password
```

### Hospital Management

#### `Hospitaldata` (Hospital Information)

```sql
- id (Primary Key)
- hcode (String, 20, Unique) - Hospital Code
- hname (String, 100) - Hospital Name
- normalbed (Integer) - Normal beds available
- hicubed (Integer) - HICU beds available
- icubed (Integer) - ICU beds available
- vbed (Integer) - Ventilator beds available
```

### Booking Management

#### `Bookingpatient` (Patient Bookings)

```sql
- id (Primary Key)
- bedtype (String, 100) - Type of bed booked
- hcode (String, 20) - Hospital code
- spo2 (Integer) - Oxygen saturation level
- pname (String, 100) - Patient name
- pphone (String, 100) - Patient phone
- paddress (String, 100) - Patient address
- email (String, 50, Unique) - Patient email
```

#### `Trig` (Operation Logs)

```sql
- id (Primary Key)
- hcode (String, 20) - Hospital code
- normalbed (Integer) - Normal beds after operation
- hicubed (Integer) - HICU beds after operation
- icubed (Integer) - ICU beds after operation
- vbed (Integer) - Ventilator beds after operation
- querys (String, 50) - Operation type
- date (String, 50) - Operation timestamp
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL Database
- Firebase Account (for file storage)

### 1. Clone the Repository

```bash
git clone https://github.com/sachin-deshik-10/emergency-bed-booking.git
cd emergency-bed-booking
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE emergency_bed;
```

### 5. Environment Configuration

⚠️ **IMPORTANT: Never commit sensitive credentials to version control!**

1. Copy the environment template:

```bash
cp .env.example .env
```

2. Edit `.env` with your actual values:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production  # Use 'development' for local dev
FLASK_DEBUG=False     # Set to True only for development

# Database Configuration
DATABASE_URL=mysql+mysqldb://root:your_password@localhost/emergency_bed
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=emergency_bed

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=project/firebase-credentials.json
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### 6. Firebase Setup

⚠️ **Security Notice**: Firebase service account keys contain sensitive credentials and should never be committed to version control.

1. **Create a Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project or select an existing one
   - Enable Firebase Storage

2. **Generate Service Account Credentials**:
   - Go to Project Settings → Service Accounts
   - Click "Generate new private key"
   - Download the JSON file

3. **Secure Credential Setup**:

   ```bash
   # Create credentials directory
   mkdir -p project/credentials
   
   # Move your downloaded Firebase key to this location
   mv ~/Downloads/your-firebase-key.json project/firebase-credentials.json
   
   # Set restrictive permissions (Linux/Mac)
   chmod 600 project/firebase-credentials.json
   ```

4. **Update Configuration**:
   - Ensure your `.env` file points to the correct credential path
   - Never commit files with pattern `*firebase*adminsdk*.json`

### 7. Security Configuration

Before running in production:

1. **Update config.json Template**:

   ```bash
   # Copy the config template
   cp project/templates/config.json.example project/templates/config.json
   # Edit with your actual database credentials
   ```

2. **Secure File Permissions**:

   ```bash
   chmod 600 .env
   chmod 600 project/firebase-credentials.json
   chmod 600 project/templates/config.json
   ```

### 8. Run the Application

```bash
python project/main.py
```

The application will be available at `http://localhost:5000`

## � Quick Setup (Automated)

For a faster setup process, use the provided setup scripts:

### Linux/Mac/Git Bash

```bash
chmod +x setup.sh
./setup.sh
```

### Windows

```cmd
setup.bat
```

These scripts will:

- Create and activate virtual environment
- Install Python dependencies
- Copy configuration templates
- Set secure file permissions
- Provide setup instructions

⚠️ **Important**: You'll still need to manually:

1. Edit `.env` with your configuration
2. Edit `project/templates/config.json` with database credentials
3. Download and place Firebase credentials as `project/firebase-credentials.json`
4. Create the MySQL database

## 🔧 Troubleshooting

If you encounter issues during setup or deployment, check the [Troubleshooting Guide](TROUBLESHOOTING.md) for solutions to common problems:

- Git push issues (secret scanning violations)
- Credential setup problems
- Database connection errors
- Python environment issues
- Web application errors

## �📖 Usage Guide

### For Patients

1. **Registration**: Sign up with email and personal details
2. **Browse Hospitals**: View available beds across different hospitals
3. **Book Beds**: Select bed type and hospital based on availability
4. **Upload Documents**: Submit medical reports through the secure upload system
5. **Track Booking**: Monitor booking status and hospital details

### For Hospital Staff

1. **Login**: Access the hospital portal with credentials
2. **Manage Bed Data**: Update real-time bed availability
3. **View Patient Details**: Access patient information and medical reports
4. **Update Information**: Modify hospital details and bed counts

### For Administrators

1. **System Access**: Administrative login for full system control
2. **Hospital Management**: Add new hospitals and manage existing ones
3. **User Management**: Oversee user registrations and access
4. **System Monitoring**: Track operations and system performance

## 🔄 API Endpoints

### Public Routes

- `GET /` - Home page
- `GET /signup` - Patient registration
- `GET /login` - Patient login
- `GET /hospitallogin` - Hospital login
- `GET /admin` - Admin login

### Protected Routes (Authentication Required)

- `GET /slotbooking` - Bed booking interface
- `GET /pdetails` - Patient details view
- `POST /upload` - File upload
- `GET /view_pdf` - PDF document viewer
- `POST /addhospitalinfo` - Add hospital data
- `GET /hedit/<id>` - Edit hospital information
- `DELETE /hdelete/<id>` - Delete hospital data

### System Routes

- `GET /trigers` - View operation logs
- `GET /test` - Database connection test
- `GET /logout` - User logout
- `GET /logoutadmin` - Admin logout

## 🔐 Security Features

### Authentication & Authorization

- **Password Hashing**: Werkzeug-based secure password storage
- **Session Management**: Flask-Login session handling
- **Role-based Access**: Different access levels for patients, hospitals, and admins
- **CSRF Protection**: Built-in Flask security measures

### Data Protection

- **Input Validation**: Server-side validation for all forms
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **Secure File Handling**: Firebase-managed file storage
- **Data Encryption**: Encrypted sensitive data storage

## 🎨 UI/UX Features

### Responsive Design

- **Mobile-First**: Optimized for mobile devices
- **Cross-Browser**: Compatible with modern browsers
- **Accessibility**: WCAG-compliant design elements

### Interactive Elements

- **Real-time Updates**: Dynamic bed availability display
- **Smooth Animations**: AOS-powered scroll animations
- **Loading States**: User feedback during operations
- **Error Handling**: Comprehensive error messaging

## 📱 Screenshots

*Include screenshots of your application here showing:*

- Home page
- Login interfaces
- Bed booking system
- Hospital dashboard
- Admin panel

## 🤝 Contributing

We welcome contributions to improve the Emergency Hospital Bed Booking System!

### Development Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Include comments for complex logic
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Project Lead**: [Your Name]
- **Backend Developer**: [Name]
- **Frontend Developer**: [Name]
- **Database Designer**: [Name]

## 🙏 Acknowledgments

- Bootstrap team for the excellent CSS framework
- Firebase team for reliable cloud services
- Flask community for the robust web framework
- All contributors who helped improve this system

## 📞 Support

For support, please email <nayakulasachindeshik@gmail.com> or create an issue in the GitHub repository.

## 🔮 Future Enhancements

- [ ] **Mobile App**: Native mobile applications for iOS and Android
- [ ] **Real-time Chat**: Communication system between patients and hospitals
- [ ] **Payment Integration**: Online payment for bed reservations
- [ ] **Analytics Dashboard**: Advanced analytics and reporting
- [ ] **API Documentation**: Comprehensive REST API documentation
- [ ] **Multi-language Support**: Additional language localizations
- [ ] **Notification System**: SMS and email notifications
- [ ] **Geolocation**: Location-based hospital recommendations

---

*Built with ❤️ for emergency healthcare management*
