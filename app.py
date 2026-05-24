import os
import shelve
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_12345'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------------------------------------------
# PERMANENT LOCAL DATABASE INITIALIZATION
# ---------------------------------------------------------
DB_FILE = 'nnc_database.db'

def init_db():
    """Initializes the database files with default settings if they don't exist."""
    with shelve.open(DB_FILE, writeback=True) as db:
        if 'users' not in db:
            db['users'] = {
                "admin": {"name": "Supreme Leader", "password": "nazi_congress_admin"}
            }
        if 'roster' not in db:
            db['roster'] = {
                "admin": {"name": "Supreme Leader", "title": "Party Founder"}
            }
        if 'pending' not in db:
            db['pending'] = {}
        if 'website_data' not in db:
            db['website_data'] = {
                "manifesto_point_1": "1. Complete and total dedication to the unified structure of the Congress.",
                "manifesto_point_2": "2. Development of unbreakable economic and structural defense platforms.",
                "manifesto_point_3": "3. Promotion of elite training for all appointed branch secretaries.",
                "manifesto_point_4": "4. Expansion of infrastructure to match real-time live network capacity.",
                "manifesto_point_5": "5. Maintenance of absolute loyalty to the supreme executive command.",
                "ideology_1": "1. Absolute Order and Hierarchy within society.",
                "ideology_2": "2. Total Unbreakable Resilience against outside pressure.",
                "ideology_3": "3. Supreme Central Direction for fast execution.",
                "ideology_4": "4. National Technological Superiority across administrative networks.",
                "ideology_5": "5. Uncompromised economic self-reliance models.",
                "ideology_6": "6. Strategic placement of structural resources.",
                "ideology_7": "7. Elite selection protocols for party representatives.",
                "ideology_8": "8. Complete synchronization of collective community goals.",
                "ideology_9": "9. Deep-level data-driven civic management.",
                "ideology_10": "10. Preservation of supreme discipline in all ranks.",
                "banner_photo": "/static/uploads/default_banner.jpg"
            }
        if 'stats' not in db:
            db['stats'] = {"base_percentage": 14.7}

# Run database setup configuration
init_db()

# ---------------------------------------------------------
# ROUTING CONTROLLERS
# ---------------------------------------------------------

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        with shelve.open(DB_FILE) as db:
            users_db = db['users']
            if username in users_db and users_db[username]['password'] == password:
                session['username'] = username
                session['is_admin'] = (username == "admin")
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="Invalid website credentials.")
                
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        real_name = request.form.get('real_name')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not real_name or not username or not password:
            return render_template('register.html', error="All fields are required.")
            
        with shelve.open(DB_FILE, writeback=True) as db:
            if username in db['users']:
                return render_template('register.html', error="Username already registered.")
                
            db['users'][username] = {
                "name": real_name,
                "password": password
            }
        return redirect(url_for('login'))
        
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    current_user = session['username']
    
    with shelve.open(DB_FILE) as db:
        users_db = db['users']
        if current_user not in users_db:
            session.clear()
            return redirect(url_for('login'))
            
        is_admin = session.get('is_admin', False)
        congress_roster = db['roster']
        pending_applications = db['pending']
        website_data = db['website_data']
        party_stats = db['stats']
        
        is_in_party = current_user in congress_roster
        user_party_info = congress_roster.get(current_user, {"name": users_db[current_user]['name'], "title": "Standard Website Guest"})
        has_pending_app = current_user in pending_applications
        
        return render_template(
            'dashboard.html',
            username=current_user,
            user_info=user_party_info,
            is_admin=is_admin,
            is_in_party=is_in_party,
            has_pending_app=has_pending_app,
            all_members=congress_roster,
            pending_list=pending_applications,
            manifesto_1=website_data['manifesto_point_1'],
            manifesto_2=website_data['manifesto_point_2'],
            manifesto_3=website_data['manifesto_point_3'],
            manifesto_4=website_data['manifesto_point_4'],
            manifesto_5=website_data['manifesto_point_5'],
            
            id_1=website_data['ideology_1'], id_2=website_data['ideology_2'], id_3=website_data['ideology_3'],
            id_4=website_data['ideology_4'], id_5=website_data['ideology_5'], id_6=website_data['ideology_6'],
            id_7=website_data['ideology_7'], id_8=website_data['ideology_8'], id_9=website_data['ideology_9'],
            id_10=website_data['ideology_10'],
            
            banner_photo=website_data['banner_photo'],
            base_percentage=party_stats['base_percentage']
        )


@app.route('/ideology')
def ideology():
    if 'username' not in session:
        return redirect(url_for('login'))
    with shelve.open(DB_FILE) as db:
        return render_template('ideology.html', w_data=db['website_data'])


@app.route('/join_party', methods=['POST'])
def join_party():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    current_user = session['username']
    with shelve.open(DB_FILE, writeback=True) as db:
        if current_user not in db['roster'] and current_user not in db['pending']:
            db['pending'][current_user] = db['users'][current_user]['name']
            
    return redirect(url_for('dashboard'))


@app.route('/admin/approve/<target_username>', methods=['POST'])
def approve_member(target_username):
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
        
    with shelve.open(DB_FILE, writeback=True) as db:
        if target_username in db['pending']:
            real_name = db['pending'].pop(target_username)
            db['roster'][target_username] = {
                "name": real_name,
                "title": "Party Cadet"
            }
    return redirect(url_for('dashboard'))


@app.route('/admin/reject/<target_username>', methods=['POST'])
def reject_member(target_username):
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
        
    with shelve.open(DB_FILE, writeback=True) as db:
        if target_username in db['pending']:
            db['pending'].pop(target_username)
            
    return redirect(url_for('dashboard'))


@app.route('/admin/assign_title', methods=['POST'])
def assign_title():
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
        
    target_username = request.form.get('target_username')
    new_title = request.form.get('new_title')
    
    with shelve.open(DB_FILE, writeback=True) as db:
        if target_username in db['roster']:
            db['roster'][target_username]['title'] = new_title
            
    return redirect(url_for('dashboard'))


@app.route('/admin/update_manifesto', methods=['POST'])
def update_manifesto():
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
        
    with shelve.open(DB_FILE, writeback=True) as db:
        db['website_data']['manifesto_point_1'] = request.form.get('m1')
        db['website_data']['manifesto_point_2'] = request.form.get('m2')
        db['website_data']['manifesto_point_3'] = request.form.get('m3')
        db['website_data']['manifesto_point_4'] = request.form.get('m4')
        db['website_data']['manifesto_point_5'] = request.form.get('m5')
        
    return redirect(url_for('dashboard'))


@app.route('/admin/update_ideology', methods=['POST'])
def update_ideology():
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
        
    with shelve.open(DB_FILE, writeback=True) as db:
        for i in range(1, 11):
            db['website_data'][f'ideology_{i}'] = request.form.get(f'id_{i}')
            
    return redirect(url_for('dashboard'))


@app.route('/admin/upload_photo', methods=['POST'])
def upload_photo():
    if 'username' not in session or not session.get('is_admin', False):
        return redirect(url_for('login'))
        
    if 'party_photo' not in request.files:
        return redirect(url_for('dashboard'))
        
    file = request.files['party_photo']
    if file and file.filename != '':
        filename = "uploaded_party_banner.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        import time
        with shelve.open(DB_FILE, writeback=True) as db:
            db['website_data']['banner_photo'] = f"/static/uploads/{filename}?t={int(time.time())}"
        
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000) 
