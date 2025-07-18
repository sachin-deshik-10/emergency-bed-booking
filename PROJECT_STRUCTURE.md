# Project Structure

This document provides a detailed overview of the Emergency Hospital Bed Booking System project structure and organization.

## Root Directory Structure

```
DBMSlabEL2/
├── project/                    # Main application directory
├── nosql/                      # Firebase integration and NoSQL components
├── bootstrap/                  # Bootstrap templates and forms
├── README.md                   # Project overview and setup instructions
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT license file
├── CONTRIBUTING.md            # Contribution guidelines
├── API_DOCUMENTATION.md       # API endpoints documentation
├── DATABASE_SETUP.md          # Database configuration guide
├── DEPLOYMENT.md              # Deployment instructions
├── SECURITY.md                # Security guidelines and best practices
├── TESTING.md                 # Testing procedures and guidelines
├── CHANGELOG.md               # Version history and changes
└── PROJECT_STRUCTURE.md       # This file
```

## Main Application Directory (`project/`)

### Core Application Files

```
project/
├── main.py                     # Main Flask application file
├── test.py                     # Test configuration and utilities
├── emergencybooking-31043-firebase-adminsdk-l69k0-98c85bc3f2.json  # Firebase credentials
├── pdf.pdf                     # Sample PDF file for testing
├── filepath                    # File path configuration
├── filepth                     # Additional file path settings
├── templates/                  # HTML templates directory
└── static/                     # Static assets directory
```

### Application Entry Point (`main.py`)

The main Flask application file containing:

- **Flask Application Setup**: App configuration and initialization
- **Database Models**: SQLAlchemy models for all entities
- **Route Handlers**: All URL endpoints and request handlers
- **Authentication Logic**: User login/logout and session management
- **Business Logic**: Hospital bed booking and management functions

#### Key Components in `main.py`

```python
# Database Models
- User                 # Patient/user accounts
- Hospitaluser         # Hospital staff accounts  
- Hospitaldata         # Hospital information and bed counts
- Bookingpatient       # Patient booking records
- Trig                 # Trigger/notification system

# Main Route Categories
- Authentication routes (/login, /logout, /signup)
- Booking routes       (/booking, /bookingdetails)
- Hospital routes      (/hospitaldata, /admin)
- File upload routes   (/upload, /download)
- API endpoints        (Various data endpoints)
```

## Templates Directory (`project/templates/`)

### Template Organization

```
templates/
├── base.html                   # Base template with common layout
├── baselogin.html             # Login page base template
├── navbar.html                # Navigation bar component
├── index.html                 # Homepage template
├── userlogin.html             # User login form
├── usersignup.html            # User registration form
├── hospitallogin.html         # Hospital staff login
├── booking.html               # Bed booking form
├── admin.html                 # Admin dashboard
├── hospitaldata.html          # Hospital data display
├── addHosUser.html            # Add hospital user form
├── hedit.html                 # Hospital data editing
├── detials.html               # Booking details view
├── message.html               # Message/notification display
├── chat.html                  # Chat interface
├── trigers.html               # Trigger management
├── view_pdf.html              # PDF viewer
├── bootstap.html              # Bootstrap components demo
└── config.json                # Template configuration
```

### Template Hierarchy

```
base.html                      # Root template
├── baselogin.html            # Login-specific base
│   ├── userlogin.html        # User login
│   ├── usersignup.html       # User registration
│   └── hospitallogin.html    # Hospital login
└── navbar.html               # Navigation component
    ├── index.html            # Homepage
    ├── booking.html          # Booking form
    ├── admin.html            # Admin panel
    ├── hospitaldata.html     # Hospital listing
    └── other pages...
```

## Static Assets Directory (`project/static/`)

### Asset Organization

