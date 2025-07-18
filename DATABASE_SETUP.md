# Database Setup Guide

This guide will help you set up the database for the Emergency Hospital Bed Booking System.

## Prerequisites

- MySQL 8.0 or higher
- Python 3.8 or higher
- MySQL client tools

## Database Creation

### 1. Connect to MySQL

```bash
mysql -u root -p
```

### 2. Create Database

```sql
CREATE DATABASE emergency_bed CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Create Database User (Optional but Recommended)

```sql
CREATE USER 'emergency_user'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON emergency_bed.* TO 'emergency_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Use the Database

```sql
USE emergency_bed;
```

## Table Schemas

### Users Table (Patients)

```sql
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(50) NOT NULL,
    dob VARCHAR(1000),
    UNIQUE KEY unique_email (email)
);
```

### Hospital Users Table (Hospital Staff)

```sql
CREATE TABLE hospitaluser (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hcode VARCHAR(20) NOT NULL,
    email VARCHAR(50) NOT NULL,
    password VARCHAR(1000) NOT NULL,
    UNIQUE KEY unique_email (email),
    INDEX idx_hcode (hcode)
);
```

### Hospital Data Table

```sql
CREATE TABLE hospitaldata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hcode VARCHAR(20) NOT NULL UNIQUE,
    hname VARCHAR(100) NOT NULL,
    normalbed INT DEFAULT 0,
    hicubed INT DEFAULT 0,
    icubed INT DEFAULT 0,
    vbed INT DEFAULT 0,
    INDEX idx_hcode (hcode)
);
```

### Patient Bookings Table

```sql
CREATE TABLE bookingpatient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bedtype VARCHAR(100) NOT NULL,
    hcode VARCHAR(20) NOT NULL,
    spo2 INT,
    pname VARCHAR(100) NOT NULL,
    pphone VARCHAR(100) NOT NULL,
    paddress VARCHAR(100) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hcode (hcode),
    INDEX idx_email (email),
    FOREIGN KEY (hcode) REFERENCES hospitaldata(hcode) ON DELETE CASCADE
);
```

### Operations Log Table

```sql
CREATE TABLE trig (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hcode VARCHAR(20) NOT NULL,
    normalbed INT,
    hicubed INT,
    icubed INT,
    vbed INT,
    querys VARCHAR(50),
    date VARCHAR(50),
    INDEX idx_hcode (hcode),
    INDEX idx_date (date)
);
```

## Sample Data

### Insert Sample Hospitals

```sql
INSERT INTO hospitaldata (hcode, hname, normalbed, hicubed, icubed, vbed) VALUES
('HOS001', 'City General Hospital', 50, 15, 10, 5),
('HOS002', 'Metro Medical Center', 75, 20, 15, 8),
('HOS003', 'Central Emergency Hospital', 100, 25, 20, 12),
('HOS004', 'Regional Healthcare', 60, 18, 12, 6),
('HOS005', 'Community Hospital', 40, 10, 8, 4);
```

### Insert Sample Hospital Users

```sql
INSERT INTO hospitaluser (hcode, email, password) VALUES
('HOS001', 'admin@citygeneral.com', 'scrypt:32768:8:1$encrypted_password_here'),
('HOS002', 'admin@metromedical.com', 'scrypt:32768:8:1$encrypted_password_here'),
('HOS003', 'admin@centralemergency.com', 'scrypt:32768:8:1$encrypted_password_here');
```

*Note: Replace `encrypted_password_here` with actual hashed passwords*

### Insert Sample Users

```sql
INSERT INTO user (email, dob) VALUES
('patient1@example.com', '1990-01-15'),
('patient2@example.com', '1985-03-22'),
('patient3@example.com', '1992-07-08');
```

## Database Triggers (Optional)

### Automatic Operation Logging

```sql
DELIMITER //

CREATE TRIGGER log_bed_update 
AFTER UPDATE ON hospitaldata
FOR EACH ROW
BEGIN
    INSERT INTO trig (hcode, normalbed, hicubed, icubed, vbed, querys, date)
    VALUES (NEW.hcode, NEW.normalbed, NEW.hicubed, NEW.icubed, NEW.vbed, 
            'Bed Count Updated', NOW());
END//

CREATE TRIGGER log_booking_insert 
AFTER INSERT ON bookingpatient
FOR EACH ROW
BEGIN
    INSERT INTO trig (hcode, normalbed, hicubed, icubed, vbed, querys, date)
    SELECT NEW.hcode, normalbed, hicubed, icubed, vbed, 
           CONCAT('Bed Booked - ', NEW.bedtype), NOW()
    FROM hospitaldata WHERE hcode = NEW.hcode;
END//

DELIMITER ;
```

