# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS

# Initialize Flask App
app = Flask(__name__)

# --- Configuration ---
# Enable Cross-Origin Resource Sharing (CORS) to allow the React frontend
# (running on a different port) to communicate with this backend.
CORS(app, resources={r"/register": {"origins": "http://localhost:3000"}})

# In-memory "database" for demonstration purposes.
# In a real application, you would use a database like PostgreSQL, MySQL, or MongoDB.
employee_records = []

@app.route('/')
def index():
    """
    Root endpoint to confirm the server is running.
    """
    return "<h1>Employee Registration API</h1><p>The server is running. Use the /register endpoint to POST data.</p>"

@app.route('/register', methods=['POST'])
def register_employee():
    """
    API endpoint to handle new employee registration.
    Receives JSON data from the frontend.
    """
    # --- Data Extraction and Validation ---
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Error: No data provided."}), 400

        # Extract data from the JSON payload
        first_name = data.get('firstName')
        surname = data.get('surname')
        id_number = data.get('idNumber')
        employee_number = data.get('employeeNumber')

        # Basic validation to ensure required fields are present
        if not all([first_name, surname, id_number, employee_number]):
            return jsonify({"message": "Error: Missing required fields."}), 400
        
        # Check for duplicate ID numbers (as a simple uniqueness constraint)
        if any(emp['idNumber'] == id_number for emp in employee_records):
            return jsonify({"message": f"Error: An employee with ID number {id_number} is already registered."}), 409 # 409 Conflict


    except Exception as e:
        # Handle cases where the request body is not valid JSON
        return jsonify({"message": f"Error parsing JSON: {e}"}), 400

    # --- Data Processing and Storage ---
    new_employee = {
        "firstName": first_name,
        "surname": surname,
        "idNumber": id_number,
        "employeeNumber": employee_number,
    }

    # "Save" the data to our in-memory list
    employee_records.append(new_employee)

    # Print to console to simulate saving to a log or database
    print("--- New Employee Registered ---")
    print(f"  Name: {first_name} {surname}")
    print(f"  ID Number: {id_number}")
    print(f"  Employee Number: {employee_number}")
    print(f"  Total Records: {len(employee_records)}")
    print("-----------------------------")


    # --- Response ---
    # Send a success response back to the frontend
    return jsonify({
        "message": f"Employee {first_name} {surname} registered successfully!",
        "employee": new_employee
    }), 201 # 201 Created

if __name__ == '__main__':
    # Runs the app in debug mode for development.
    # In a production environment, you would use a proper WSGI server like Gunicorn.
    app.run(debug=True, port=5000)

