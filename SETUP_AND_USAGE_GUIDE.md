# SurveyPlane - Setup and Usage Guide

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation Methods](#installation-methods)
3. [Environment Setup](#environment-setup)
4. [Database Configuration](#database-configuration)
5. [Running the Application](#running-the-application)
6. [API Usage Guide](#api-usage-guide)
7. [Development Workflow](#development-workflow)
8. [Deployment Options](#deployment-options)
9. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites
- Python 3.12.4 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### 30-Second Setup
```bash
# Clone the repository
git clone https://github.com/husseinahmad7/SurveyPlane.git
cd SurveyPlane

# Install dependencies
pip install pipenv
pipenv install

# Setup database
pipenv run migrate

# Create superuser (optional)
pipenv run createsuperuser

# Start development server
pipenv run runserver
```

**🎉 Your SurveyPlane instance is now running at `http://localhost:8000`**

## 🛠️ Installation Methods

### Method 1: Using Pipenv (Recommended)

#### Step 1: Clone and Navigate
```bash
git clone <repository-url>
cd SurveyPlane
```

#### Step 2: Install Pipenv
```bash
# On Windows
pip install pipenv

# On macOS
brew install pipenv

# On Ubuntu/Debian
sudo apt install pipenv
```

#### Step 3: Install Dependencies
```bash
# Install all dependencies
pipenv install

# Install development dependencies (optional)
pipenv install --dev
```

#### Step 4: Activate Virtual Environment
```bash
# Activate the virtual environment
pipenv shell

# Or run commands with pipenv run
pipenv run python manage.py --help
```

### Method 2: Using Virtual Environment

#### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python -m venv surveyplane_env

# Activate virtual environment
# On Windows
surveyplane_env\Scripts\activate
# On macOS/Linux
source surveyplane_env/bin/activate
```

#### Step 2: Install Dependencies
```bash
# Install from requirements (if available)
pip install -r requirements.txt

# Or install manually
pip install django==5.1.2
pip install djangorestframework
pip install django-rest-authemail
pip install django-filter==24.2
pip install django-environ
pip install numpy
pip install reportlab
pip install django-cors-headers
pip install psycopg[binary]
```

### Method 3: Using Docker (Advanced)

#### Step 1: Create Dockerfile
```dockerfile
FROM python:3.12.4

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### Step 2: Build and Run
```bash
# Build Docker image
docker build -t surveyplane .

# Run container
docker run -p 8000:8000 surveyplane
```

## ⚙️ Environment Setup

### Environment Variables

Create a `.env` file in the project root as `example.env`:

```env
# Basic Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration (Optional)
DATABASE_URL=postgresql://user:password@localhost:5432/surveyplane

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
AUTHEMAIL_DEFAULT_EMAIL_FROM=noreply@yoursite.com
AUTHEMAIL_DEFAULT_EMAIL_BCC=admin@yoursite.com

# Production Settings
ALLOWED_HOSTS=localhost,127.0.0.1,yoursite.com
```

### Development vs Production

#### Development Settings
```env
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Production Settings
```env
DEBUG=False
DATABASE_URL=postgresql://user:password@host:port/database
ALLOWED_HOSTS=yoursite.com,www.yoursite.com
SECRET_KEY=your-very-secure-secret-key
```

## 🗄️ Database Configuration

### SQLite (Default - Development)
```bash
# Apply migrations
pipenv run migrate

# Create superuser
pipenv run createsuperuser
```

### PostgreSQL (Production)

#### Step 1: Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

#### Step 2: Create Database
```sql
-- Connect to PostgreSQL
sudo -u postgres psql

-- Create database and user
CREATE DATABASE surveyplane;
CREATE USER surveyplane_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE surveyplane TO surveyplane_user;
```

#### Step 3: Update Environment
```env
DATABASE_URL=postgresql://surveyplane_user:your_password@localhost:5432/surveyplane
```

#### Step 4: Migrate
```bash
pipenv run migrate
```

## 🏃‍♂️ Running the Application

### Development Server

#### Using Pipenv
```bash
# Start development server
pipenv run runserver

# Start on specific port
pipenv run runserver 8080

# Start on all interfaces
pipenv run runserver 0.0.0.0:8000
```

#### Using Django Management Commands
```bash
# Activate virtual environment first
pipenv shell

# Then run Django commands
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### Available Management Commands

#### Database Operations
```bash
pipenv run makemigrations    # Create new migrations
pipenv run migrate          # Apply migrations
pipenv run check           # Check for issues
```

#### User Management
```bash
pipenv run createsuperuser  # Create admin user
pipenv run shell           # Django shell
```

#### Development Tools
```bash
pipenv run test            # Run tests
pipenv run testWa          # Run tests with warnings
```

### Production Server

#### Using Gunicorn
```bash
# Install gunicorn
pipenv install gunicorn

# Run with gunicorn
pipenv run gunicorn SurveyPlane.wsgi:application
```

#### Using uWSGI
```bash
# Install uwsgi
pipenv install uwsgi

# Run with uwsgi
pipenv run uwsgi --http :8000 --module SurveyPlane.wsgi
```

## 📡 API Usage Guide

### Authentication

#### 1. Register User
```bash
curl -X POST http://localhost:8000/accounts/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

#### 2. Verify Email (if required)
```bash
curl -X POST http://localhost:8000/accounts/signup/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "code": "verification-code-from-email"
  }'
```

#### 3. Login
```bash
curl -X POST http://localhost:8000/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Survey Operations

#### 1. Create Survey
```bash
curl -X POST http://localhost:8000/Survey/surveys/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token" \
  -d '{
    "title": "Customer Satisfaction Survey",
    "description": "Help us improve our services",
    "closes_at": "2024-12-31T23:59:59Z",
    "respondent_auth_requirement": "QUICK",
    "questions": [
      {
        "question_text": "How satisfied are you?",
        "question_type": "rating",
        "required": true,
        "order": 1,
        "settings": {
          "min_value": 1,
          "max_value": 5
        }
      }
    ]
  }'
```

#### 2. List Surveys with Filters
```bash
# Get active surveys with NONE authentication
curl "http://localhost:8000/Survey/surveys/?is_active=true&respondent_auth_requirement=NONE"

# Search surveys
curl "http://localhost:8000/Survey/surveys/?search=customer&ordering=title"

# Get surveys by creator
curl "http://localhost:8000/Survey/surveys/?creator=1&has_responses=true"
```

#### 3. Submit Response
```bash
curl -X POST http://localhost:8000/Survey/responses/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-auth-token" \
  -d '{
    "survey": 1,
    "answers": [
      {
        "question": 1,
        "value": "4"
      }
    ]
  }'
```

#### 4. Export to PDF
```bash
# Export survey responses
curl -H "Authorization: Token your-auth-token" \
  "http://localhost:8000/Survey/surveys/1/responses/export/" \
  -o survey_responses.pdf

# Export with statistics
curl -H "Authorization: Token your-auth-token" \
  "http://localhost:8000/Survey/surveys/1/responses/export/?include_stats=true" \
  -o survey_responses_with_stats.pdf
```

### Response Formats

#### Success Response
```json
{
  "id": 1,
  "title": "Customer Satisfaction Survey",
  "description": "Help us improve our services",
  "creator": 1,
  "created_at": "2024-07-01T10:00:00Z",
  "closes_at": "2024-12-31T23:59:59Z",
  "is_active": true,
  "respondent_auth_requirement": "QUICK",
  "is_closed": false,
  "questions": [...]
}
```

#### Error Response
```json
{
  "error": "Survey not found",
  "detail": "No Survey matches the given query."
}
```

## 💻 Development Workflow

### Setting Up Development Environment

#### 1. Clone and Setup
```bash
git clone <repository-url>
cd SurveyPlane
pipenv install --dev
pipenv shell
```

#### 2. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

#### 3. Load Sample Data (Optional)
```bash
# Create sample surveys and responses
python manage.py shell
# Then run sample data creation scripts
```

### Development Commands

#### Running Tests
```bash
# Run all tests
pipenv run test

# Run specific app tests
pipenv run test Survey

# Run with coverage
pipenv install coverage
pipenv run coverage run manage.py test
pipenv run coverage report
```

#### Code Quality
```bash
# Check code style
pipenv install flake8
pipenv run flake8 .

# Format code
pipenv install black
pipenv run black .
```

### Making Changes

#### 1. Model Changes
```bash
# After modifying models
python manage.py makemigrations
python manage.py migrate
```

#### 2. Adding Dependencies
```bash
# Add new package
pipenv install package-name

# Add development dependency
pipenv install package-name --dev
```

#### 3. Static Files
```bash
# Collect static files
python manage.py collectstatic
```

## 🚀 Deployment Options

### Option 1: PythonAnywhere (Current Production)

#### 1. Upload Code
```bash
# Zip your project
zip -r surveyplane.zip SurveyPlane/

# Upload to PythonAnywhere and extract
```

#### 2. Setup Virtual Environment
```bash
# In PythonAnywhere console
mkvirtualenv --python=/usr/bin/python3.12 surveyplane
pip install -r requirements.txt
```

#### 3. Configure Web App
- Set source code path: `/home/yourusername/SurveyPlane`
- Set working directory: `/home/yourusername/SurveyPlane`
- Edit WSGI file to point to your Django app

### Option 2: Heroku

#### 1. Prepare for Heroku
```bash
# Create Procfile
echo "web: gunicorn SurveyPlane.wsgi" > Procfile

# Create runtime.txt
echo "python-3.12.4" > runtime.txt
```

#### 2. Deploy
```bash
# Install Heroku CLI and login
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
```

### Option 3: DigitalOcean/AWS

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade

# Install Python and dependencies
sudo apt install python3.12 python3-pip nginx postgresql
```

#### 2. Application Setup
```bash
# Clone and setup application
git clone <repository-url>
cd SurveyPlane
pip install pipenv
pipenv install
```

#### 3. Configure Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/SurveyPlane/static/;
    }
    
    location /media/ {
        alias /path/to/SurveyPlane/media/;
    }
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database status
python manage.py dbshell

# Reset database
python manage.py flush
python manage.py migrate
```

#### 2. Permission Errors
```bash
# Fix file permissions
chmod +x manage.py
chmod -R 755 media/
```

#### 3. Module Import Errors
```bash
# Reinstall dependencies
pipenv install --dev
pipenv clean
```

#### 4. Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --clear
```

### Debug Mode

#### Enable Debug Mode
```env
DEBUG=True
```

#### View Debug Information
- Visit `http://localhost:8000/admin/` for admin interface
- Check Django debug toolbar (if installed)
- Review console output for errors

### Performance Issues

#### Database Optimization
```python
# Add database indexes
python manage.py dbshell
CREATE INDEX idx_survey_creator ON Survey_survey(creator_id);
```

#### Memory Usage
```bash
# Monitor memory usage
pip install memory-profiler
python -m memory_profiler manage.py runserver
```

### Getting Help

#### 1. Check Logs
```bash
# View Django logs
tail -f /path/to/logs/django.log

# Check system logs
journalctl -u your-service-name
```

#### 2. Debug Shell
```bash
# Django shell for debugging
python manage.py shell

# Database shell
python manage.py dbshell
```

#### 3. Test API Endpoints
```bash
# Test with curl
curl -v http://localhost:8000/Survey/surveys/

# Test with httpie
pip install httpie
http GET localhost:8000/Survey/surveys/
```

## 📚 Additional Resources

### Documentation Files
- **`PROJECT_DOCUMENTATION.md`** - Complete project overview and technical details
- **`SURVEY_FILTERS_DOCUMENTATION.md`** - Comprehensive filtering and search guide
- **`SURVEY_FILTERS_SUMMARY.md`** - Quick reference for filtering features

### Test Scripts
- **`test_pdf_export.py`** - Test PDF export functionality
- **`test_survey_filters.py`** - Test filtering capabilities
- **`test_filter_integration.py`** - Integration testing

### Configuration Files
- **`Pipfile`** - Dependency management
- **`docker-compose.yml`** - Docker configuration
- **`.env.example`** - Environment variables template

## 🎯 Quick Reference

### Essential Commands
```bash
# Start development server
pipenv run runserver

# Apply database migrations
pipenv run migrate

# Create admin user
pipenv run createsuperuser

# Run tests
pipenv run test

# Export survey to PDF
curl -H "Authorization: Token TOKEN" \
  "http://localhost:8000/Survey/surveys/1/responses/export/" \
  -o survey.pdf
```

### Key URLs
- **API Base:** `http://localhost:8000/`
- **Admin Panel:** `http://localhost:8000/admin/`
- **Surveys API:** `http://localhost:8000/Survey/surveys/`
- **Authentication:** `http://localhost:8000/accounts/`
- **Production:** `https://surveyplane.pythonanywhere.com/`

---

## 📞 Support

For additional help:
- Check the project documentation files
- Review error logs in console output
- Test with minimal configuration
- Use the Django admin panel for debugging
- Contact the development team

**Happy surveying with SurveyPlane! 🎉**
