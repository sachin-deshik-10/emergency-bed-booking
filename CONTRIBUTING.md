# Contributing to Emergency Hospital Bed Booking System

Thank you for your interest in contributing to the Emergency Hospital Bed Booking System! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

1. **Bug Description**: Clear and concise description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - OS version
   - Python version
   - Browser (if applicable)
   - Database version
6. **Screenshots**: If applicable, add screenshots to help explain the problem

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

1. **Enhancement Description**: Clear description of the proposed feature
2. **Use Case**: Why this enhancement would be useful
3. **Implementation Ideas**: Any thoughts on how it could be implemented
4. **Alternatives**: Alternative solutions you've considered

### Pull Request Process

1. **Fork the Repository**

   ```bash
   git clone https://github.com/sachin-deshik-10/emergency-bed-booking.git
   cd emergency-bed-booking
   ```

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/your-bugfix-name
   ```

3. **Make Your Changes**
   - Follow the coding standards outlined below
   - Write or update tests as needed
   - Update documentation if necessary

4. **Test Your Changes**

   ```bash
   # Run tests
   python -m pytest tests/
   
   # Test the application manually
   python project/main.py
   ```

5. **Commit Your Changes**

   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

6. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Provide a clear title and description
   - Reference any related issues

## 📝 Coding Standards

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable and function names

**Example:**

```python
# Good
def calculate_available_beds(hospital_code, bed_type):
    """Calculate available beds for a specific hospital and bed type."""
    hospital = Hospitaldata.query.filter_by(hcode=hospital_code).first()
    return hospital.get_bed_count(bed_type)

# Avoid
def calc(hc, bt):
    h = Hospitaldata.query.filter_by(hcode=hc).first()
    return h.get_bed_count(bt)
```

### HTML/CSS Guidelines

- Use semantic HTML5 elements
- Follow Bootstrap conventions
- Use consistent indentation (2 spaces)
- Include appropriate ARIA labels for accessibility

### JavaScript Standards

- Use ES6+ features when possible
- Use meaningful variable names
- Include comments for complex logic
- Follow consistent formatting

### Database Guidelines

- Use descriptive table and column names
- Include appropriate indexes
- Follow naming conventions:
  - Tables: lowercase with underscores (e.g., `hospital_data`)
  - Columns: lowercase with underscores (e.g., `bed_count`)

## 🧪 Testing Guidelines

### Writing Tests

- Write unit tests for new functions
- Include integration tests for API endpoints
- Test both success and failure scenarios
- Use descriptive test names

**Example:**

```python
def test_bed_booking_with_valid_data():
    """Test successful bed booking with all required fields."""
    # Test implementation

def test_bed_booking_with_invalid_hospital_code():
    """Test bed booking failure with non-existent hospital code."""
    # Test implementation
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_booking.py

# Run with coverage
python -m pytest --cov=project tests/
```

## 📚 Documentation

### Code Documentation

- Include docstrings for all functions and classes
- Use clear and concise comments
- Document complex algorithms or business logic

**Example:**

```python
def book_hospital_bed(patient_data, hospital_code, bed_type):
    """
    Book a hospital bed for a patient.
    
    Args:
        patient_data (dict): Patient information including name, phone, address
        hospital_code (str): Unique hospital identifier
        bed_type (str): Type of bed (NormalBed, ICUBed, etc.)
    
    Returns:
        dict: Booking confirmation with booking ID and details
    
    Raises:
        ValueError: If hospital code doesn't exist
        RuntimeError: If no beds are available
    """
```

### API Documentation

- Document all API endpoints
- Include request/response examples
- Specify required parameters and data types

## 🔍 Code Review Process

### What We Look For

1. **Functionality**: Does the code work as intended?
2. **Code Quality**: Is the code readable and maintainable?
3. **Testing**: Are there adequate tests?
4. **Security**: Are there any security vulnerabilities?
5. **Performance**: Is the code efficient?
6. **Documentation**: Is the code properly documented?

### Review Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New features have appropriate tests
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Performance considerations addressed
- [ ] Error handling is appropriate

## 🎯 Development Priorities

### High Priority

- Security enhancements
- Performance optimizations
- Bug fixes
- Accessibility improvements

### Medium Priority

- New features
- UI/UX improvements
- Code refactoring
- Additional testing

### Low Priority

- Code cleanup
- Documentation improvements
- Development tooling

## 🛠️ Development Environment Setup

### Required Tools

1. **Python 3.8+**
2. **MySQL 8.0+**
3. **Git**
4. **Code Editor** (VS Code, PyCharm, etc.)

### Optional Tools

1. **Docker** (for containerized development)
2. **Postman** (for API testing)
3. **MySQL Workbench** (for database management)

### Environment Configuration

1. **Clone and Setup**

   ```bash
   git clone https://github.com/yourusername/emergency-bed-booking.git
   cd emergency-bed-booking
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**

   ```bash
   mysql -u root -p
   CREATE DATABASE emergency_bed_dev;
   ```

3. **Environment Variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize Database**

   ```python
   python -c "from project.main import dbsql; dbsql.create_all()"
   ```

## 📋 Project Structure

```
emergency-bed-booking/
├── project/
│   ├── main.py                 # Main application file
│   ├── static/                 # Static assets
│   │   ├── assets/
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   ├── img/
│   │   │   └── vendor/
│   └── templates/              # HTML templates
├── tests/                      # Test files
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── README.md                   # Project README
├── CONTRIBUTING.md             # This file
└── .env.example               # Environment variables template
```

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority-high`: High priority issue
- `priority-medium`: Medium priority issue
- `priority-low`: Low priority issue

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: [your-email@example.com]
- **Discord/Slack**: [If you have a community chat]

## 🎉 Recognition

Contributors will be recognized in:

- README.md file
- Release notes
- Contributors page (if applicable)

Thank you for helping improve the Emergency Hospital Bed Booking System! 🏥✨
