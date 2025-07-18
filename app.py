import sqlite3
from flask import Flask, render_template, request
from flask import redirect, url_for, session, flash
import bcrypt
from functools import wraps
from datetime import datetime, timedelta
import re

database_name = "merits.db"
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

houses = [
    "CHELMSFORD", "CUTLER", "DAVIDSON", "HARVEY", "HEWAN", "HONE",
    "NORTHCOTT", "PERKINS", "RAWSON", "STREET", "STRICKLAND",
    "THOMAS", "WAKEHURST", "WOODWARD"
]


@app.route('/db')
def home():
    connection = sqlite3.connect(database_name)
    connection.row_factory = sqlite3.Row
    query = "SELECT * FROM sqlite_master WHERE type='table'"
    tables = connection.execute(query).fetchall()
    database = []
    for table in tables:
        query = "SELECT name FROM PRAGMA_TABLE_INFO('{}');".format(table[1])
        columns = connection.execute(query).fetchall()

        query = "SELECT * FROM {}".format(table[1])
        rows = connection.execute(query).fetchall()

        database.append((table[1], columns, rows))

    return render_template('print_database.html', database=database)


def award_merit(StudentName, grade, house, reason, awarded_by):
    StudentName = StudentName.upper()
    date = datetime.now().strftime('%Y-%m-%d')
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    new_merit = (StudentName, grade, house, reason, awarded_by, date)
    query = "INSERT INTO Merits (StudentName, Grade, House, Reason, awarded_by, date) VALUES (?, ?, ?, ?, ?, ?);"
    connection.execute(query, new_merit)
    connection.commit()
    connection.close()

def award_demerit(StudentName, grade, house, reason, awarded_by):
    StudentName = StudentName.upper()
    date = datetime.now().strftime('%Y-%m-%d')
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    new_demerit = (StudentName, grade, house, reason, awarded_by, date)
    query = "INSERT INTO Demerits (StudentName, Grade, House, Reason, awarded_by, date) VALUES (?, ?, ?, ?, ?, ?);"
    connection.execute(query, new_demerit)
    connection.commit()
    connection.close()

def get_merit_history(username):
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    merits = connection.execute('SELECT * FROM Merits WHERE awarded_by = ? ORDER BY date DESC, ID DESC', (username,)).fetchall()
    connection.close()
    return merits

def get_demerit_history(username):
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    demerits = connection.execute('SELECT * FROM Demerits WHERE awarded_by = ? ORDER BY date DESC, ID DESC', (username,)).fetchall()
    connection.close()
    return demerits


def get_user_by_username(username):
    connection = sqlite3.connect('users.db')
    user = connection.execute('SELECT id, username, password_hash, role FROM users WHERE username = ?', (username,)).fetchone()
    connection.close()
    return user

def is_logged_in():
    return 'user_id' in session

def get_role():
    return session.get('role', 'Teacher')

def is_admin():
    return get_role() == 'admin'

