from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Goal, Transaction, Habit, Category, GoalStatus, TransactionType, HabitFrequency
from datetime import datetime, date
from sqlalchemy import desc

api_bp = Blueprint('api', __name__)

# Goals API endpoints
@api_bp.route('/goals', methods=['GET'])
@login_required
def get_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(desc(Goal.created_at)).all()
    return jsonify([{
        'id': goal.id,
        'title': goal.title,
        'description': goal.description,
        'target_date': goal.target_date.isoformat() if goal.target_date else None,
        'status': goal.status.value,
        'progress_percentage': goal.progress_percentage,
        'created_at': goal.created_at.isoformat(),
        'days_remaining': goal.days_remaining()
    } for goal in goals])

@api_bp.route('/goals', methods=['POST'])
@login_required
def create_goal_api():
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    goal = Goal(
        user_id=current_user.id,
        title=data['title'],
        description=data.get('description', ''),
        target_date=datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data.get('target_date') else None
    )
    
    db.session.add(goal)
    db.session.commit()
    
    return jsonify({
        'id': goal.id,
        'title': goal.title,
        'description': goal.description,
        'target_date': goal.target_date.isoformat() if goal.target_date else None,
        'status': goal.status.value,
        'progress_percentage': goal.progress_percentage,
        'created_at': goal.created_at.isoformat()
    }), 201

@api_bp.route('/goals/<id>', methods=['PUT'])
@login_required
def update_goal_api(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    
    if 'title' in data:
        goal.title = data['title']
    if 'description' in data:
        goal.description = data['description']
    if 'target_date' in data:
        goal.target_date = datetime.strptime(data['target_date'], '%Y-%m-%d').date() if data['target_date'] else None
    if 'status' in data:
        goal.status = GoalStatus(data['status'])
    
    goal.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Goal updated successfully'})

@api_bp.route('/goals/<id>', methods=['DELETE'])
@login_required
def delete_goal_api(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    return jsonify({'message': 'Goal deleted successfully'})

# Transactions API endpoints
@api_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
                                  .order_by(desc(Transaction.transaction_date))\
                                  .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'amount': float(t.amount),
            'type': t.type.value,
            'category': {
                'id': t.category.id,
                'name': t.category.name,
                'color': t.category.color,
                'icon': t.category.icon
            },
            'description': t.description,
            'transaction_date': t.transaction_date.isoformat(),
            'created_at': t.created_at.isoformat()
        } for t in transactions.items],
        'pagination': {
            'page': transactions.page,
            'pages': transactions.pages,
            'per_page': transactions.per_page,
            'total': transactions.total,
            'has_next': transactions.has_next,
            'has_prev': transactions.has_prev
        }
    })

@api_bp.route('/transactions', methods=['POST'])
@login_required
def create_transaction_api():
    data = request.get_json()
    
    required_fields = ['amount', 'type', 'category_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate sufficient funds for expenses
    if data['type'] == 'Expense':
        current_balance = current_user.get_balance()
        if float(data['amount']) > current_balance:
            return jsonify({'error': f'Insufficient funds. Current balance: ${current_balance:.2f}'}), 400
    
    transaction = Transaction(
        user_id=current_user.id,
        category_id=data['category_id'],
        amount=data['amount'],
        type=TransactionType(data['type']),
        description=data.get('description', ''),
        transaction_date=datetime.strptime(data.get('transaction_date', date.today().isoformat()), '%Y-%m-%d').date()
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'id': transaction.id,
        'amount': float(transaction.amount),
        'type': transaction.type.value,
        'category_id': transaction.category_id,
        'description': transaction.description,
        'transaction_date': transaction.transaction_date.isoformat(),
        'created_at': transaction.created_at.isoformat()
    }), 201

@api_bp.route('/transactions/summary', methods=['GET'])
@login_required
def get_transaction_summary():
    # Current balance
    balance = current_user.get_balance()
    
    # This month's totals
    current_month_start = date.today().replace(day=1)
    monthly_income = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.INCOME,
        Transaction.transaction_date >= current_month_start
    ).scalar() or 0
    
    monthly_expenses = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.transaction_date >= current_month_start
    ).scalar() or 0
    
    return jsonify({
        'balance': float(balance),
        'monthly_income': float(monthly_income),
        'monthly_expenses': float(monthly_expenses),
        'monthly_net': float(monthly_income) - float(monthly_expenses)
    })

# Habits API endpoints
@api_bp.route('/habits', methods=['GET'])
@login_required
def get_habits():
    habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.created_at.desc()).all()
    return jsonify([{
        'id': habit.id,
        'name': habit.name,
        'description': habit.description,
        'frequency': habit.frequency.value,
        'target_count': habit.target_count,
        'current_streak': habit.current_streak,
        'longest_streak': habit.longest_streak,
        'is_active': habit.is_active,
        'reminder_time': habit.reminder_time.strftime('%H:%M') if habit.reminder_time else None,
        'completion_rate': habit.get_completion_rate(),
        'created_at': habit.created_at.isoformat()
    } for habit in habits])

@api_bp.route('/habits', methods=['POST'])
@login_required
def create_habit_api():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    # Check habit limit
    active_habits_count = Habit.query.filter_by(user_id=current_user.id, is_active=True).count()
    if active_habits_count >= 20:
        return jsonify({'error': 'Maximum habits reached (20)'}), 400
    
    # Check for duplicate name
    existing_habit = Habit.query.filter_by(
        user_id=current_user.id,
        name=data['name']
    ).first()
    
    if existing_habit:
        return jsonify({'error': 'Habit name already exists'}), 400
    
    habit = Habit(
        user_id=current_user.id,
        name=data['name'],
        description=data.get('description', ''),
        frequency=HabitFrequency(data.get('frequency', 'Daily')),
        target_count=data.get('target_count', 1)
    )
    
    db.session.add(habit)
    db.session.commit()
    
    return jsonify({
        'id': habit.id,
        'name': habit.name,
        'description': habit.description,
        'frequency': habit.frequency.value,
        'target_count': habit.target_count,
        'current_streak': habit.current_streak,
        'longest_streak': habit.longest_streak,
        'is_active': habit.is_active,
        'created_at': habit.created_at.isoformat()
    }), 201

@api_bp.route('/habits/<id>/checkin', methods=['POST'])
@login_required
def checkin_habit_api(id):
    habit = Habit.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    data = request.get_json() or {}
    checkin_date = data.get('date')
    
    if checkin_date:
        try:
            checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    else:
        checkin_date = date.today()
    
    success = habit.check_in(checkin_date)
    
    if success:
        db.session.commit()
        return jsonify({
            'message': 'Habit checked in successfully!',
            'current_streak': habit.current_streak,
            'longest_streak': habit.longest_streak
        })
    else:
        return jsonify({'error': 'Already checked in for this date'}), 400

# Categories API endpoint
@api_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'color': category.color,
        'icon': category.icon,
        'is_default': category.is_default
    } for category in categories])