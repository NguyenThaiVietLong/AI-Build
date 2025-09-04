from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Habit, HabitLog, HabitFrequency
from app.forms import HabitForm, HabitCheckInForm
from datetime import datetime, date, timedelta
from sqlalchemy import desc, func

habits_bp = Blueprint('habits', __name__)

@habits_bp.route('/')
@login_required
def list_habits():
    active_only = request.args.get('active', 'true') == 'true'
    
    query = Habit.query.filter_by(user_id=current_user.id)
    if active_only:
        query = query.filter_by(is_active=True)
    
    habits = query.order_by(Habit.created_at.desc()).all()
    
    # Check today's completion status for each habit
    today = date.today()
    for habit in habits:
        habit.completed_today = HabitLog.query.filter_by(
            habit_id=habit.id,
            date_completed=today
        ).first() is not None
    
    return render_template('habits/list.html', habits=habits, active_only=active_only)

@habits_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_habit():
    # Check habit limit
    active_habits_count = Habit.query.filter_by(user_id=current_user.id, is_active=True).count()
    if active_habits_count >= 20:
        flash('Maximum habits reached (20). Please deactivate some habits first.', 'error')
        return redirect(url_for('habits.list_habits'))
    
    form = HabitForm()
    if form.validate_on_submit():
        # Check for duplicate habit name
        existing_habit = Habit.query.filter_by(
            user_id=current_user.id,
            name=form.name.data
        ).first()
        
        if existing_habit:
            flash('Habit name already exists', 'error')
        else:
            habit = Habit(
                user_id=current_user.id,
                name=form.name.data,
                description=form.description.data,
                frequency=HabitFrequency(form.frequency.data),
                target_count=form.target_count.data,
                reminder_time=form.reminder_time.data
            )
            db.session.add(habit)
            db.session.commit()
            flash('Habit created successfully!', 'success')
            return redirect(url_for('habits.view_habit', id=habit.id))
    
    return render_template('habits/create.html', form=form)

@habits_bp.route('/<id>')
@login_required
def view_habit(id):
    habit = Habit.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Get recent logs (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    recent_logs = HabitLog.query.filter_by(habit_id=habit.id)\
                               .filter(HabitLog.date_completed >= thirty_days_ago)\
                               .order_by(desc(HabitLog.date_completed)).all()
    
    # Calculate completion rate
    completion_rate = habit.get_completion_rate()
    
    # Check if completed today
    completed_today = HabitLog.query.filter_by(
        habit_id=habit.id,
        date_completed=date.today()
    ).first() is not None
    
    return render_template('habits/view.html', 
                         habit=habit, 
                         recent_logs=recent_logs,
                         completion_rate=completion_rate,
                         completed_today=completed_today)

@habits_bp.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_habit(id):
    habit = Habit.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = HabitForm(obj=habit)
    form.frequency.data = habit.frequency.value
    
    if form.validate_on_submit():
        habit.name = form.name.data
        habit.description = form.description.data
        habit.frequency = HabitFrequency(form.frequency.data)
        
        habit.reminder_time = form.reminder_time.data
        db.session.commit()
        flash('Habit updated successfully!', 'success')
        return redirect(url_for('habits.view_habit', id=habit.id))
    
    return render_template('habits/edit.html', form=form, habit=habit)

@habits_bp.route('/<id>/toggle', methods=['POST'])
@login_required
def toggle_habit(id):
    habit = Habit.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    habit.is_active = not habit.is_active
    db.session.commit()
    
    status = 'activated' if habit.is_active else 'deactivated'
    flash(f'Habit {status} successfully!', 'success')
    return redirect(url_for('habits.list_habits'))

@habits_bp.route('/<id>/delete', methods=['POST'])
@login_required
def delete_habit(id):
    habit = Habit.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(habit)
    db.session.commit()
    flash('Habit deleted successfully!', 'success')
    return redirect(url_for('habits.list_habits'))

@habits_bp.route('/<id>/checkin', methods=['POST'])
@login_required
def checkin_habit(id):
    habit = Habit.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    checkin_date = request.json.get('date')
    if checkin_date:
        try:
            checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format'}), 400
    else:
        checkin_date = date.today()
    
    success = habit.check_in(checkin_date)
    
    if success:
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Habit checked in successfully!',
            'current_streak': habit.current_streak,
            'longest_streak': habit.longest_streak
        })
    else:
        return jsonify({
            'success': False, 
            'message': 'Already checked in for this date'
        }), 400

@habits_bp.route('/checkin/<log_id>', methods=['DELETE'])
@login_required
def remove_checkin(log_id):
    log = HabitLog.query.join(Habit).filter(
        HabitLog.id == log_id,
        Habit.user_id == current_user.id
    ).first_or_404()
    
    habit = log.habit
    db.session.delete(log)
    habit.update_streak()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Check-in removed successfully!'})

@habits_bp.route('/calendar')
@login_required
def calendar_view():
    # Get all habits for the current user
    habits = Habit.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    # Get habit logs for the last 3 months
    three_months_ago = date.today() - timedelta(days=90)
    logs = db.session.query(HabitLog)\
                    .join(Habit)\
                    .filter(Habit.user_id == current_user.id,
                           HabitLog.date_completed >= three_months_ago)\
                    .all()
    
    # Organize logs by date and habit
    calendar_data = {}
    for log in logs:
        date_str = log.date_completed.strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        calendar_data[date_str].append({
            'habit_id': log.habit_id,
            'habit_name': log.habit.name
        })
    
    return render_template('habits/calendar.html', 
                         habits=habits, 
                         calendar_data=calendar_data)