def is_valid_password(password):
    if len(password) < 10:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[^A-Za-z0-9]', password):
        return False
    return True

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in() or not is_admin():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/create-user', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        house = request.form.get('house')
        year_group = request.form.get('year_group')
        if role not in ['Housemaster', 'Mentor']:
            house = None
        if role != 'Mentor':
            year_group = None
        if not is_valid_password(password):
            flash('Password must be at least 10 characters long, contain a capital letter, a lowercase letter, and a special character.', 'danger')
            return render_template('create_user.html', houses=houses)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        connection = sqlite3.connect('users.db')
        try:
            connection.execute('INSERT INTO users (username, password_hash, role, house, year_group) VALUES (?, ?, ?, ?, ?)', (username, password_hash, role, house, year_group))
            connection.commit()
            flash('User created successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'danger')
        connection.close()
    return render_template('create_user.html', houses=houses)

@app.route('/')
@login_required
def index():
    return render_template('home.html', logged_in=True, is_admin=is_admin(), username=session.get('username'))

@app.route('/account')
@login_required
def account():
    username = session.get('username')
    merits = get_merit_history(username)
    demerits = get_demerit_history(username)
    return render_template('account.html', username=username, role=get_role(), is_admin=is_admin(), merits=merits, demerits=demerits)

# Protect all other routes except login, logout, and static
@app.route('/award-merit')
@login_required
def award_merit_page():
    return render_template('award_merit.html', houses=houses)

@app.route('/award-demerit')
@login_required
def award_demerit_page():
    return render_template('award_demerit.html', houses=houses)

def get_student_merits(student_name):
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    merits = connection.execute('SELECT * FROM Merits WHERE StudentName = ? ORDER BY date DESC, ID DESC', (student_name,)).fetchall()
    connection.close()
    return merits

def get_student_demerits(student_name):
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    demerits = connection.execute('SELECT * FROM Demerits WHERE StudentName = ? ORDER BY date DESC, ID DESC', (student_name,)).fetchall()
    connection.close()
    return demerits

def get_current_term():
    connection = sqlite3.connect('school.db')
    connection.row_factory = sqlite3.Row
    today = datetime.now().strftime('%Y-%m-%d')
    # Try to find current term
    term = connection.execute('SELECT * FROM terms WHERE start_date <= ? AND end_date >= ? ORDER BY year DESC, term_number DESC LIMIT 1', (today, today)).fetchone()
    if term:
        connection.close()
        return term, False
    # If not found, get the most recent previous term
    term = connection.execute('SELECT * FROM terms WHERE end_date < ? ORDER BY end_date DESC LIMIT 1', (today,)).fetchone()
    connection.close()
    if term:
        return term, True
    return None, False

def get_week_dates():
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.strftime('%Y-%m-%d'), end_of_week.strftime('%Y-%m-%d')

def get_year_dates():
    today = datetime.now()
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)
    return start_of_year.strftime('%Y-%m-%d'), end_of_year.strftime('%Y-%m-%d')

def filter_students_by_date(students, start_date, end_date):
    filtered_students = {}
    for student_name, student_data in students.items():
        # Get merits and demerits for this student within date range
        connection = sqlite3.connect('awards.db')
        connection.row_factory = sqlite3.Row
        merits = connection.execute('SELECT * FROM Merits WHERE StudentName = ? AND date >= ? AND date <= ? ORDER BY date DESC', 
                                  (student_name, start_date, end_date)).fetchall()
        connection.close()
        
        connection = sqlite3.connect('awards.db')
        connection.row_factory = sqlite3.Row
        demerits = connection.execute('SELECT * FROM Demerits WHERE StudentName = ? AND date >= ? AND date <= ? ORDER BY date DESC', 
                                    (student_name, start_date, end_date)).fetchall()
        connection.close()
        
        if merits or demerits:
            student_data['merits'] = merits
            student_data['demerits'] = demerits
            filtered_students[student_name] = student_data
    
    return filtered_students

def count_demerits_this_week(student_name):
    start_date, end_date = get_week_dates()
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    count = connection.execute('SELECT COUNT(*) FROM Demerits WHERE StudentName = ? AND date >= ? AND date <= ?', (student_name, start_date, end_date)).fetchone()[0]
    connection.close()
    return count

def filter_students_by_date_grouped(students, start_date, end_date):
    filtered_students = {}
    for key, student_data in students.items():
        name, house, grade = student_data['name'], student_data['house'], student_data['grade']
        connection = sqlite3.connect('awards.db')
        connection.row_factory = sqlite3.Row
        merits = connection.execute('SELECT * FROM Merits WHERE StudentName = ? AND House = ? AND Grade = ? AND date >= ? AND date <= ? ORDER BY date DESC',
                                   (name, house, grade, start_date, end_date)).fetchall()
        connection.close()
        connection = sqlite3.connect('awards.db')
        connection.row_factory = sqlite3.Row
        demerits = connection.execute('SELECT * FROM Demerits WHERE StudentName = ? AND House = ? AND Grade = ? AND date >= ? AND date <= ? ORDER BY date DESC',
                                      (name, house, grade, start_date, end_date)).fetchall()
        connection.close()
        if merits or demerits:
            student_data['merits'] = merits
            student_data['demerits'] = demerits
            filtered_students[key] = student_data
    return filtered_students

