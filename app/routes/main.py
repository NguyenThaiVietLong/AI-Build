from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import Goal, Transaction, Habit, HabitLog, TransactionType, GoalStatus
from app import db
from datetime import date, datetime, timedelta
from sqlalchemy import func, desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Goals statistics
    total_goals = Goal.query.filter_by(user_id=current_user.id).count()
    active_goals = Goal.query.filter_by(user_id=current_user.id, status=GoalStatus.ACTIVE).count()
    completed_goals = Goal.query.filter_by(user_id=current_user.id, status=GoalStatus.COMPLETED).count()
    
    # Recent goals
    recent_goals = Goal.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Goal.created_at)).limit(5).all()
    
    # Financial statistics
    current_balance = current_user.get_balance()
    
    # This month's transactions
    current_month_start = date.today().replace(day=1)
    monthly_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.INCOME,
        Transaction.transaction_date >= current_month_start
    ).scalar() or 0
    
    monthly_expenses = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.transaction_date >= current_month_start
    ).scalar() or 0
    
    # Recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(desc(Transaction.created_at)).limit(5).all()
    
    # Habits statistics
    active_habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).count()
    
    # Today's habits completion
    today_completed_habits = 0
    user_habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    for habit in user_habits:
        log = HabitLog.query.filter_by(habit_id=habit.id, date_completed=date.today()).first()
        if log:
            today_completed_habits += 1
    
    # Recent habit activity
    recent_habit_logs = db.session.query(HabitLog)\
        .join(Habit)\
        .filter(Habit.user_id == current_user.id)\
        .order_by(desc(HabitLog.created_at))\
        .limit(5).all()
    
    return render_template('dashboard.html',
                         total_goals=total_goals,
                         active_goals=active_goals,
                         completed_goals=completed_goals,
                         recent_goals=recent_goals,
                         current_balance=current_balance,
                         monthly_income=monthly_income,
                         monthly_expenses=monthly_expenses,
                         recent_transactions=recent_transactions,
                         active_habits=active_habits,
                         today_completed_habits=today_completed_habits,
                         user_habits=user_habits,
                         recent_habit_logs=recent_habit_logs)

@main_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats():
    # Spending by category (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    spending_data = db.session.query(
        Transaction.category_id,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction.category)\
     .filter(Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date >= thirty_days_ago)\
     .group_by(Transaction.category_id).all()
    
    # Goals progress
    goals_progress = []
    for goal in Goal.query.filter_by(user_id=current_user.id, status=GoalStatus.ACTIVE).all():
        goals_progress.append({
            'title': goal.title,
            'progress': goal.progress_percentage,
            'days_remaining': goal.days_remaining()
        })
    
    return jsonify({
        'spending_by_category': [{'category_id': s.category_id, 'total': float(s.total)} for s in spending_data],
        'goals_progress': goals_progress
    })