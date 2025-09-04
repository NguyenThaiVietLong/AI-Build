from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app import db
from app.models import Transaction, Category, TransactionType
from app.forms import TransactionForm, CategoryForm
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc, extract
import csv
import io

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/')
@login_required
def list_transactions():
    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type', 'all')
    category_filter = request.args.get('category', 'all')
    
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    if type_filter != 'all':
        query = query.filter_by(type=TransactionType(type_filter))
    
    if category_filter != 'all':
        query = query.filter_by(category_id=category_filter)
    
    transactions = query.order_by(desc(Transaction.transaction_date))\
                       .paginate(page=page, per_page=20, error_out=False)
    
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    return render_template('transactions/list.html', 
                         transactions=transactions,
                         categories=categories,
                         type_filter=type_filter,
                         category_filter=category_filter)

@transactions_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_transaction():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form = TransactionForm(categories=categories)
    
    if form.validate_on_submit():
        if form.type.data == 'Expense':
            current_balance = current_user.get_balance()
            if float(form.amount.data) > current_balance:
                flash('Insufficient funds! Current balance: ${:.2f}'.format(current_balance), 'error')
                return render_template('transactions/create.html', form=form)
        
        transaction = Transaction(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount=form.amount.data,
            type=TransactionType(form.type.data),
            description=form.description.data,
            transaction_date=form.transaction_date.data,
            receipt_url=form.receipt_url.data
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction recorded successfully!', 'success')
        return redirect(url_for('transactions.list_transactions'))
    
    return render_template('transactions/create.html', form=form)

@transactions_bp.route('/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    form = TransactionForm(categories=categories, obj=transaction)
    form.type.data = transaction.type.value
    
    if form.validate_on_submit():
        transaction.category_id = form.category_id.data
        transaction.amount = form.amount.data
        transaction.type = TransactionType(form.type.data)
        transaction.description = form.description.data
        transaction.transaction_date = form.transaction_date.data
        transaction.receipt_url = form.receipt_url.data
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.list_transactions'))
    
    return render_template('transactions/edit.html', form=form, transaction=transaction)

@transactions_bp.route('/<id>/delete', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('transactions.list_transactions'))

@transactions_bp.route('/categories')
@login_required
def list_categories():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('transactions/categories.html', categories=categories)

@transactions_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        existing_category = Category.query.filter_by(
            user_id=current_user.id, 
            name=form.name.data
        ).first()
        
        if existing_category:
            flash('Category name already exists', 'error')
        else:
            category = Category(
                user_id=current_user.id,
                name=form.name.data,
                color=form.color.data,
                icon=form.icon.data
            )
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
            return redirect(url_for('transactions.list_categories'))
    
    return render_template('transactions/create_category.html', form=form)

@transactions_bp.route('/categories/<id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Check if category has transactions
    transaction_count = Transaction.query.filter_by(category_id=category.id).count()
    if transaction_count > 0:
        flash(f'Cannot delete category. It has {transaction_count} transactions.', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    
    return redirect(url_for('transactions.list_categories'))

@transactions_bp.route('/summary')
@login_required
def summary():
    # Monthly summary for current year
    current_year = datetime.now().year
    monthly_data = db.session.query(
        extract('month', Transaction.transaction_date).label('month'),
        Transaction.type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        extract('year', Transaction.transaction_date) == current_year
    ).group_by('month', Transaction.type).all()
    
    # Category breakdown for last 30 days
    thirty_days_ago = date.today() - timedelta(days=30)
    category_data = db.session.query(
        Category.name,
        Category.color,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.transaction_date >= thirty_days_ago
    ).group_by(Category.id).all()
    
    return render_template('transactions/summary.html',
                         monthly_data=monthly_data,
                         category_data=category_data,
                         current_year=current_year)

@transactions_bp.route('/export')
@login_required
def export_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
                                  .order_by(desc(Transaction.transaction_date)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Type', 'Amount', 'Category', 'Description'])
    
    # Write data
    for transaction in transactions:
        writer.writerow([
            transaction.transaction_date.strftime('%Y-%m-%d'),
            transaction.type.value,
            float(transaction.amount),
            transaction.category.name,
            transaction.description or ''
        ])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=transactions_{date.today().strftime("%Y%m%d")}.csv'
    
    return response