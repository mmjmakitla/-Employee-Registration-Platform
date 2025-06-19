from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import uuid

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firstName TEXT,
                    lastName TEXT,
                    idNumber TEXT,
                    email TEXT,
                    department TEXT,
                    employeeNumber TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    employeeNumber = 'EMP-' + str(uuid.uuid4())[:8].upper()

    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("""INSERT INTO employees 
              (firstName, lastName, idNumber, email, department, employeeNumber) 
              VALUES (?, ?, ?, ?, ?, ?)""", 
              (data['firstName'], data['lastName'], data['idNumber'], data['email'], data['department'], employeeNumber))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Employee registered successfully! Employee Number: {employeeNumber}"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)