## Views for Reporting

### Available Beds Summary

```sql
CREATE VIEW available_beds_summary AS
SELECT 
    hcode,
    hname,
    normalbed,
    hicubed,
    icubed,
    vbed,
    (normalbed + hicubed + icubed + vbed) as total_beds
FROM hospitaldata
ORDER BY total_beds DESC;
```

### Booking Statistics

```sql
CREATE VIEW booking_statistics AS
SELECT 
    h.hcode,
    h.hname,
    COUNT(b.id) as total_bookings,
    COUNT(CASE WHEN b.bedtype = 'NormalBed' THEN 1 END) as normal_bookings,
    COUNT(CASE WHEN b.bedtype = 'HICUBed' THEN 1 END) as hicu_bookings,
    COUNT(CASE WHEN b.bedtype = 'ICUBed' THEN 1 END) as icu_bookings,
    COUNT(CASE WHEN b.bedtype = 'VENTILATORBed' THEN 1 END) as ventilator_bookings
FROM hospitaldata h
LEFT JOIN bookingpatient b ON h.hcode = b.hcode
GROUP BY h.hcode, h.hname;
```

## Indexes for Performance

```sql
-- Additional indexes for better performance
CREATE INDEX idx_booking_bedtype ON bookingpatient(bedtype);
CREATE INDEX idx_booking_created ON bookingpatient(created_at);
CREATE INDEX idx_trig_querys ON trig(querys);
CREATE INDEX idx_hospital_name ON hospitaldata(hname);
```

## Backup and Restore

### Create Backup

```bash
mysqldump -u root -p emergency_bed > emergency_bed_backup.sql
```

### Restore from Backup

```bash
mysql -u root -p emergency_bed < emergency_bed_backup.sql
```

## Python Database Initialization

If you prefer to create tables using the Flask application:

```python
from project.main import app, dbsql

with app.app_context():
    # Create all tables
    dbsql.create_all()
    print("Database tables created successfully!")
```

## Environment Configuration

Update your `.env` file with the database connection details:

```env
DATABASE_URL=mysql+mysqldb://emergency_user:secure_password_here@localhost/emergency_bed
MYSQL_HOST=localhost
MYSQL_USER=emergency_user
MYSQL_PASSWORD=secure_password_here
MYSQL_DATABASE=emergency_bed
```

## Security Considerations

1. **Use Strong Passwords**: Ensure database user passwords are strong
2. **Limit Privileges**: Grant only necessary privileges to application users
3. **Regular Backups**: Set up automated backup schedules
4. **SSL Connections**: Configure SSL for database connections in production
5. **Firewall Rules**: Restrict database access to application servers only

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if MySQL service is running
   - Verify connection parameters
   - Check firewall settings

2. **Access Denied**
   - Verify username and password
   - Check user privileges
   - Ensure user can connect from the specified host

3. **Table Doesn't Exist**
   - Run database initialization scripts
   - Check if you're connected to the correct database

### Useful Commands

```sql
-- Check database status
SHOW DATABASES;
SHOW TABLES;
DESCRIBE table_name;

-- Check user privileges
SHOW GRANTS FOR 'emergency_user'@'localhost';

-- Check table sizes
SELECT 
    table_name,
    round(((data_length + index_length) / 1024 / 1024), 2) as 'Size in MB'
FROM information_schema.tables 
WHERE table_schema = 'emergency_bed';
```

## Performance Tuning

### MySQL Configuration Recommendations

Add to your MySQL configuration file (`my.cnf` or `my.ini`):

```ini
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200
query_cache_size = 64M
tmp_table_size = 64M
max_heap_table_size = 64M
```

### Query Optimization

1. Use EXPLAIN to analyze query performance
2. Ensure proper indexing on frequently queried columns
3. Use LIMIT clauses for large result sets
4. Consider partitioning for very large tables

## Monitoring

### Key Metrics to Monitor

1. Connection count
2. Query execution time
3. Table sizes
4. Index usage
5. Lock contention

### Monitoring Queries

```sql
-- Show current connections
SHOW PROCESSLIST;

-- Show slow queries
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- Show table sizes
SELECT 
    table_name,
    table_rows,
    data_length,
    index_length
FROM information_schema.tables 
WHERE table_schema = 'emergency_bed';
```
