import sqlite3
from flask import Flask, render_template

database_name = "merits.db"

app = Flask(__name__)


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

app.run(debug=True, reloader_type='stat', port=5000)
