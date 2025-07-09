import sqlite3
from flask import Flask, render_template, request

database_name = "merits.db"
app = Flask(__name__)

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


def award_merit(StudentName, grade, house, reason):
    StudentName = StudentName.upper()
    connection = sqlite3.connect('merits.db')
    connection.row_factory = sqlite3.Row
    new_merit = (StudentName, grade, house, reason)
    query = "INSERT INTO Merits (StudentName, Grade, House, Reason) VALUES (?, ?, ?, ?);"
    connection.execute(query, new_merit)
    connection.commit()
    connection.close()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/award-merit')
def award_merit_page():
    return render_template('award_merit.html', houses=houses)


@app.route('/award-demerit')
def award_demerit_page():
    return render_template('award_merit.html', houses=houses)  # Reusing the same template for now


@app.route('/manage-students')
def manage_students():
    return "Manage Students functionality coming soon!"


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    year = request.form['year']
    house = request.form['house']
    reason = request.form['reason']
    award_merit(name.upper(), year, house, reason)
    return f"Merit awarded to {name} from Year {year}, House {house}. Reason: {reason}"


if __name__ == '__main__':
    app.run(debug=True)
