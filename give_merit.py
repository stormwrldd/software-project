import sqlite3


def award_merit(StudentName, grade, house, reason):
    StudentName = StudentName.upper()
    connection = sqlite3.connect('merits.db')
    connection.row_factory = sqlite3.Row
    new_merit = (StudentName, grade, house, reason)
    query = "INSERT INTO Merits (StudentName, Grade, House, Reason) VALUES (?, ?, ?, ?);"
    connection.execute(query, new_merit)
    connection.commit()
    connection.close()


def get_merits_for_student(StudentName):
    StudentName = StudentName.upper()
    connection = sqlite3.connect('merits.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.execute("SELECT * FROM Merits WHERE StudentName = ?;", (StudentName,))
    merits = cursor.fetchall()
    connection.close()
    return [dict(row) for row in merits]


if __name__ == "__main__":
    # Example usage
    award_merit("James Smith", 10, "Hone", "Good leadership")
    award_merit("John doe", 7, "Davidson", "working hard")
