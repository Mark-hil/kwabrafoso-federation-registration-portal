# Kwabrafoso District Youth Ministry Management System

A comprehensive church management system designed for the Kwabrafoso District Youth Ministry to manage member registration, attendance tracking, visitor management, and communication for the 2026 Annual Survival Camp.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (for production)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd kwbrafoso-district
```

2. **Set up virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser account**
```bash
python manage.py createsuperuser
```

7. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## 🐳 Docker Deployment

### Using Docker Compose
```bash
docker-compose up --build
```

### Manual Docker Build
```bash
docker build -t kwbrafoso-district .
docker run -p 8000:8000 kwbrafoso-district
```

## 📱 Features

### 🎯 Core Functionality
- **Member Management**: Complete registration system with QR code generation
- **Attendance Tracking**: QR code scanner for worship services, events, and camps
- **Room Allocation**: Smart room assignment based on gender, church, and district
- **Visitor Management**: Guest registration and follow-up system
- **Analytics Dashboard**: Real-time statistics and visualizations

### 📊 Analytics & Reporting
- Live attendance trends and statistics
- Church and district distribution charts
- Gender demographics analysis
- Room occupancy monitoring
- Exportable CSV reports

### 📱 Communication
- **SMS Integration**: Automated welcome messages via Arkesel (Ghana)
- **Email Notifications**: Account activation and password reset
- **Bulk Messaging**: Send announcements to member groups

### 🔐 Security
- Email-based account activation
- Role-based access control
- Secure authentication system
- CSRF protection

## 🏗️ Technology Stack

### Backend
- **Django 5.1** - Web framework
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **Gunicorn** - WSGI server

### Frontend
- **HTML5/CSS3** - Modern markup
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Data visualization
- **Font Awesome** - Icon library

### Third-party Services
- **Arkesel SMS API** - SMS messaging for Ghana
- **QR Code Library** - QR code generation
- **Pillow** - Image processing

## 📁 Project Structure

```
kwbrafoso-district/
├── church_crm/          # Django project configuration
├── members/             # Main Django app
│   ├── models.py        # Database models
│   ├── views.py         # Business logic
│   ├── forms.py         # Form classes
│   └── utils/sms.py     # SMS functionality
├── templates/           # HTML templates
├── static/             # CSS, JS, images
├── media/              # User uploads
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── Dockerfile         # Docker configuration
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ARKESEL_API_KEY=your-sms-api-key
ARKESEL_SENDER_ID=Kwabrafoso District
```

### Database Setup

#### Development (SQLite)
```bash
# SQLite is configured by default
python manage.py migrate
```

#### Production (PostgreSQL)
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Set DATABASE_URL in .env
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

## 📊 Key Features Overview

### 🏠 Room Management
- **Smart Allocation**: Automatic room assignment based on member attributes
- **Capacity Tracking**: Real-time occupancy monitoring
- **Gender Segregation**: Separate accommodations for male/female members
- **Manual Override**: Administrators can manually adjust assignments

### 📱 QR Code System
- **Unique Codes**: Each member gets a unique QR code for attendance
- **Mobile Scanner**: Responsive scanner interface for mobile devices
- **Multiple Events**: Track attendance for worship services, events, and camps
- **Real-time Updates**: Dashboard updates immediately after scanning

### 📈 Analytics Dashboard
- **Live Metrics**: Total members, attendance counts, visitor statistics
- **Visual Charts**: Attendance trends, demographic distributions
- **Interactive Elements**: Hover effects and smooth animations
- **Data Export**: Download reports in CSV format

## 🚀 Deployment

### Production Deployment
1. **Set environment variables**
2. **Configure database**
3. **Collect static files**
```bash
python manage.py collectstatic --noinput
```
4. **Run with Gunicorn**
```bash
gunicorn church_crm.wsgi:application
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📞 Support

### Documentation
- **Full Documentation**: See `PROJECT_DOCUMENTATION.md` for detailed technical documentation
- **API Reference**: Comprehensive API documentation included
- **User Guide**: Step-by-step usage instructions

### Common Issues
- **SMS Not Working**: Check Arkesel API key configuration
- **Database Errors**: Verify DATABASE_URL format
- **Static Files**: Run `collectstatic` command
- **Permission Errors**: Check file permissions for media/uploads

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is proprietary software for the Kwabrafoso District Youth Ministry.

## 📅 Project Information

- **Organization**: Kwabrafoso District Youth Ministry
- **Event**: 2026 Annual Survival Camp
- **Purpose**: Member management and attendance tracking
- **Version**: 0.1.0
- **Last Updated**: February 2026

---

**Built with ❤️ for the Kwabrafoso District Youth Ministry**
