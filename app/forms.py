from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateField, SelectField, DecimalField, IntegerField, BooleanField, TimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional
from datetime import date, datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])

class GoalForm(FlaskForm):
    title = StringField('Goal Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    target_date = DateField('Target Date', validators=[Optional()], default=None)

class MilestoneForm(FlaskForm):
    title = StringField('Milestone Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    target_date = DateField('Target Date', validators=[Optional()], default=None)

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    color = StringField('Color', validators=[Optional(), Length(max=7)], default='#6B7280')
    icon = StringField('Icon', validators=[Optional(), Length(max=50)], default='📊')

class TransactionForm(FlaskForm):
    type = SelectField('Type', choices=[('Income', 'Income'), ('Expense', 'Expense')], 
                      validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    category_id = SelectField('Category', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional(), Length(max=500)])
    transaction_date = DateField('Date', validators=[DataRequired()], default=date.today)
    receipt_url = StringField('Receipt URL', validators=[Optional(), Length(max=500)])
    
    def __init__(self, categories=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if categories:
            self.category_id.choices = [(c.id, c.name) for c in categories]

class HabitForm(FlaskForm):
    name = StringField('Habit Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    frequency = SelectField('Frequency', 
                           choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')],
                           validators=[DataRequired()], default='Daily')
    time_unit = SelectField('Time Unit', 
                           choices=[('Minute', 'Minute'), ('Hour', 'Hour')],
                           validators=[Optional()], default='Minute')
    time_value = IntegerField('Time Value', validators=[Optional(), NumberRange(min=1)], default=1)
    reminder_time = TimeField('Reminder Time', validators=[Optional()])

class HabitCheckInForm(FlaskForm):
    date_completed = DateField('Date Completed', validators=[DataRequired()], default=date.today)
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])