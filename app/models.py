from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
import uuid
from app import db

class GoalStatus(Enum):
    ACTIVE = "Active"
    COMPLETED = "Completed" 
    PAUSED = "Paused"

class TransactionType(Enum):
    INCOME = "Income"
    EXPENSE = "Expense"

class HabitFrequency(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    habits = db.relationship('Habit', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_balance(self):
        income = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.id,
            Transaction.type == TransactionType.INCOME
        ).scalar() or 0
        
        expenses = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.id,
            Transaction.type == TransactionType.EXPENSE
        ).scalar() or 0
        
        return float(income) - float(expenses)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    status = db.Column(db.Enum(GoalStatus), default=GoalStatus.ACTIVE)
    progress_percentage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    milestones = db.relationship('Milestone', backref='goal', lazy=True, cascade='all, delete-orphan')
    
    def update_progress(self):
        if self.milestones:
            completed_milestones = len([m for m in self.milestones if m.is_completed])
            total_milestones = len(self.milestones)
            self.progress_percentage = int((completed_milestones / total_milestones) * 100)
            
            if self.progress_percentage == 100:
                self.status = GoalStatus.COMPLETED
        else:
            self.progress_percentage = 0
    
    def days_remaining(self):
        if self.target_date:
            delta = self.target_date - date.today()
            return delta.days
        return None
    
    def __repr__(self):
        return f'<Goal {self.title}>'

class Milestone(db.Model):
    __tablename__ = 'milestones'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = db.Column(db.String(36), db.ForeignKey('goals.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_complete(self):
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.goal.update_progress()
    
    def __repr__(self):
        return f'<Milestone {self.title}>'

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#6B7280')  # hex color
    icon = db.Column(db.String(50), default='📊')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    
    def get_total_amount(self, transaction_type=None, start_date=None, end_date=None):
        query = Transaction.query.filter(Transaction.category_id == self.id)
        
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        return db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.category_id == self.id
        ).scalar() or 0
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    description = db.Column(db.String(500))
    transaction_date = db.Column(db.Date, default=date.today)
    receipt_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.type.value}: ${self.amount}>'

class Habit(db.Model):
    __tablename__ = 'habits'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    frequency = db.Column(db.Enum(HabitFrequency), default=HabitFrequency.DAILY)
    target_count = db.Column(db.Integer, default=1)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    reminder_time = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    habit_logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade='all, delete-orphan')
    
    def check_in(self, date_completed=None):
        if date_completed is None:
            date_completed = date.today()
        
        existing_log = HabitLog.query.filter(
            HabitLog.habit_id == self.id,
            HabitLog.date_completed == date_completed
        ).first()
        
        if not existing_log:
            log = HabitLog(habit_id=self.id, date_completed=date_completed)
            db.session.add(log)
            self.update_streak()
            return True
        return False
    
    def update_streak(self):
        from datetime import timedelta
        today = date.today()
        current_streak = 0
        
        check_date = today
        while True:
            log = HabitLog.query.filter(
                HabitLog.habit_id == self.id,
                HabitLog.date_completed == check_date
            ).first()
            
            if log:
                current_streak += 1
                if self.frequency == HabitFrequency.DAILY:
                    check_date = check_date - timedelta(days=1)
                elif self.frequency == HabitFrequency.WEEKLY:
                    check_date = check_date - timedelta(days=7)
                elif self.frequency == HabitFrequency.MONTHLY:
                    # Go to first day of current month, then subtract one day to get last day of previous month
                    first_of_month = check_date.replace(day=1)
                    check_date = first_of_month - timedelta(days=1)
            else:
                break
        
        self.current_streak = current_streak
        if current_streak > self.longest_streak:
            self.longest_streak = current_streak
    
    def get_completion_rate(self, days=30):
        from datetime import timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        total_days = days
        completed_days = HabitLog.query.filter(
            HabitLog.habit_id == self.id,
            HabitLog.date_completed.between(start_date, end_date)
        ).count()
        
        return (completed_days / total_days) * 100 if total_days > 0 else 0
    
    def __repr__(self):
        return f'<Habit {self.name}>'

class HabitLog(db.Model):
    __tablename__ = 'habit_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    habit_id = db.Column(db.String(36), db.ForeignKey('habits.id'), nullable=False)
    date_completed = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('habit_id', 'date_completed'),)
    
    def __repr__(self):
        return f'<HabitLog {self.habit_id} on {self.date_completed}>'