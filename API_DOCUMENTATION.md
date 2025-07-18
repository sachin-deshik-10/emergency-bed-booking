# API Documentation

## Emergency Hospital Bed Booking System API

This document describes the REST API endpoints available in the Emergency Hospital Bed Booking System.

### Base URL

```
http://localhost:5000
```

### Authentication

The system uses Flask-Login for session-based authentication. Users must be logged in to access protected endpoints.

## Public Endpoints

### Home Page

- **GET** `/`
- **Description**: Displays the home page
- **Authentication**: Not required
- **Response**: HTML page

### User Registration

- **GET/POST** `/signup`
- **Description**: User registration form and processing
- **Authentication**: Not required
- **Request Body** (POST):

```json
{
  "email": "user@example.com",
  "dob": "1990-01-01",
  "password": "password123"
}
```

### User Login

- **GET/POST** `/login`
- **Description**: User login form and authentication
- **Authentication**: Not required
- **Request Body** (POST):

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Hospital Login

- **GET/POST** `/hospitallogin`
- **Description**: Hospital staff login
- **Authentication**: Not required
- **Request Body** (POST):

```json
{
  "email": "hospital@example.com",
  "password": "hospitalpass123"
}
```

### Admin Login

- **GET/POST** `/admin`
- **Description**: Administrator login
- **Authentication**: Not required
- **Request Body** (POST):

```json
{
  "username": "admin",
  "password": "admin"
}
```

## Protected Endpoints

### Bed Booking

- **GET/POST** `/slotbooking`
- **Description**: View available beds and book a slot
- **Authentication**: Required (User/Patient)
- **Request Body** (POST):

```json
{
  "email": "patient@example.com",
  "bedtype": "NormalBed",
  "hcode": "HOS001",
  "spo2": 95,
  "pname": "John Doe",
  "pphone": "1234567890",
  "paddress": "123 Main St"
}
```

- **Response** (Success):

```json
{
  "status": "success",
  "message": "Slot is Booked kindly Visit Hospital for Further Procedure",
  "booking_id": 123
}
```

### Patient Details

- **GET** `/pdetails`
- **Description**: View patient booking details
- **Authentication**: Required (Hospital Staff)
- **Response**:

```json
{
  "patient": {
    "id": 1,
    "pname": "John Doe",
    "email": "patient@example.com",
    "bedtype": "NormalBed",
    "hcode": "HOS001",
    "spo2": 95,
    "pphone": "1234567890",
    "paddress": "123 Main St"
  }
}
```

### Hospital Data Management

- **GET/POST** `/addhospitalinfo`
- **Description**: Add or update hospital information
- **Authentication**: Required (Hospital Staff)
- **Request Body** (POST):

```json
{
  "hcode": "HOS001",
  "hname": "City General Hospital",
  "normalbed": 50,
  "hicubeds": 10,
  "icubeds": 8,
  "ventbeds": 5
}
```

### Edit Hospital Data

- **GET/POST** `/hedit/<id>`
- **Description**: Edit specific hospital record
- **Authentication**: Required (Hospital Staff)
- **Parameters**:
  - `id`: Hospital record ID
- **Request Body** (POST):

```json
{
  "hcode": "HOS001",
  "hname": "Updated Hospital Name",
  "normalbed": 55,
  "hicubeds": 12,
  "icubeds": 10,
  "ventbeds": 6
}
```

### Delete Hospital Data

- **POST** `/hdelete/<id>`
- **Description**: Delete hospital record
- **Authentication**: Required (Hospital Staff)
- **Parameters**:
  - `id`: Hospital record ID

### File Upload

- **POST** `/upload`
- **Description**: Upload medical documents
- **Authentication**: Required
- **Content-Type**: `multipart/form-data`
- **Request Body**:

```
file: [Binary file data]
```

- **Response**:

```json
{
  "status": "success",
  "download_url": "https://storage.googleapis.com/bucket/filename.pdf"
}
```

### View PDF Documents

- **GET** `/view_pdf`
- **Description**: View uploaded PDF documents
- **Authentication**: Required
- **Response**: HTML page with embedded PDF viewer

### Operations Log

- **GET** `/trigers`
- **Description**: View system operation logs
- **Authentication**: Not required
- **Response**: HTML page with operations table

## Administrative Endpoints

### Add Hospital User

- **GET/POST** `/addHospitalUser`
- **Description**: Add new hospital user account
- **Authentication**: Required (Admin)
- **Request Body** (POST):

```json
{
  "hcode": "HOS002",
  "email": "newhospital@example.com",
  "password": "hospitalpass456"
}
```

### Database Test

- **GET** `/test`
- **Description**: Test database connectivity
- **Authentication**: Not required
- **Response**:

```json
{
  "status": "success",
  "message": "Database connection successful"
}
```

## Logout Endpoints

### User Logout

- **GET** `/logout`
- **Description**: Log out current user
- **Authentication**: Required

### Admin Logout

- **GET** `/logoutadmin`
- **Description**: Log out admin user
- **Authentication**: Required (Admin)

## Error Responses

### Common Error Codes

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "status": "error",
  "message": "Descriptive error message",
  "code": "ERROR_CODE"
}
```

## Data Models

### User Model

```json
{
  "id": 1,
  "email": "user@example.com",
  "dob": "1990-01-01"
}
```

### Hospital User Model

```json
{
  "id": 1,
  "hcode": "HOS001",
  "email": "hospital@example.com"
}
```

### Hospital Data Model

```json
{
  "id": 1,
  "hcode": "HOS001",
  "hname": "City General Hospital",
  "normalbed": 50,
  "hicubed": 10,
  "icubed": 8,
  "vbed": 5
}
```

### Booking Patient Model

```json
{
  "id": 1,
  "bedtype": "NormalBed",
  "hcode": "HOS001",
  "spo2": 95,
  "pname": "John Doe",
  "pphone": "1234567890",
  "paddress": "123 Main St",
  "email": "patient@example.com"
}
```

### Operation Log Model

```json
{
  "id": 1,
  "hcode": "HOS001",
  "normalbed": 49,
  "hicubed": 10,
  "icubed": 8,
  "vbed": 5,
  "querys": "Bed Booked",
  "date": "2024-01-15 10:30:00"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## CORS

Cross-Origin Resource Sharing (CORS) is not configured. Configure as needed for frontend applications.

## Security Considerations

1. **HTTPS**: Use HTTPS in production
2. **Input Validation**: All inputs are validated server-side
3. **SQL Injection**: Protected by SQLAlchemy ORM
4. **Authentication**: Session-based authentication with secure cookies
5. **File Upload**: Validate file types and sizes

## SDK/Client Libraries

Currently, no official SDK is available. Use standard HTTP clients to interact with the API.

## Postman Collection

A Postman collection is available for testing the API endpoints. Import the collection file `postman_collection.json` into Postman.

## Changelog

### Version 1.0.0

- Initial API implementation
- Basic CRUD operations for hospitals and bookings
- User authentication system
- File upload functionality
