from flask import (
    Flask, request, jsonify, render_template,
    redirect, session, url_for
)
from flask_pymongo import PyMongo
from flask_cors import CORS
import webbrowser
import threading
import secrets
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Secret key for session encryption
app.secret_key = secrets.token_hex(16)

# MongoDB Atlas connection
# MongoDB Atlas connection
app.config["MONGO_URI"] = "mongodb+srv://praveen01388:Welcome%40573@cluster0.ub5oqqi.mongodb.net/Travelbuddy?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)
users_collection = mongo.db.users

# ─── Register API ─────────────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email    = data.get('email')
    password = data.get('password')
    full_name = data.get('fullName')
    travel_preferences  = data.get('travelPreferences')
    travel_destination  = data.get('travelDestination')
    travel_dates        = data.get('travelDates')
    
    gender              = data.get('gender')

    if not username or not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    if users_collection.find_one({'$or': [
        {'username': username},
        {'email': email}
    ]}):
        return jsonify({'message': 'User already exists'}), 400

    users_collection.insert_one({
        'username': username,
        'email': email,
        'password': password,
        'full_name': full_name,
        'travel_preferences': travel_preferences,
        'travel_destination': travel_destination,
        'travel_dates': {
            'start': datetime.strptime(travel_dates['start'], '%Y-%m-%d'),
            'end':   datetime.strptime(travel_dates['end'],   '%Y-%m-%d')
        },
        'gender': gender
    })

    return jsonify({'message': 'Registration successful'}), 200

# ─── Login API ────────────────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    user = users_collection.find_one({'username': username})
    if user and user['password'] == password:
        # Store user info in session
        session.update({
            'username': user['username'],
            'email': user['email'],
            'fullName': user.get('full_name'),
            'travelPreferences': user.get('travel_preferences'),
            'travelDestination': user.get('travel_destination'),
            'travelDates': {
                'start': user['travel_dates']['start'].strftime('%Y-%m-%d'),
                'end':   user['travel_dates']['end'].strftime('%Y-%m-%d')
            },
            'gender': user.get('gender')
        })
        return jsonify({
            'message': 'Login successful',
            'user': session  # send back the same session data
        }), 200

    return jsonify({'message': 'Invalid credentials'}), 401

# ─── Logout Route ─────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('root'))

# ─── Root Redirect ────────────────────────────────────────────────────
@app.route('/')
def root():
    if 'username' in session:
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('travel_user_details'))

# ─── NEW: force-show registration page ─────────────────────────────────
@app.route('/register', endpoint='register_page')
def _force_register():
    return render_template('traveluserdetails.html')

# ─── traveluserdetails.html (registration/login page) ────────────────
@app.route('/traveluserdetails')
def travel_user_details():
    if 'username' in session:
        return redirect(url_for('user_dashboard'))
    return render_template('traveluserdetails.html')

# ─── user.html (dashboard) ────────────────────────────────────────────
@app.route('/user')
def user_dashboard():
    if 'username' not in session:
        return redirect(url_for('travel_user_details'))
    return render_template('user.html', user=session)

# ─── travelpartner.html (search form) ─────────────────────────────────
@app.route('/travel-partner')
def travel_partner():
    if 'username' not in session:
        return redirect(url_for('travel_user_details'))
    return render_template('travelpartner.html')

# ─── NEW: Find My Buddy Logic ─────────────────────────────────────────
@app.route('/find-buddy', methods=['POST'])
def find_buddy():
    # 1. Extract form fields
    dest      = request.form.get('preferredDestination', '')
    start_str = request.form.get('startDate', '')
    end_str   = request.form.get('endDate', '')
    prefs     = request.form.get('preferences', '')
    gender    = request.form.get('buddyGender', 'any')

    # 2. Parse dates
    try:
        start_dt = datetime.strptime(start_str, '%Y-%m-%d')
        end_dt   = datetime.strptime(end_str,   '%Y-%m-%d')
    except ValueError:
        return "Invalid date format", 400

    # 3. Build MongoDB query
    query = {
        'travel_destination': { '$regex': dest, '$options': 'i' },
        'travel_dates.start': { '$lte': start_dt },
        'travel_dates.end':   { '$gte': end_dt }
    }
    if prefs:
        query['travel_preferences'] = { '$regex': prefs, '$options': 'i' }
   # Use case-insensitive gender matching if not "any"
    if gender and gender.lower() != 'any':
        query['gender'] = { '$regex': f'^{gender}$', '$options': 'i' }


    # 4. Fetch matches
    matches = list(users_collection.find(query))

    # 5. Render results.html with match list
    return render_template('results.html', users=matches)

# ─── Auto-open Browser ────────────────────────────────────────────────
def open_browser():
    webbrowser.open_new_tab("http://127.0.0.1:5000/")

if __name__ == '__main__':
    threading.Timer(3, open_browser).start()
    app.run(debug=True, use_reloader=False)