```
static/
├── assets/                     # Main assets directory
│   ├── css/                   # Stylesheets
│   │   └── style.css          # Main custom stylesheet
│   ├── js/                    # JavaScript files
│   │   └── main.js            # Main JavaScript functionality
│   ├── img/                   # Images and media
│   │   ├── logo.png           # Site logo
│   │   ├── favicon.png        # Site favicon
│   │   ├── about.jpg          # About page image
│   │   ├── features.jpg       # Features section image
│   │   ├── departments-*.jpg  # Department images (1-5)
│   │   ├── doctors/           # Doctor profile images
│   │   │   └── doctors-*.jpg  # Doctor photos (1-4)
│   │   ├── gallery/           # Gallery images
│   │   │   └── gallery-*.jpg  # Gallery photos (1-8)
│   │   ├── slide/             # Slider images
│   │   │   └── slide-*.jpg    # Slider photos (1-3)
│   │   └── testimonials/      # Testimonial images
│   │       └── testimonials-*.jpg  # Testimonial photos (1-5)
│   ├── scss/                  # SCSS source files
│   │   └── Readme.txt         # SCSS documentation
│   └── vendor/                # Third-party libraries
│       ├── animate.css/       # CSS animations
│       ├── aos/               # Animate On Scroll library
│       ├── bootstrap/         # Bootstrap framework
│       ├── bootstrap-icons/   # Bootstrap icon fonts
│       ├── boxicons/          # Box icon fonts
│       ├── fontawesome-free/  # Font Awesome icons
│       ├── glightbox/         # Lightbox gallery
│       ├── php-email-form/    # Email form handler
│       ├── purecounter/       # Counter animations
│       └── swiper/            # Touch slider
```

### Vendor Libraries Details

#### Bootstrap Framework

```
vendor/bootstrap/
├── css/
│   ├── bootstrap.css
│   ├── bootstrap.min.css
│   └── bootstrap.rtl.css
└── js/
    ├── bootstrap.bundle.js
    ├── bootstrap.bundle.min.js
    └── bootstrap.esm.js
```

#### Icon Libraries

```
vendor/bootstrap-icons/
├── bootstrap-icons.css        # Main icon stylesheet
├── bootstrap-icons.min.css    # Minified version
├── bootstrap-icons.json       # Icon metadata
└── fonts/                     # Icon font files

vendor/fontawesome-free/
├── css/                       # FontAwesome stylesheets
└── webfonts/                  # FontAwesome font files

vendor/boxicons/
├── css/                       # Boxicons stylesheets
└── fonts/                     # Boxicons font files
```

## NoSQL Integration Directory (`nosql/`)

### Firebase Components

```
nosql/
├── emergencybooking-31043-firebase-adminsdk-l69k0-98c85bc3f2.json  # Firebase service account
├── fileup.py                  # File upload functionality
└── templates/                 # NoSQL-specific templates
    ├── upload.html            # File upload interface
    └── download.html          # File download interface
```

### File Upload System

The `fileup.py` module handles:

- Firebase Storage integration
- File upload/download operations
- File metadata management
- Storage security and validation

## Bootstrap Templates (`bootstrap/`)

### Template Components

```
bootstrap/
├── inner-page.html            # Inner page template
├── Readme.txt                 # Bootstrap documentation
└── forms/                     # Form templates
    ├── appointment.php        # Appointment booking form
    ├── contact.php            # Contact form
    └── Readme.txt             # Form documentation
```

## Configuration Files

### Environment Configuration

```
.env.example                   # Environment variables template
├── DATABASE_URL               # Database connection string
├── SECRET_KEY                 # Flask secret key
├── FIREBASE_CONFIG            # Firebase configuration
├── MAIL_SERVER               # Email server settings
└── DEBUG                     # Debug mode flag
```

### Dependencies

```
requirements.txt               # Python package dependencies
├── Flask==2.3.3              # Web framework
├── Flask-SQLAlchemy==3.0.5    # Database ORM
├── Flask-Login==0.6.3         # Authentication
├── mysql-connector-python     # MySQL driver
├── firebase-admin             # Firebase SDK
├── Werkzeug==2.3.7           # WSGI utilities
└── Other dependencies...
```

## File Naming Conventions

### Template Files

- **HTML Templates**: Use lowercase with descriptive names
  - `userlogin.html` - User login page
  - `hospitaldata.html` - Hospital data display
  - `addHosUser.html` - Add hospital user form

