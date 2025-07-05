# SurveyPlane - Complete Project Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Authentication & Authorization](#authentication--authorization)
8. [File Management](#file-management)
9. [Filtering & Search](#filtering--search)
10. [Export Capabilities](#export-capabilities)
11. [Security Features](#security-features)
12. [Deployment](#deployment)

## 🎯 Project Overview

**SurveyPlane** is a comprehensive survey management platform built with Django REST Framework. It provides a complete solution for creating, managing, and analyzing surveys with advanced features including multiple question types, flexible authentication, real-time analytics, and comprehensive export capabilities.

### Key Capabilities

- **Survey Creation & Management** - Create surveys with multiple question types
- **Flexible Authentication** - Three-tier authentication system for respondents
- **Advanced Analytics** - Statistical analysis with correlation and trend analysis
- **Export Functionality** - PDF export with customizable layouts
- **File Management** - Support for file uploads in surveys
- **Comprehensive Filtering** - Advanced filtering and search capabilities
- **Real-time Statistics** - Live survey statistics and insights

## 🏗️ Architecture

### System Architecture

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

### Application Structure

```
SurveyPlane/
├── Account/                 # User management & authentication
├── Survey/                  # Core survey functionality
├── SurveyPlane/            # Project settings & configuration
├── media/                  # File uploads storage
├── static/                 # Static files
└── manage.py              # Django management script
```

## ✨ Features

### Core Features

#### 1. Survey Management
- **Create Surveys** - Rich survey creation with metadata
- **Question Types** - Text, Single Choice, Multiple Choice, Rating, File Upload
- **Survey Settings** - Flexible closing dates and activation controls
- **Survey Analytics** - Comprehensive statistics and insights

#### 2. Question System
- **Multiple Types** - Support for 5 different question types
- **Validation** - Built-in validation for each question type
- **File Attachments** - Questions can include file attachments
- **Ordering** - Custom question ordering within surveys

#### 3. Response Collection
- **Flexible Submission** - Support for authenticated and anonymous responses
- **File Uploads** - Respondents can upload files as answers
- **Validation** - Real-time validation of responses
- **Progress Tracking** - Completion time tracking

#### 4. Advanced Analytics
- **Statistical Analysis** - Mean, median, standard deviation for rating questions
- **Correlation Analysis** - Cross-question correlation analysis
- **Trend Analysis** - Time-based trend analysis (daily, weekly, monthly, quarterly)
- **Demographic Insights** - Response patterns by user demographics
- **Real-time Updates** - Live statistics as responses come in

#### 5. Export & Reporting
- **PDF Export** - Professional PDF reports with customizable layouts
- **Statistics Integration** - Optional statistics inclusion in exports
- **Responsive Design** - Optimized for various content sizes
- **Batch Export** - Export multiple survey responses at once

### Advanced Features

#### 1. Authentication System
- **Three-Tier Auth** - NONE, QUICK, FULL authentication levels
- **Email Verification** - Secure email verification system
- **Token Authentication** - REST API token-based authentication
- **Permission System** - Granular permissions for different user roles

#### 2. Filtering & Search
- **15+ Filter Options** - Comprehensive filtering system
- **Text Search** - Full-text search across surveys
- **Date Range Filtering** - Filter by creation and closing dates
- **Status Filtering** - Filter by active/inactive, open/closed status
- **Creator Filtering** - Filter by survey creator
- **Response-based Filtering** - Filter by response count and existence

#### 3. File Management
- **Secure Upload** - Validated file uploads with size and type restrictions
- **Organized Storage** - Hierarchical file organization
- **Access Control** - Secure file access with proper permissions
- **Multiple Formats** - Support for various file formats

## 🛠️ Technology Stack

### Backend
- **Django 5.1.2** - Web framework
- **Django REST Framework** - API framework
- **django-rest-authemail** - Authentication system
- **django-filter 24.2** - Advanced filtering
- **django-cors-headers** - CORS support
- **django-environ** - Environment configuration

### Data & Analytics
- **NumPy** - Statistical calculations
- **PostgreSQL/SQLite** - Database systems
- **JSON Fields** - Flexible data storage

### File Processing & Export
- **ReportLab** - PDF generation
- **Django File Storage** - File management

### Development & Deployment
- **Pipenv** - Dependency management
- **PythonAnywhere** - Production deployment
- **Docker** - Containerization support

## 🗄️ Database Schema

### Core Models

#### Survey Model
```python
class Survey(models.Model):
    title = CharField(max_length=200)
    description = TextField(blank=True)
    creator = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)
    closes_at = DateTimeField()
    is_active = BooleanField(default=True)
    respondent_auth_requirement = CharField(
        choices=['NONE', 'QUICK', 'FULL'],
        default='QUICK'
    )
```

#### Question Model
```python
class Question(models.Model):
    survey = ForeignKey(Survey)
    question_text = TextField()
    question_type = CharField(choices=[
        'text', 'single_choice', 'multiple_choice', 
        'rating', 'file'
    ])
    required = BooleanField(default=False)
    order = IntegerField(default=0)
    settings = JSONField(default=dict)  # Type-specific settings
```

#### Response Model
```python
class Response(models.Model):
    survey = ForeignKey(Survey)
    respondent = ForeignKey(User, null=True, blank=True)
    submitted_at = DateTimeField(auto_now_add=True)
    completion_time = DurationField(null=True, blank=True)
```

#### Answer Model
```python
class Answer(models.Model):
    response = ForeignKey(Response)
    question = ForeignKey(Question)
    value = JSONField()  # Flexible answer storage
```

### Relationships

```
User ──┐
       ├── Survey (creator)
       └── Response (respondent)

Survey ──┐
         ├── Question (multiple)
         └── Response (multiple)

Response ── Answer (multiple)
Question ── Answer (multiple)
```

## 🔌 API Endpoints

### Survey Endpoints
```
GET    /Survey/surveys/                    # List surveys (with filtering)
POST   /Survey/surveys/                    # Create survey
GET    /Survey/surveys/{id}/               # Get survey details
PUT    /Survey/surveys/{id}/               # Update survey
DELETE /Survey/surveys/{id}/               # Delete survey
GET    /Survey/surveys/{id}/statistics/    # Get survey statistics
GET    /Survey/surveys/management/         # Get user's surveys
```

### Question Endpoints
```
GET    /Survey/questions/                  # List questions
POST   /Survey/questions/                  # Create question
GET    /Survey/questions/{id}/             # Get question details
PUT    /Survey/questions/{id}/             # Update question
DELETE /Survey/questions/{id}/             # Delete question
```

### Response Endpoints
```
GET    /Survey/responses/                  # List responses
POST   /Survey/responses/                  # Submit response
GET    /Survey/responses/{id}/             # Get response details
PUT    /Survey/responses/{id}/             # Update response
DELETE /Survey/responses/{id}/             # Delete response
```

### Management Endpoints
```
GET    /Survey/surveys/{id}/responses/     # List survey responses
GET    /Survey/surveys/{id}/responses/{response_id}/  # Get specific response
GET    /Survey/surveys/{id}/responses/export/         # Export to PDF
```

### Authentication Endpoints
```
POST   /accounts/signup/                   # User registration
POST   /accounts/signup/verify/            # Email verification
POST   /accounts/login/                    # User login
POST   /accounts/logout/                   # User logout
POST   /accounts/password/reset/           # Password reset
```

## 🔐 Authentication & Authorization

### Authentication Levels

#### 1. NONE - No Authentication Required
- Anonymous responses allowed
- No user registration needed
- Suitable for public surveys

#### 2. QUICK - Quick Registration
- User registration required
- No email verification needed
- Fast onboarding process

#### 3. FULL - Full Authentication
- User registration required
- Email verification mandatory
- Maximum security level

### Permission System

#### Survey Permissions
- **Creators** - Full CRUD access to their surveys
- **Respondents** - Submit responses based on auth level
- **Anonymous** - Limited access based on survey settings

#### Response Permissions
- **Survey Creators** - View all responses to their surveys
- **Respondents** - View/edit their own responses
- **Anonymous** - Submit responses only

## 📁 File Management

### File Upload System

#### Supported File Types
- **Documents** - PDF, DOC, DOCX
- **Images** - JPG, PNG, GIF
- **Archives** - ZIP, RAR
- **Custom** - Configurable per question

#### Storage Organization
```
media/
├── questions/
│   └── {survey_id}/
│       └── question_{id}.{ext}
└── answers/
    └── {survey_id}/
        └── {response_id}/
            └── {question_id}/
                └── {question_id}_{response_id}.{ext}
```

#### Security Features
- **File Size Limits** - Configurable per question (default 5MB)
- **Type Validation** - Strict file type checking
- **Secure Storage** - Protected file access
- **Cleanup** - Automatic file cleanup on deletion

## 🔍 Filtering & Search

### Available Filters

#### Authentication & Status
- `respondent_auth_requirement` - NONE, QUICK, FULL
- `is_active` - true/false
- `is_closed` - true/false

#### Creator & Ownership
- `creator` - User ID
- `creator_email` - Email pattern matching

#### Date & Time
- `created_after` / `created_before` - Creation date range
- `closes_after` / `closes_before` - Closing date range

#### Content Search
- `title` - Title pattern matching
- `description` - Description pattern matching
- `search` - Cross-field search

#### Response Analytics
- `has_responses` - true/false
- `min_responses` - Minimum response count

### Ordering Options
- `created_at` - Creation date (default: newest first)
- `closes_at` - Closing date
- `title` - Alphabetical
- `id` - Survey ID

## 📊 Export Capabilities

### PDF Export Features

#### Layout Optimization
- **Landscape Orientation** - Better table fit
- **Dynamic Column Widths** - Automatic width calculation
- **Text Wrapping** - Proper content wrapping
- **Responsive Design** - Adapts to content size

#### Content Options
- **Basic Export** - Survey responses only
- **With Statistics** - Include survey analytics
- **Custom Formatting** - Professional styling
- **Batch Export** - Multiple surveys

#### Technical Features
- **Memory Efficient** - Streaming PDF generation
- **Large Dataset Support** - Handles thousands of responses
- **Error Handling** - Graceful failure handling
- **Download Management** - Proper file delivery

## 🛡️ Security Features

### Data Protection
- **Input Validation** - Comprehensive input sanitization
- **SQL Injection Prevention** - ORM-based queries
- **XSS Protection** - Output escaping
- **CSRF Protection** - Built-in CSRF tokens

### Authentication Security
- **Token-based Auth** - Secure API authentication
- **Email Verification** - Verified user accounts
- **Password Security** - Django's built-in password handling
- **Session Management** - Secure session handling

### File Security
- **Upload Validation** - File type and size validation
- **Secure Storage** - Protected file access
- **Access Control** - Permission-based file access
- **Malware Prevention** - File content validation

## 🚀 Deployment

### Production Environment
- **Platform** - PythonAnywhere
- **URL** - surveyplane.pythonanywhere.com
- **Database** - PostgreSQL (production) / SQLite (development)
- **File Storage** - Local file system with backup

### Environment Configuration
- **Environment Variables** - Secure configuration management
- **Debug Settings** - Production-safe debug configuration
- **CORS Settings** - Proper cross-origin configuration
- **Static Files** - Optimized static file serving

### Monitoring & Maintenance
- **Error Logging** - Comprehensive error tracking
- **Performance Monitoring** - Query optimization
- **Backup Strategy** - Regular data backups
- **Update Management** - Controlled deployment updates

---

## 📞 Support & Contact

For technical support, feature requests, or bug reports, please contact the development team or create an issue in the project repository.

**Project Status:** ✅ Production Ready
**Last Updated:** July 2025
**Version:** 1.0.0