def count_demerits_this_week_grouped(name, house, grade):
    start_date, end_date = get_week_dates()
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    count = connection.execute('SELECT COUNT(*) FROM Demerits WHERE StudentName = ? AND House = ? AND Grade = ? AND date >= ? AND date <= ?',
                              (name, house, grade, start_date, end_date)).fetchone()[0]
    connection.close()
    return count

def get_house_merit_count(house, start_date, end_date):
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    merits = connection.execute('SELECT COUNT(*) FROM Merits WHERE House = ? AND date >= ? AND date <= ?', (house, start_date, end_date)).fetchone()[0]
    demerits = connection.execute('SELECT COUNT(*) FROM Demerits WHERE House = ? AND date >= ? AND date <= ?', (house, start_date, end_date)).fetchone()[0]
    connection.close()
    return merits - demerits

def get_yeargroup_house_merit_counts(year_group, start_date, end_date):
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    houses = set([row['House'] for row in connection.execute('SELECT DISTINCT House FROM Merits WHERE Grade = ?', (year_group,))])
    houses.update([row['House'] for row in connection.execute('SELECT DISTINCT House FROM Demerits WHERE Grade = ?', (year_group,))])
    house_counts = {}
    for house in houses:
        merits = connection.execute('SELECT COUNT(*) FROM Merits WHERE House = ? AND Grade = ? AND date >= ? AND date <= ?', (house, year_group, start_date, end_date)).fetchone()[0]
        demerits = connection.execute('SELECT COUNT(*) FROM Demerits WHERE House = ? AND Grade = ? AND date >= ? AND date <= ?', (house, year_group, start_date, end_date)).fetchone()[0]
        house_counts[house] = merits - demerits
    connection.close()
    return house_counts

@app.route('/admin/manage-terms', methods=['GET', 'POST'])
@admin_required
def manage_terms():
    selected_year = request.args.get('year', datetime.now().year, type=int)
    if request.method == 'POST':
        for term_number in range(1, 5):
            start_date = request.form.get(f'start_date_{term_number}')
            end_date = request.form.get(f'end_date_{term_number}')
            if start_date and end_date:
                connection = sqlite3.connect('school.db')
                # Upsert term
                connection.execute('''INSERT OR REPLACE INTO terms (year, term_number, start_date, end_date) VALUES (?, ?, ?, ?)''',
                                   (selected_year, term_number, start_date, end_date))
                connection.commit()
                connection.close()
        flash('Terms updated!', 'success')
    # Get all terms for the selected year
    connection = sqlite3.connect('school.db')
    connection.row_factory = sqlite3.Row
    terms = {row['term_number']: row for row in connection.execute('SELECT * FROM terms WHERE year = ? ORDER BY term_number', (selected_year,))}
    connection.close()
    return render_template('manage_terms.html', terms=terms, selected_year=selected_year)

def get_available_terms():
    connection = sqlite3.connect('school.db')
    connection.row_factory = sqlite3.Row
    terms = list(connection.execute('SELECT * FROM terms ORDER BY year, term_number'))
    connection.close()
    return terms

def get_students_by_filter(role, user_info):
    students = {}
    filter_label = None
    if role == 'Housemaster' and user_info[0]:
        filter_value = user_info[0]
        filter_field = 'House'
        filter_label = f"House: {filter_value}"
    elif role == 'Mentor' and user_info[1]:
        filter_value = user_info[1]
        filter_field = 'Grade'
        filter_label = f"Year Group: {filter_value}"
    else:
        return {}, None
    # Query Merits
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    merits = connection.execute(f'SELECT DISTINCT StudentName, Grade, House FROM Merits WHERE {filter_field} = ? ORDER BY StudentName', (filter_value,)).fetchall()
    connection.close()
    # Query Demerits
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    demerits = connection.execute(f'SELECT DISTINCT StudentName, Grade, House FROM Demerits WHERE {filter_field} = ? ORDER BY StudentName', (filter_value,)).fetchall()
    connection.close()
    # Merge results by (name, house, grade)
    for row in merits:
        key = (row['StudentName'], row['House'], row['Grade'])
        students[key] = {'name': row['StudentName'], 'grade': row['Grade'], 'house': row['House']}
    for row in demerits:
        key = (row['StudentName'], row['House'], row['Grade'])
        if key not in students:
            students[key] = {'name': row['StudentName'], 'grade': row['Grade'], 'house': row['House']}
    return students, filter_label

