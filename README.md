# 🎯 Self-Focus Management App

A comprehensive personal management web application built with Flask that helps users track goals, manage finances, and build healthy habits.

## 📑 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Core Features](#core-features)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Roadmap](#roadmap)

## ✨ Features

### 🎯 Goal Management
- SMART goal creation and tracking
- Milestone system for better organization
- Visual progress tracking
- Status management (Active/Completed/Paused)
- Due date monitoring

### 💰 Financial Tracking
- Income and expense recording
- Custom category management
- Real-time balance monitoring
- Spending analytics
- CSV data export

### ✅ Habit Building
- Daily/weekly/monthly habits
- Streak tracking
- Calendar visualization
- Completion analytics
- Quick check-in functionality
- Maximum 20 active habits

### 📊 Dashboard
- Key metrics overview
- Recent activity feed
- Progress visualizations
- Quick actions

## 🛠 Tech Stack
- **Backend**: Python Flask, SQLAlchemy ORM
- **Database**: SQLite (configurable to PostgreSQL/MySQL)
- **Frontend**: Jinja2, Modern CSS, JavaScript
- **Security**: Flask-Login, Flask-WTF

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Clone repository
git clone <repository-url>
cd AI-App

# Set up virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo SECRET_KEY=your-secret-key-here > .env
echo DATABASE_URL=sqlite:///self_focus.db >> .env

# Run application
python run.py
```

### Demo Account
- Username: `john_doe`
- Password: `password123`

## 📁 Project Structure
```
self_focus_app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── forms.py             # Form classes
│   └── routes/              # Route handlers
├── templates/               # HTML templates
├── static/                  # Assets
├── tests/                   # Unit tests
└── run.py                   # Entry point
```

## Core Features

### Goal Management
- **SMART Goals**: Support for Specific, Measurable, Achievable, Relevant, Time-bound goals
- **Milestone System**: Break large goals into smaller, manageable milestones
- **Progress Tracking**: Visual progress bars and percentage completion
- **Status Management**: Active, Completed, and Paused states
- **Due Date Tracking**: Days remaining and overdue notifications

### Financial Management
- **Transaction Recording**: Easy income and expense entry
- **Category System**: Customizable categories with colors and icons
- **Balance Tracking**: Real-time balance calculations
- **Spending Analytics**: Monthly summaries and category breakdowns
- **Data Export**: CSV export for external analysis
- **Validation**: Insufficient funds protection

### Habit Tracking
- **Flexible Frequency**: Daily, weekly, or monthly habits
- **Streak Tracking**: Current and longest streak counters
- **Calendar View**: Visual habit completion calendar
- **Completion Analytics**: 30-day completion rates
- **Quick Check-in**: One-click habit completion
- **Habit Limits**: Maximum 20 active habits per user

### Dashboard Analytics
- **Key Metrics**: Goals, balance, habits overview
- **Recent Activity**: Latest goals, transactions, and habits
- **Progress Indicators**: Visual progress tracking
- **Quick Actions**: Fast access to common tasks

## API Documentation

### Goals
- `GET /api/goals` - List user goals
- `POST /api/goals` - Create new goal
- `PUT /api/goals/<id>` - Update goal
- `DELETE /api/goals/<id>` - Delete goal

### Transactions
- `GET /api/transactions` - List transactions (paginated)
- `POST /api/transactions` - Create transaction
- `GET /api/transactions/summary` - Financial summary

### Habits
- `GET /api/habits` - List user habits
- `POST /api/habits` - Create new habit
- `POST /api/habits/<id>/checkin` - Record habit completion

### Categories
- `GET /api/categories` - List user categories

## 🔒 Security Features
- Secure password hashing
- Session management
- CSRF protection
- Input validation
- User data isolation


## 📄 License
This project is licensed under the MIT License.

## 💡 Future Enhancements
- [ ] Mobile responsive design
- [ ] Push notifications
- [ ] Advanced analytics
- [ ] Dark mode
- [ ] Multi-language support
- [ ] Docker support

---

**Built with ❤️ for personal productivity**
