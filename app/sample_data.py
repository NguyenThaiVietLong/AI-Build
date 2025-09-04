from app import db
from app.models import User, Goal, Milestone, Transaction, Category, Habit, HabitLog, GoalStatus, TransactionType, HabitFrequency
from datetime import date, datetime, timedelta
import random
from decimal import Decimal

def create_sample_data():
    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create regular user
    user1 = User(
        username='john_doe',
        email='john@example.com'
    )
    user1.set_password('password123')
    db.session.add(user1)
    
    db.session.commit()
    
    # Create default categories for both users
    create_default_categories(admin)
    create_default_categories(user1)
    
    # Create sample goals for john_doe
    create_sample_goals(user1)
    
    # Create sample transactions for john_doe
    create_sample_transactions(user1)
    
    # Create sample habits for john_doe
    create_sample_habits(user1)
    
    db.session.commit()
    print("Sample data created successfully!")

def create_default_categories(user):
    categories = [
        {'name': 'Food & Dining', 'color': '#EF4444', 'icon': '🍽️'},
        {'name': 'Transportation', 'color': '#3B82F6', 'icon': '🚗'},
        {'name': 'Shopping', 'color': '#8B5CF6', 'icon': '🛍️'},
        {'name': 'Entertainment', 'color': '#F59E0B', 'icon': '🎬'},
        {'name': 'Health & Fitness', 'color': '#10B981', 'icon': '💊'},
        {'name': 'Education', 'color': '#06B6D4', 'icon': '📚'},
        {'name': 'Bills & Utilities', 'color': '#6B7280', 'icon': '💡'},
        {'name': 'Salary', 'color': '#22C55E', 'icon': '💰'},
        {'name': 'Freelance', 'color': '#84CC16', 'icon': '💻'},
        {'name': 'Investment', 'color': '#14B8A6', 'icon': '📈'},
    ]
    
    for cat_data in categories:
        category = Category(
            user_id=user.id,
            name=cat_data['name'],
            color=cat_data['color'],
            icon=cat_data['icon'],
            is_default=True
        )
        db.session.add(category)

def create_sample_goals(user):
    goals_data = [
        {
            'title': 'Learn Python Programming',
            'description': 'Master Python programming language including advanced concepts like decorators, generators, and async programming.',
            'target_date': date.today() + timedelta(days=180),
            'status': GoalStatus.ACTIVE,
            'milestones': [
                {'title': 'Complete Python Basics Course', 'target_date': date.today() + timedelta(days=30), 'completed': True},
                {'title': 'Build First Python Project', 'target_date': date.today() + timedelta(days=60), 'completed': True},
                {'title': 'Learn Advanced Python Concepts', 'target_date': date.today() + timedelta(days=120), 'completed': False},
                {'title': 'Complete Portfolio Project', 'target_date': date.today() + timedelta(days=180), 'completed': False}
            ]
        },
        {
            'title': 'Save $10,000 Emergency Fund',
            'description': 'Build a comprehensive emergency fund to cover 6 months of expenses for financial security.',
            'target_date': date.today() + timedelta(days=365),
            'status': GoalStatus.ACTIVE,
            'milestones': [
                {'title': 'Save $2,500', 'target_date': date.today() + timedelta(days=90), 'completed': True},
                {'title': 'Save $5,000', 'target_date': date.today() + timedelta(days=180), 'completed': False},
                {'title': 'Save $7,500', 'target_date': date.today() + timedelta(days=270), 'completed': False},
                {'title': 'Reach $10,000 Goal', 'target_date': date.today() + timedelta(days=365), 'completed': False}
            ]
        },
        {
            'title': 'Run a Half Marathon',
            'description': 'Train for and complete a 13.1 mile half marathon race to improve fitness and achieve personal milestone.',
            'target_date': date.today() + timedelta(days=240),
            'status': GoalStatus.ACTIVE,
            'milestones': [
                {'title': 'Run 5K without stopping', 'target_date': date.today() + timedelta(days=30), 'completed': True},
                {'title': 'Run 10K race', 'target_date': date.today() + timedelta(days=90), 'completed': True},
                {'title': 'Complete 15K training run', 'target_date': date.today() + timedelta(days=150), 'completed': False},
                {'title': 'Finish Half Marathon', 'target_date': date.today() + timedelta(days=240), 'completed': False}
            ]
        },
        {
            'title': 'Start Freelance Business',
            'description': 'Launch a successful freelance web development business and acquire first 5 clients.',
            'target_date': date.today() + timedelta(days=150),
            'status': GoalStatus.COMPLETED,
            'milestones': [
                {'title': 'Build Portfolio Website', 'target_date': date.today() - timedelta(days=60), 'completed': True},
                {'title': 'Get First Client', 'target_date': date.today() - timedelta(days=30), 'completed': True},
                {'title': 'Complete 3 Projects', 'target_date': date.today() - timedelta(days=10), 'completed': True},
                {'title': 'Acquire 5 Regular Clients', 'target_date': date.today() - timedelta(days=5), 'completed': True}
            ]
        }
    ]
    
    for goal_data in goals_data:
        goal = Goal(
            user_id=user.id,
            title=goal_data['title'],
            description=goal_data['description'],
            target_date=goal_data['target_date'],
            status=goal_data['status']
        )
        db.session.add(goal)
        db.session.flush()  # Get the goal ID
        
        for milestone_data in goal_data['milestones']:
            milestone = Milestone(
                goal_id=goal.id,
                title=milestone_data['title'],
                target_date=milestone_data['target_date'],
                is_completed=milestone_data['completed']
            )
            if milestone_data['completed']:
                milestone.completed_at = datetime.utcnow()
            db.session.add(milestone)
        
        goal.update_progress()