def apply_time_filter_and_actions(students, start_date, end_date, time_filter):
    filtered = filter_students_by_date_grouped(students, start_date, end_date)
    for student in filtered.values():
        if time_filter == 'week':
            demerit_count = count_demerits_this_week_grouped(student['name'], student['house'], student['grade'])
            if demerit_count >= 3:
                student['action_required'] = True
                student['action_message'] = f"Action Required: 3 demerits this week — Red Detention"
            else:
                student['action_required'] = False
                student['action_message'] = ""
        else:
            student['action_required'] = False
            student['action_message'] = ""
    return filtered

@app.route('/manage-students')
@login_required
def manage_students():
    username = session.get('username')
    role = get_role()
    time_filter = request.args.get('filter', 'week')
    show_current_date = False
    available_terms = []
    connection = sqlite3.connect('users.db')
    user_info = connection.execute('SELECT house, year_group FROM users WHERE username = ?', (username,)).fetchone()
    connection.close()
    students, filter_label = get_students_by_filter(role, user_info)
    if not students:
        return "You don't have permission to manage students or your house/year group is not set."
    if time_filter == 'week':
        start_date, end_date = get_week_dates()
        filter_label2 = "This Week"
    elif time_filter == 'term':
        current_term, is_previous = get_current_term()
        if current_term:
            start_date, end_date = current_term['start_date'], current_term['end_date']
            if is_previous:
                filter_label2 = f"Previous Term: Year {current_term['year']} Term {current_term['term_number']} ({current_term['start_date']} to {current_term['end_date']})"
            else:
                filter_label2 = f"Current Term: Year {current_term['year']} Term {current_term['term_number']}"
            show_current_date = False
            available_terms = []
        else:
            start_date, end_date = get_week_dates()
            today_str = datetime.now().strftime('%Y-%m-%d')
            available_terms = get_available_terms()
            filter_label2 = f"This Week (No current term set, today: {today_str}, available terms below)"
            show_current_date = True
    elif time_filter == 'year':
        start_date, end_date = get_year_dates()
        filter_label2 = "This Year"
    else:
        start_date, end_date = get_week_dates()
        filter_label2 = "This Week"
    house_merit_count = None
    yeargroup_house_counts = None
    if role == 'Housemaster' and user_info[0]:
        house_merit_count = get_house_merit_count(user_info[0], start_date, end_date)
    elif role == 'Mentor' and user_info[1]:
        yeargroup_house_counts = get_yeargroup_house_merit_counts(user_info[1], start_date, end_date)
    students = apply_time_filter_and_actions(students, start_date, end_date, time_filter)
    return render_template('manage_students.html', students=list(students.values()), role=role, filter_type=filter_label, time_filter=time_filter, filter_label=filter_label2, house_merit_count=house_merit_count, yeargroup_house_counts=yeargroup_house_counts, show_current_date=show_current_date, available_terms=available_terms, now=datetime.now)

@app.route('/submit', methods=['POST'])
@login_required
def submit():
    name = request.form['name']
    year = request.form['year']
    house = request.form['house']
    reason = request.form['reason']
    awarded_by = session.get('username')
    date = datetime.now().strftime('%Y-%m-%d')
    award_merit(name.upper(), year, house, reason, awarded_by)
    return render_template('award_success.html', award_type='Merit', color='success', name=name, year=year, house=house, reason=reason)

