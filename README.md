New Employee Registration System
This project is a full-stack application designed for registering new employees. It features a reactive frontend built with React and a functional backend API built with Python and Flask.

Project by: New Employee Registration System.

Overview
The application provides a user-friendly interface for HR personnel or administrators to input new employee details. The key feature is the automatic generation of a unique Employee Number based on the employee's surname and their government-issued ID number, streamlining the onboarding process.

Features
Interactive Frontend: A clean and responsive registration form built with React and styled with Tailwind CSS.

Dynamic Employee Number Generation: The Employee Number is automatically created and displayed in real-time as the user fills in the form. It is formed by combining the first three letters of the surname and the last four digits of the ID number.

Data Validation: The form includes client-side validation to ensure that mandatory fields, like the ID number, are filled correctly.

Backend API: A simple yet robust backend built with Python and Flask to receive and process the registration data.

Seamless Integration: The frontend communicates with the backend via API calls to submit the registration data.

Setup and Installation
Prerequisites
Node.js and npm (for the frontend)

Python 3.x and pip (for the backend)

Git

Frontend (React)
Clone the repository:

git clone <your-repository-url>
cd <repository-folder>/frontend

Install dependencies:

npm install

Run the application:

npm start

The application will be running on http://localhost:3000.

Backend (Python/Flask)
Navigate to the backend directory:

cd ../backend

Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

Install dependencies:

pip install -r requirements.txt

(You will need to create a requirements.txt file containing Flask and Flask-Cors).

Run the Flask server:

flask run

The API server will be running on http://localhost:5000.

Project Structure
.
├── frontend/         # Contains the React application
│   ├── public/
│   └── src/
│       ├── App.js    # Main application component
│       └── ...
├── backend/          # Contains the Flask API
│   ├── app.py        # Main API file
│   └── ...
├── LICENSE
└── README.md