def create_sample_transactions(user):
    # Get user categories
    categories = Category.query.filter_by(user_id=user.id).all()
    cat_map = {cat.name: cat for cat in categories}
    
    # Generate transactions for the last 90 days
    start_date = date.today() - timedelta(days=90)
    
    sample_transactions = []
    
    # Regular income
    for i in range(3):  # 3 months of salary
        salary_date = start_date + timedelta(days=30*i + 1)
        sample_transactions.append({
            'amount': Decimal('5500.00'),
            'type': TransactionType.INCOME,
            'category': cat_map['Salary'],
            'description': 'Monthly Salary',
            'date': salary_date
        })
    
    # Freelance income
    freelance_dates = [start_date + timedelta(days=15), start_date + timedelta(days=45), start_date + timedelta(days=75)]
    freelance_amounts = [Decimal('800.00'), Decimal('1200.00'), Decimal('950.00')]
    
    for date_val, amount in zip(freelance_dates, freelance_amounts):
        sample_transactions.append({
            'amount': amount,
            'type': TransactionType.INCOME,
            'category': cat_map['Freelance'],
            'description': 'Website Development Project',
            'date': date_val
        })
    
    # Regular expenses
    expense_patterns = [
        # Food & Dining
        {'category': 'Food & Dining', 'min': 15, 'max': 85, 'frequency': 25},  # 25 transactions over 90 days
        # Transportation
        {'category': 'Transportation', 'min': 25, 'max': 120, 'frequency': 15},
        # Shopping
        {'category': 'Shopping', 'min': 30, 'max': 200, 'frequency': 12},
        # Entertainment
        {'category': 'Entertainment', 'min': 20, 'max': 150, 'frequency': 10},
        # Health & Fitness
        {'category': 'Health & Fitness', 'min': 25, 'max': 80, 'frequency': 8},
        # Bills & Utilities (monthly)
        {'category': 'Bills & Utilities', 'min': 150, 'max': 350, 'frequency': 9},
    ]
    
    for pattern in expense_patterns:
        for i in range(pattern['frequency']):
            random_date = start_date + timedelta(days=random.randint(0, 89))
            amount = Decimal(str(random.uniform(pattern['min'], pattern['max'])))
            amount = amount.quantize(Decimal('0.01'))
            
            sample_transactions.append({
                'amount': amount,
                'type': TransactionType.EXPENSE,
                'category': cat_map[pattern['category']],
                'description': f"{pattern['category']} expense",
                'date': random_date
            })
    
    # Add specific memorable transactions
    sample_transactions.extend([
        {
            'amount': Decimal('1200.00'),
            'type': TransactionType.EXPENSE,
            'category': cat_map['Education'],
            'description': 'Python Programming Course',
            'date': start_date + timedelta(days=10)
        },
        {
            'amount': Decimal('300.00'),
            'type': TransactionType.EXPENSE,
            'category': cat_map['Health & Fitness'],
            'description': 'Gym Membership Annual',
            'date': start_date + timedelta(days=5)
        },
    ])
    
    # Create transactions in database
    for trans_data in sample_transactions:
        transaction = Transaction(
            user_id=user.id,
            category_id=trans_data['category'].id,
            amount=trans_data['amount'],
            type=trans_data['type'],
            description=trans_data['description'],
            transaction_date=trans_data['date']
        )
        db.session.add(transaction)

def create_sample_habits(user):
    habits_data = [
        {
            'name': 'Drink 8 glasses of water',
            'description': 'Stay hydrated by drinking at least 8 glasses of water daily',
            'frequency': HabitFrequency.DAILY,
            'target_count': 8,
            'streak_days': 15  # Days of current streak
        },
        {
            'name': 'Exercise for 30 minutes',
            'description': 'Complete at least 30 minutes of physical exercise',
            'frequency': HabitFrequency.DAILY,
            'target_count': 1,
            'streak_days': 8
        },
        {
            'name': 'Read 20 pages',
            'description': 'Read at least 20 pages from a book or educational material',
            'frequency': HabitFrequency.DAILY,
            'target_count': 1,
            'streak_days': 12
        },
        {
            'name': 'Meditate',
            'description': '10 minutes of mindfulness meditation',
            'frequency': HabitFrequency.DAILY,
            'target_count': 1,
            'streak_days': 5
        },
        {
            'name': 'Code for 1 hour',
            'description': 'Practice programming for at least 1 hour',
            'frequency': HabitFrequency.DAILY,
            'target_count': 1,
            'streak_days': 7
        },
        {
            'name': 'Weekly meal prep',
            'description': 'Prepare meals for the upcoming week',
            'frequency': HabitFrequency.WEEKLY,
            'target_count': 1,
            'streak_days': 3
        },
    ]
    
    for habit_data in habits_data:
        habit = Habit(
            user_id=user.id,
            name=habit_data['name'],
            description=habit_data['description'],
            frequency=habit_data['frequency'],
            target_count=habit_data['target_count']
        )
        db.session.add(habit)
        db.session.flush()  # Get the habit ID
        
        # Create habit logs for the streak
        current_date = date.today()
        for i in range(habit_data['streak_days']):
            log_date = current_date - timedelta(days=i)
            log = HabitLog(
                habit_id=habit.id,
                date_completed=log_date
            )
            db.session.add(log)
        
        # Add some missed days to make it more realistic
        if habit_data['streak_days'] > 5:
            for i in range(2):  # Add 2 missed days before the streak
                missed_date = current_date - timedelta(days=habit_data['streak_days'] + i + 1)
                # Randomly skip some days (don't add logs)
                if random.random() > 0.3:  # 70% chance of completion
                    log = HabitLog(
                        habit_id=habit.id,
                        date_completed=missed_date
                    )
                    db.session.add(log)
        
        habit.update_streak()