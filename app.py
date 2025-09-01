import csv
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import smtplib

app = Flask(__name__)
app.config.from_object(Config)

USER_FILE = 'data/users.csv'

# --- Routes ---

@app.route('/')
def home():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = find_user_by_id(user_id)
    if not user:
        return redirect(url_for('logout'))
        
    return render_template('home.html', user_name=user['name'])

@app.route('/child')
def child_home():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = find_user_by_id(user_id)
    choice = user.get('parent_choice')

    if choice and choice in ['game', 'puzzle', 'story']:
        # If parent has made a choice, redirect directly to that activity
        return redirect(url_for(choice)) # e.g., redirect to /puzzle
    else:
        # Otherwise, show the child the main activity hub
        return render_template('child.html')

@app.route('/puzzle')
def puzzle():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('puzzle.html')

@app.route('/game')
def game():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('game.html')

@app.route('/story')
def story():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('story.html')

@app.route('/complete_task')
def complete_task():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = find_user_by_id(user_id)
    activity = request.args.get('activity', 'adventure') # e.g., 'puzzle'

    # Send the email
    send_success_email(user['email'], activity)

    # Reset the parent's choice so the loop can start again
    update_user_choice(user_id, '') # Pass an empty string to clear it
    
    flash("Great job! Your parent has been notified of your success.")
    return redirect(url_for('home'))

@app.route('/parent')
def parent():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    choice = request.args.get('choice')
    
    if choice in ['game', 'story', 'puzzle']:
        # Update the user's choice in the CSV
        update_user_choice(user_id, choice)
        
        flash(f"Preference saved! The '{choice}' quest is ready for your child.")
        
        return redirect(url_for('home'))

    return render_template('parent.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if find_user_by_email(email):
            flash('Email already registered.')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        
        new_user = {
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'parent_choice': '',
            'last_accessed': datetime.utcnow().isoformat()
        }
        
        add_user_to_csv(new_user)
        
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = find_user_by_email(email)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

def find_user_by_email(email):
    with open(USER_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for user in reader:
            if user['email'] == email:
                return user
    return None

def add_user_to_csv(user_dict):
    with open(USER_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=user_dict.keys())
        writer.writerow(user_dict)

def find_user_by_id(user_id):
    with open(USER_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for user in reader:
            if user['id'] == user_id:
                return user
    return None

def update_user_choice(user_id, choice):
    rows = []
    user_found = False
    
    with open(USER_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['id'] == user_id:
                row['parent_choice'] = choice
                row['last_accessed'] = datetime.utcnow().isoformat()
                user_found = True
            rows.append(row)
    
    if not user_found:
        return False

    with open(USER_FILE, mode='w', newline='') as file:
        # Get headers from the first row dictionary's keys
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        
    return True

def send_success_email(user_email, activity):
    sender_email = "d6mr07@gmail.com"
    password = "twqm whle nxhn owig"
    
    if not password:
        print("EMAIL NOT SENT: Please configure sender_email and password in app.py")
        return

    message = f"Subject: Quest Complete!\n\nYour child has successfully completed their {activity} quest. Great job, team!"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, user_email, message)
        print(f"Completion email sent to {user_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    app.run(debug=True)