@app.route('/submit-demerit', methods=['POST'])
@login_required
def submit_demerit():
    name = request.form['name']
    year = request.form['year']
    house = request.form['house']
    reason = request.form['reason']
    awarded_by = session.get('username')
    date = datetime.now().strftime('%Y-%m-%d')
    award_demerit(name.upper(), year, house, reason, awarded_by)
    return render_template('award_success.html', award_type='Demerit', color='danger', name=name, year=year, house=house, reason=reason)

def get_leaderboard_by_house(start_date, end_date):
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    houses = set([row['House'] for row in connection.execute('SELECT DISTINCT House FROM Merits')])
    houses.update([row['House'] for row in connection.execute('SELECT DISTINCT House FROM Demerits')])
    leaderboard = []
    for house in houses:
        merits = connection.execute('SELECT COUNT(*) FROM Merits WHERE House = ? AND date >= ? AND date <= ?', (house, start_date, end_date)).fetchone()[0]
        demerits = connection.execute('SELECT COUNT(*) FROM Demerits WHERE House = ? AND date >= ? AND date <= ?', (house, start_date, end_date)).fetchone()[0]
        leaderboard.append({'house': house, 'score': merits - demerits, 'merits': merits, 'demerits': demerits})
    connection.close()
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    return leaderboard

def get_leaderboard_by_yeargroup(start_date, end_date):
    connection = sqlite3.connect('awards.db')
    connection.row_factory = sqlite3.Row
    years = set([row['Grade'] for row in connection.execute('SELECT DISTINCT Grade FROM Merits')])
    years.update([row['Grade'] for row in connection.execute('SELECT DISTINCT Grade FROM Demerits')])
    leaderboard = []
    for year in years:
        merits = connection.execute('SELECT COUNT(*) FROM Merits WHERE Grade = ? AND date >= ? AND date <= ?', (year, start_date, end_date)).fetchone()[0]
        demerits = connection.execute('SELECT COUNT(*) FROM Demerits WHERE Grade = ? AND date >= ? AND date <= ?', (year, start_date, end_date)).fetchone()[0]
        leaderboard.append({'year': year, 'score': merits - demerits, 'merits': merits, 'demerits': demerits})
    connection.close()
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    return leaderboard

@app.route('/leaderboard')
def leaderboard():
    sort_by = request.args.get('sort', 'house')  # 'house' or 'year'
    time_filter = request.args.get('filter', 'week')
    show_current_date = False
    available_terms = []
    if time_filter == 'week':
        start_date, end_date = get_week_dates()
        filter_label = "This Week"
    elif time_filter == 'term':
        current_term, is_previous = get_current_term()
        if current_term:
            start_date, end_date = current_term['start_date'], current_term['end_date']
            if is_previous:
                filter_label = f"Previous Term: Year {current_term['year']} Term {current_term['term_number']} ({current_term['start_date']} to {current_term['end_date']})"
            else:
                filter_label = f"Current Term: Year {current_term['year']} Term {current_term['term_number']}"
            show_current_date = False
            available_terms = []
        else:
            start_date, end_date = get_week_dates()
            today_str = datetime.now().strftime('%Y-%m-%d')
            available_terms = get_available_terms()
            filter_label = f"This Week (No current term set, today: {today_str}, available terms below)"
            show_current_date = True
    elif time_filter == 'year':
        start_date, end_date = get_year_dates()
        filter_label = "This Year"
    else:
        start_date, end_date = get_week_dates()
        filter_label = "This Week"
    if sort_by == 'house':
        leaderboard_data = get_leaderboard_by_house(start_date, end_date)
    else:
        leaderboard_data = get_leaderboard_by_yeargroup(start_date, end_date)
    return render_template('leaderboard.html', leaderboard=leaderboard_data, sort_by=sort_by, time_filter=time_filter, filter_label=filter_label, show_current_date=show_current_date, available_terms=available_terms, now=datetime.now)


if __name__ == '__main__':
    app.run(debug=True)

