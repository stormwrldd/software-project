# Cranbrook Merits

Cranbrook Merits is a web application designed for schools to manage and track student merits and demerits. It provides a secure, role-based system for awarding, viewing, and analyzing student achievements and behavior, supporting teachers, mentors, housemasters, and administrators.

## Features

- **Award Merits & Demerits:** Easily award merits or demerits to students, including reasons, year group, and house.
- **Role-Based Access:**
  - **Admin:** Manage users and school terms.
  - **Housemaster:** Manage and view students in their house.
  - **Mentor:** Manage and view students in their year group.
  - **Teacher:** Award merits/demerits.
- **Leaderboards:** View merit/demerit scores by house or year group, filterable by week, term, or year.
- **Account Pages:** Staff can view their own award history and relevant statistics.
- **Term Management:** Admins can set and update school term dates.
- **Secure Authentication:** Passwords are securely hashed using bcrypt.
- **Database Viewer:** Special route to view the underlying database tables (for admins).

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (awards, users, school info)
- **Frontend:** HTML, CSS (Jinja2 templates)
- **Security:** bcrypt for password hashing

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```
2. **Install dependencies:**
   Ensure you have Python 3.x installed. Then run:
   ```bash
   pip install flask bcrypt
   ```
3. **Initialize the databases:**
   Run the database setup script:
   ```bash
   python create_database.py
   ```
   This will create the necessary SQLite databases and tables, and add an initial admin user (`admin` / `Cranbrook`).
4. **Run the application:**
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5000/`.

## Usage

- **Login:** Use the admin credentials or create new users via the admin panel.
- **Award Merits/Demerits:** Use the navigation to award merits or demerits to students.
- **Manage Students:** Housemasters and mentors can view and manage students in their house/year group.
- **Leaderboards:** View merit/demerit standings by house or year group.
- **Admin Functions:** Create users and manage school terms from the account page (admin only).

## File Structure

- `app.py` — Main Flask application.
- `create_database.py` — Script to initialize databases and tables.
- `awards.db`, `users.db`, `school.db` — SQLite databases.
- `templates/` — HTML templates for the web interface.
- `static/` — Static files (CSS, PDF, etc).

## Security Notes
- Passwords must be at least 10 characters, with uppercase, lowercase, and special characters.
- All sensitive actions require login; admin actions require admin role.

## License

This project is for educational use at Cranbrook School. For other uses, please contact the author.

---

*Created for Cranbrook School Software Major Project.* 