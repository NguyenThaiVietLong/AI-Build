# 🎯 Self-Focus Management App

A comprehensive personal management web application built with Flask that helps users track goals, manage finances, and build healthy habits.

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

## 🔒 Security Features
- Secure password hashing
- Session management
- CSRF protection
- Input validation
- User data isolation


## 💡 Future Enhancements
- [ ] Mobile responsive design
- [ ] Push notifications
- [ ] Advanced analytics
- [ ] Dark mode
- [ ] Multi-language support
- [ ] Docker support

---

**Built with ❤️ for personal productivity**
