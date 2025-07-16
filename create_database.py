import sqlite3
import bcrypt

def setup_database_merits():
    connection = sqlite3.connect('awards.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Merits (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentName TEXT NOT NULL,
            Grade INTEGER NOT NULL,
            House TEXT NOT NULL,
            Reason TEXT NOT NULL,
            awarded_by TEXT NOT NULL,
            date TEXT NOT NULL
        );
    ''')
    connection.commit()
    connection.close()
    print("Merits table created successfully in awards.db.")

def setup_database_demerits():
    connection = sqlite3.connect('awards.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Demerits (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentName TEXT NOT NULL,
            Grade INTEGER NOT NULL,
            House TEXT NOT NULL,
            Reason TEXT NOT NULL,
            awarded_by TEXT NOT NULL,
            date TEXT NOT NULL
        );
    ''')
    connection.commit()
    connection.close()
    print("Demerits table created successfully in awards.db.")


def setup_users_table():
    connection = sqlite3.connect('users.db')
    connection.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Teacher',
            house TEXT,
            year_group INTEGER
        );
    ''')
    connection.commit()
    connection.close()
    print("Users table created successfully.")


def setup_terms_table():
    connection = sqlite3.connect('school.db')
    connection.execute('''
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            term_number INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            UNIQUE(year, term_number)
        );
    ''')
    connection.commit()
    connection.close()
    print("Terms table created successfully.")


def setup_years_table():
    connection = sqlite3.connect('school.db')
    connection.execute('''
        CREATE TABLE IF NOT EXISTS years (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL UNIQUE
        );
    ''')
    connection.commit()
    connection.close()
    print("Years table created successfully.")


def setup_initial_terms():
    connection = sqlite3.connect('school.db')
    # Check if 2025 terms already exist
    existing = connection.execute("SELECT COUNT(*) FROM terms WHERE year = 2025").fetchone()[0]
    if existing == 0:
        # Insert 2025 Senior School terms
        connection.execute('''INSERT INTO terms (year, term_number, start_date, end_date) VALUES (?, ?, ?, ?)''',
            (2025, 1, "2025-01-30", "2025-04-11"))
        connection.execute('''INSERT INTO terms (year, term_number, start_date, end_date) VALUES (?, ?, ?, ?)''',
            (2025, 2, "2025-04-29", "2025-06-27"))
        connection.execute('''INSERT INTO terms (year, term_number, start_date, end_date) VALUES (?, ?, ?, ?)''',
            (2025, 3, "2025-07-22", "2025-09-19"))
        connection.execute('''INSERT INTO terms (year, term_number, start_date, end_date) VALUES (?, ?, ?, ?)''',
            (2025, 4, "2025-10-14", "2025-12-11"))
        connection.commit()
        print("2025 Senior School terms added.")
    else:
        print("2025 Senior School terms already exist.")
    connection.close()


def create_admin_user(username, password):
    connection = sqlite3.connect('users.db')
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        connection.execute('INSERT INTO users (username, password_hash, role, house, year_group) VALUES (?, ?, ?, ?, ?)', (username, password_hash, 'admin', None, None))
        connection.commit()
        print(f"Admin user '{username}' created successfully.")
    except sqlite3.IntegrityError:
        print(f"Admin user '{username}' already exists.")
    connection.close()


if __name__ == "__main__":
    setup_database_merits()
    setup_database_demerits()
    setup_users_table()
    setup_terms_table()
    setup_years_table()
    setup_initial_terms()
    # Uncomment and run once to create the admin user, then comment again for safety
    create_admin_user('admin', 'Cranbrook')
