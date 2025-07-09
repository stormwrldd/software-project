import sqlite3

def setup_database_merits():
    connection = sqlite3.connect('merits.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Merits (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentName TEXT NOT NULL,
            Grade INTEGER NOT NULL,
            House TEXT NOT NULL,
            Reason TEXT NOT NULL
        );
    ''')

    connection.commit()
    connection.close()
    print("Database and table created successfully.")


def setup_database_demerits():
    connection = sqlite3.connect('demerits.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Demerits (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentName TEXT NOT NULL,
            Grade INTEGER NOT NULL,
            House TEXT NOT NULL,
            Reason TEXT NOT NULL
        );
    ''')

    connection.commit()
    connection.close()
    print("Database and table created successfully.")


if __name__ == "__main__":
    setup_database_merits()
