from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

app = Flask(__name__)
app.secret_key = 'renzqtpie'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pisopulse_initial_user:o67hHm9MnimaUREyldU4qv1vPY4YeJ6I@dpg-d7eggj5ckfvc73fc2img-a.oregon-postgres.render.com/pisopulse_initial'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    expenses = db.relationship(
        'Expense',
        backref='user',
        lazy=True
    )

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    description = db.Column(db.String(300))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Expense %r>' % self.id
    
@app.route('/')
def home():
    return redirect('/login')

@app.route('/expenses')
def expenses():
    if 'user_id' not in session:
        return redirect('/login')

    selected_date_str = request.args.get('date')

    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d')
    else:
        selected_date = datetime.today()

    expenses = Expense.query.filter_by(
        user_id=session['user_id']
    ).filter(
        db.func.date(Expense.date) == selected_date.date()
    ).all()

    return render_template(
        'index.html',
        expenses=expenses,
        selected_date_raw=selected_date.strftime('%Y-%m-%d'),   # for JS
        selected_date_pretty=selected_date.strftime('%b %d, %Y') # for display
    )

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    selected_date_str = request.args.get('date')

    if request.method == 'POST':
        date_str = request.form['date']
        date = datetime.strptime(date_str, '%Y-%m-%d')

        amounts = request.form.getlist('amount[]')
        descriptions = request.form.getlist('description[]')

        for amount, description in zip(amounts, descriptions):
            new_expense = Expense(
                amount=float(amount),
                description=description,
                date=date,
                user_id=session['user_id']
            )
            db.session.add(new_expense)

        db.session.commit()

        return redirect('/expenses?date=' + date.strftime('%Y-%m-%d'))

    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d')
        default_date = selected_date.strftime('%Y-%m-%d')
    else:
        default_date = datetime.today().strftime('%Y-%m-%d')

    return render_template('add_expense.html', today=default_date)


@app.route('/user-expenses', methods=['GET'])
def user_expenses():
    users = User.query.all()
    selected_user_id = request.args.get('user_id')

    selected_date_str = request.args.get('date')

    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d')
    else:
        selected_date = datetime.today()

    expenses = []

    if selected_user_id:
        expenses = Expense.query.filter_by(
            user_id=selected_user_id
        ).filter(
            db.func.date(Expense.date) == selected_date.date()
        ).all()

    return render_template(
        'user_expenses.html',
        users=users,
        expenses=expenses,
        selected_user_id=selected_user_id,
        selected_date_raw=selected_date.strftime('%Y-%m-%d'),
        selected_date_pretty=selected_date.strftime('%b %d, %Y')
    )


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)

    if request.method == 'POST':
        expense.amount = float(request.form['amount'])
        expense.description = request.form['description']
        expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d')

        db.session.commit()
        return redirect('/expenses?date=' + expense.date.strftime('%Y-%m-%d'))

    return render_template('edit.html', expense=expense)


@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)

    db.session.delete(expense)
    db.session.commit()

    return redirect('/expenses?date=' + expense.date.strftime('%Y-%m-%d'))


@app.route('/dashboard')
def dashboard():
    expenses = Expense.query.all()

    # structure:
    # {date: {user: total}}
    data = {}
    users = set()

    for expense in expenses:
        date = expense.date.strftime('%Y-%m-%d')
        user = expense.user.username
        
        users.add(user)

        if date not in data:
            data[date] = {}

        if user not in data[date]:
            data[date][user] = 0

        data[date][user] += expense.amount

    # sort dates
    sorted_dates = sorted(data.keys())

    formatted_dates = [
        {
            "raw": date,
            "pretty": datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
        }
        for date in sorted_dates
    ]

    # sort users
    users = sorted(users)

    return render_template(
        'dashboard.html',
        data=data,
        dates=formatted_dates,
        users=users
    )



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        user = User(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect('/expenses')
        else:
            error = "Invalid username or password"

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        return redirect('/login')

    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/delete-user/<int:id>', methods=['POST'])
def admin_delete_user(id):
    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get_or_404(id)

    # delete all user's expenses first
    Expense.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    return redirect('/admin')

if __name__ == "__main__":
    app.run(debug=True)