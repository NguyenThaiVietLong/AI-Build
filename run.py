from app import create_app, db
from app.models import User, Goal, Milestone, Transaction, Category, Habit, HabitLog
import os

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Goal': Goal, 
        'Milestone': Milestone,
        'Transaction': Transaction, 
        'Category': Category, 
        'Habit': Habit, 
        'HabitLog': HabitLog
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        from app.sample_data import create_sample_data
        if not User.query.first():
            create_sample_data()
            
    app.run(debug=True, host='0.0.0.0', port=5000)