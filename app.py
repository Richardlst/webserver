import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database connection configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'ssl_ca': 'DigiCertGlobalRootG2.crt.pem'
}

# Create a database connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Route for home page (Read operation)
@app.route('/')
def index():
    conn = get_db_connection()
    message = request.args.get('message', '')
    message_type = request.args.get('message_type', '')
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', users=users, message=message, message_type=message_type)
    else:
        return render_template('index.html', users=[], message="Database connection error", message_type="error")

# Route for adding a new user (Create operation)
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, hashed_password)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('index', message="User added successfully", message_type="success"))
            except mysql.connector.Error as err:
                cursor.close()
                conn.close()
                return redirect(url_for('add', message=f"Error: {err}", message_type="error"))
        return redirect(url_for('index'))
    message = request.args.get('message', '')
    message_type = request.args.get('message_type', '')
    return render_template('add.html', message=message, message_type=message_type)

# Route for editing a user (Update operation)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = get_db_connection()
    if conn:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE users SET name = %s, email = %s WHERE id = %s",
                    (name, email, id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('index', message="User updated successfully", message_type="success"))
            except mysql.connector.Error as err:
                cursor.close()
                conn.close()
                return redirect(url_for('edit', id=id, message=f"Error: {err}", message_type="error"))
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        message = request.args.get('message', '')
        message_type = request.args.get('message_type', '')
        return render_template('edit.html', user=user, message=message, message_type=message_type)
    else:
        return redirect(url_for('index', message="Database connection error", message_type="error"))

# Route for deleting a user (Delete operation)
@app.route('/delete/<int:id>')
def delete_user(id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = %s", (id,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index', message="User deleted successfully", message_type="success"))
        except mysql.connector.Error as err:
            cursor.close()
            conn.close()
            return redirect(url_for('index', message=f"Error: {err}", message_type="error"))
    else:
        return redirect(url_for('index', message="Database connection error", message_type="error"))

# Initialize the database and create tables if they don't exist
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Database initialized successfully")
        except mysql.connector.Error as err:
            print(f"Error initializing database: {err}")
        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    init_db()  
    app.run(debug=True, host='0.0.0.0', port=5000)