### Static Assets

- **CSS Files**: Use kebab-case or descriptive names
  - `style.css` - Main stylesheet
  - `bootstrap.min.css` - Bootstrap framework

- **JavaScript Files**: Use descriptive names
  - `main.js` - Main application logic
  - `bootstrap.bundle.js` - Bootstrap functionality

- **Images**: Use descriptive names with numbers for series
  - `logo.png` - Site logo
  - `doctors-1.jpg` - First doctor image
  - `gallery-3.jpg` - Third gallery image

### Python Files

- **Module Files**: Use lowercase with underscores
  - `main.py` - Main application
  - `fileup.py` - File upload module
  - `test.py` - Test utilities

## Directory Structure Best Practices

### Separation of Concerns

1. **Application Logic** (`project/main.py`)
   - Database models
   - Route handlers
   - Business logic
   - Authentication

2. **Presentation Layer** (`project/templates/`)
   - HTML templates
   - Template inheritance
   - Component organization

3. **Static Assets** (`project/static/`)
   - Stylesheets and styling
   - Client-side JavaScript
   - Images and media files
   - Third-party libraries

4. **External Integrations** (`nosql/`)
   - Firebase integration
   - File storage handling
   - External service APIs

### Scalability Considerations

The current structure allows for easy expansion:

- **New Features**: Add new templates in `templates/`
- **API Endpoints**: Extend `main.py` with new routes
- **Static Assets**: Organize in `static/assets/`
- **External Services**: Add modules in appropriate directories

### Development Workflow

```
1. Model Changes        → Update main.py database models
2. Route Development    → Add/modify routes in main.py
3. Template Creation    → Add HTML files in templates/
4. Styling Updates      → Modify CSS in static/assets/css/
5. JavaScript Features  → Update JS in static/assets/js/
6. Testing             → Add tests for new functionality
7. Documentation       → Update relevant .md files
```

## Asset Management

### CSS Organization

```css
/* static/assets/css/style.css */
/* 
Structure:
1. Global styles and resets
2. Typography
3. Layout components
4. Navigation
5. Forms
6. Cards and sections
7. Responsive design
8. Utility classes
*/
```

### JavaScript Organization

```javascript
// static/assets/js/main.js
// 
// Structure:
// 1. Utility functions
// 2. Form validation
// 3. UI interactions
// 4. AJAX requests
// 5. Event listeners
// 6. Initialization code
```

### Image Asset Guidelines

- **Logo**: `logo.png` - Main site branding
- **Icons**: Use Bootstrap Icons or Font Awesome
- **Photos**: Organize by category (doctors/, gallery/, etc.)
- **Optimization**: Compress images for web delivery
- **Responsive**: Provide multiple sizes when needed

## Security Considerations

### File Organization Security

1. **Sensitive Files**: Keep outside web root
   - Firebase credentials in project root
   - Environment files (.env) not in static/

2. **Access Control**: Restrict file permissions
   - Configuration files: 600 (read/write owner only)
   - Executable files: 755 (read/execute for others)
   - Web assets: 644 (read for others)

3. **Version Control**: Use .gitignore properly
   - Exclude sensitive credentials
   - Exclude temporary files
   - Include necessary configuration templates

## Maintenance and Updates

### Regular Maintenance Tasks

1. **Dependency Updates**
   - Update requirements.txt
   - Test compatibility
   - Security patches

2. **Asset Optimization**
   - Compress images
   - Minify CSS/JavaScript
   - Remove unused files

3. **Template Cleanup**
   - Remove unused templates
   - Update common components
   - Optimize template inheritance

4. **Documentation Updates**
   - Keep structure docs current
   - Update API documentation
   - Maintain setup instructions

### Migration Considerations

When restructuring the project:

1. **Backup Current State**: Full project backup
2. **Plan Migration**: Document structure changes
3. **Update References**: Fix all file paths
4. **Test Thoroughly**: Verify all functionality
5. **Update Documentation**: Reflect new structure

This structure provides a solid foundation for the Emergency Hospital Bed Booking System while maintaining flexibility for future enhancements and scalability needs.
