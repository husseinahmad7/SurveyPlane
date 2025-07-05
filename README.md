# 📊 SurveyPlane

> **A comprehensive survey management platform built with Django REST Framework**

[![Python](https://img.shields.io/badge/Python-3.12.4-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-Latest-orange.svg)](https://django-rest-framework.org)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://surveyplane.pythonanywhere.com)

## 🎯 Overview

**SurveyPlane** is a powerful, feature-rich survey management platform that enables users to create, distribute, and analyze surveys with advanced capabilities including multiple question types, flexible authentication, real-time analytics, and professional PDF exports.

### ✨ Key Features

- 🔐 **Flexible Authentication** - Three-tier authentication system (None, Quick, Full)
- 📝 **Multiple Question Types** - Text, Single Choice, Multiple Choice, Rating, File Upload
- 📊 **Advanced Analytics** - Real-time statistics, correlation analysis, trend analysis
- 📄 **PDF Export** - Professional PDF reports with optimized layouts
- 🔍 **Comprehensive Filtering** - 15+ filter options with search capabilities
- 📁 **File Management** - Secure file uploads with validation
- 🌐 **RESTful API** - Complete REST API with comprehensive documentation
- 🚀 **Production Ready** - Deployed and running at [surveyplane.pythonanywhere.com](https://surveyplane.pythonanywhere.com)

## 🚀 Quick Start

### Prerequisites
- Python 3.12.4+
- pip and pipenv

### 30-Second Setup
```bash
# Clone the repository
git clone <repository-url>
cd SurveyPlane

# Install dependencies
pip install pipenv
pipenv install

# Setup database and run
pipenv run migrate
pipenv run runserver
```

**🎉 Access your SurveyPlane instance at `http://localhost:8000`**

## 📚 Documentation

### 📖 Complete Guides
- **[📋 PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)** - Complete project overview, architecture, and technical details
- **[🛠️ SETUP_AND_USAGE_GUIDE.md](SETUP_AND_USAGE_GUIDE.md)** - Comprehensive setup, installation, and usage instructions
- **[🔍 SURVEY_FILTERS_DOCUMENTATION.md](SURVEY_FILTERS_DOCUMENTATION.md)** - Complete filtering and search capabilities guide

### 🎯 Quick References
- **[📊 SURVEY_FILTERS_SUMMARY.md](SURVEY_FILTERS_SUMMARY.md)** - Quick reference for filtering features
- **[🧪 Test Scripts](.)** - Various test scripts for functionality verification

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django API    │    │   Database      │
│   (External)    │◄──►│   REST Server   │◄──►│   SQLite/       │
│                 │    │                 │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   File Storage  │
                       │   (Media Files) │
                       └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Django 5.1.2** - Web framework
- **Django REST Framework** - API framework
- **django-rest-authemail** - Authentication system
- **django-filter 24.2** - Advanced filtering
- **NumPy** - Statistical calculations
- **ReportLab** - PDF generation

### Database
- **SQLite** (Development)
- **PostgreSQL** (Production)

### Deployment
- **PythonAnywhere** (Current production)
- **Docker** support available

## 🔌 API Endpoints

### Core Endpoints
```
# Surveys
GET    /Survey/surveys/                    # List surveys (with filtering)
POST   /Survey/surveys/                    # Create survey
GET    /Survey/surveys/{id}/               # Get survey details
GET    /Survey/surveys/{id}/statistics/    # Get survey statistics

# Responses
POST   /Survey/responses/                  # Submit response
GET    /Survey/surveys/{id}/responses/     # List survey responses
GET    /Survey/surveys/{id}/responses/export/  # Export to PDF

# Authentication
POST   /accounts/signup/                   # User registration
POST   /accounts/login/                    # User login
POST   /accounts/signup/verify/            # Email verification
```

### Filtering Examples
```bash
# Get active surveys with no authentication required
GET /Survey/surveys/?is_active=true&respondent_auth_requirement=NONE

# Search surveys containing "customer"
GET /Survey/surveys/?search=customer&ordering=title

# Get surveys with responses, ordered by newest
GET /Survey/surveys/?has_responses=true&ordering=-created_at
```

## 📊 Features Deep Dive

### 🔐 Authentication System
- **NONE** - Anonymous responses allowed
- **QUICK** - User registration without email verification
- **FULL** - Complete registration with email verification

### 📝 Question Types
- **Text** - Open-ended text responses
- **Single Choice** - Radio button selections
- **Multiple Choice** - Checkbox selections
- **Rating** - Numeric rating scales (1-5, 1-10, etc.)
- **File Upload** - Document and image uploads

### 📊 Analytics Features
- **Basic Statistics** - Response counts, completion rates
- **Advanced Analytics** - Mean, median, standard deviation
- **Correlation Analysis** - Cross-question correlations
- **Trend Analysis** - Time-based response trends
- **Demographic Insights** - Response patterns by user groups

### 🔍 Filtering & Search
- **15+ Filter Options** - Comprehensive filtering system
- **Text Search** - Full-text search across surveys
- **Date Filtering** - Creation and closing date ranges
- **Status Filtering** - Active/inactive, open/closed
- **Response Filtering** - By response count and existence
- **Ordering** - Multiple sorting options

## 📄 PDF Export

### Features
- **Optimized Layout** - Landscape orientation with dynamic column widths
- **Text Wrapping** - Proper content wrapping for long text
- **Statistics Integration** - Optional statistics inclusion
- **Professional Styling** - Clean, readable formatting
- **Large Dataset Support** - Handles thousands of responses

### Usage
```bash
# Basic export
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/Survey/surveys/1/responses/export/" \
  -o survey_responses.pdf

# Export with statistics
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/Survey/surveys/1/responses/export/?include_stats=true" \
  -o survey_with_stats.pdf
```

## 🚀 Deployment

### Production Environment
- **Live URL:** [surveyplane.pythonanywhere.com](https://surveyplane.pythonanywhere.com)
- **Platform:** PythonAnywhere
- **Database:** PostgreSQL
- **Status:** ✅ Production Ready

### Local Development
```bash
# Using Pipenv (Recommended)
pipenv install
pipenv run migrate
pipenv run runserver

# Using Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t surveyplane .
docker run -p 8000:8000 surveyplane
```

## 🧪 Testing

### Run Tests
```bash
# All tests
pipenv run test

# Specific functionality
python test_pdf_export.py
python test_survey_filters.py
python test_filter_integration.py
```

### API Testing
```bash
# Test survey creation
curl -X POST http://localhost:8000/Survey/surveys/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"title": "Test Survey", "description": "Test", "closes_at": "2024-12-31T23:59:59Z"}'

# Test filtering
curl "http://localhost:8000/Survey/surveys/?is_active=true&search=test"
```

## 📁 Project Structure

```
SurveyPlane/
├── Account/                    # User management & authentication
├── Survey/                     # Core survey functionality
│   ├── models.py              # Database models
│   ├── views.py               # API views and filtering
│   ├── serializers.py         # Data serialization
│   ├── permissions.py         # Access control
│   └── urls.py                # URL routing
├── SurveyPlane/               # Project settings
├── media/                     # File uploads
├── static/                    # Static files
├── Pipfile                    # Dependencies
└── manage.py                  # Django management
```

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd SurveyPlane
pipenv install --dev
pipenv shell

# Make changes and test
python manage.py test
python test_pdf_export.py
```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings for functions and classes
- Write tests for new features

## 📞 Support & Contact

### Getting Help
- 📖 Check the comprehensive documentation files
- 🧪 Run the test scripts to verify functionality
- 🔍 Use the Django admin panel for debugging
- 📝 Review API responses for error details

### Resources
- **Documentation:** Complete guides in the repository
- **API Testing:** Use tools like Postman or curl
- **Admin Panel:** `http://localhost:8000/admin/`
- **Production API:** `https://surveyplane.pythonanywhere.com/`

## 📄 License

This project is available for use under the terms specified by the project maintainers.

## 🎉 Acknowledgments

Built with Django REST Framework and powered by modern Python technologies. Special thanks to the open-source community for the excellent tools and libraries that make this project possible.

---

**Ready to start surveying? Follow the [Setup Guide](SETUP_AND_USAGE_GUIDE.md) to get started! 🚀**
