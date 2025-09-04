from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Goal, Milestone, GoalStatus
from app.forms import GoalForm, MilestoneForm
from datetime import datetime

goals_bp = Blueprint('goals', __name__)

@goals_bp.route('/')
@login_required
def list_goals():
    status_filter = request.args.get('status', 'all')
    
    query = Goal.query.filter_by(user_id=current_user.id)
    if status_filter != 'all':
        if status_filter == 'active':
            query = query.filter_by(status=GoalStatus.ACTIVE)
        elif status_filter == 'completed':
            query = query.filter_by(status=GoalStatus.COMPLETED)
        elif status_filter == 'paused':
            query = query.filter_by(status=GoalStatus.PAUSED)
    
    goals = query.order_by(Goal.created_at.desc()).all()
    return render_template('goals/list.html', goals=goals, status_filter=status_filter)

@goals_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_goal():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            target_date=form.target_date.data
        )
        db.session.add(goal)
        db.session.commit()
        flash('Goal created successfully!', 'success')
        return redirect(url_for('goals.view_goal', id=goal.id))
    
    return render_template('goals/create.html', form=form)

@goals_bp.route('/<id>')
@login_required
def view_goal(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    milestones = Milestone.query.filter_by(goal_id=goal.id).order_by(Milestone.target_date).all()
    return render_template('goals/view.html', goal=goal, milestones=milestones)

@goals_bp.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_goal(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = GoalForm(obj=goal)
    
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.description = form.description.data
        goal.target_date = form.target_date.data
        goal.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Goal updated successfully!', 'success')
        return redirect(url_for('goals.view_goal', id=goal.id))
    
    return render_template('goals/edit.html', form=form, goal=goal)

@goals_bp.route('/<id>/delete', methods=['POST'])
@login_required
def delete_goal(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('goals.list_goals'))

@goals_bp.route('/<id>/status', methods=['POST'])
@login_required
def update_status(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    new_status = request.json.get('status')
    
    if new_status in [s.value for s in GoalStatus]:
        goal.status = GoalStatus(new_status)
        goal.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': f'Goal marked as {new_status.lower()}'})
    
    return jsonify({'success': False, 'message': 'Invalid status'}), 400

@goals_bp.route('/<goal_id>/milestones/create', methods=['GET', 'POST'])
@login_required
def create_milestone(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    form = MilestoneForm()
    
    if form.validate_on_submit():
        milestone = Milestone(
            goal_id=goal.id,
            title=form.title.data,
            description=form.description.data,
            target_date=form.target_date.data
        )
        db.session.add(milestone)
        db.session.commit()
        goal.update_progress()
        db.session.commit()
        flash('Milestone created successfully!', 'success')
        return redirect(url_for('goals.view_goal', id=goal.id))
    
    return render_template('goals/create_milestone.html', form=form, goal=goal)

@goals_bp.route('/milestones/<id>/complete', methods=['POST'])
@login_required
def complete_milestone(id):
    milestone = Milestone.query.join(Goal).filter(
        Milestone.id == id,
        Goal.user_id == current_user.id
    ).first_or_404()
    
    milestone.mark_complete()
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Milestone completed!',
        'goal_progress': milestone.goal.progress_percentage
    })

@goals_bp.route('/milestones/<id>/delete', methods=['POST'])
@login_required
def delete_milestone(id):
    milestone = Milestone.query.join(Goal).filter(
        Milestone.id == id,
        Goal.user_id == current_user.id
    ).first_or_404()
    
    goal = milestone.goal
    db.session.delete(milestone)
    db.session.commit()
    goal.update_progress()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Milestone deleted successfully!'})