import React, { useState, useMemo } from 'react';

// --- Helper Components ---

// Icon for the registration button
const UserPlusIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <line x1="19" x2="19" y1="8" y2="14" />
        <line x1="22" x2="16" y1="11" y2="11" />
    </svg>
);

// Custom Modal for displaying success or error messages
const Modal = ({ message, onClose }) => {
    if (!message) return null;
    const isError = message.toLowerCase().includes('error') || message.toLowerCase().includes('failed');

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl p-6 sm:p-8 max-w-sm w-full text-center">
                <div className={`mx-auto flex items-center justify-center h-12 w-12 rounded-full ${isError ? 'bg-red-100' : 'bg-green-100'}`}>
                    {isError ? (
                        <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    ) : (
                        <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                    )}
                </div>
                <h3 className="text-lg leading-6 font-medium text-gray-900 mt-4">{isError ? 'Error' : 'Success'}</h3>
                <div className="mt-2 px-7 py-3">
                    <p className="text-sm text-gray-500">{message}</p>
                </div>
                <div className="mt-4">
                    <button
                        type="button"
                        className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm"
                        onClick={onClose}
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};


// --- Main App Component ---
export default function App() {
    // --- State Management ---
    const [firstName, setFirstName] = useState('');
    const [surname, setSurname] = useState('');
    const [idNumber, setIdNumber] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [modalMessage, setModalMessage] = useState('');
    const [errors, setErrors] = useState({});

    // --- Derived State: Employee Number Generation ---
    const employeeNumber = useMemo(() => {
        if (surname.length >= 3 && idNumber.length >= 4) {
            const surnamePart = surname.substring(0, 3).toUpperCase();
            const idPart = idNumber.slice(-4);
            return `${surnamePart}${idPart}`;
        }
        return '';
    }, [surname, idNumber]);

    // --- Form Validation ---
    const validateForm = () => {
        const newErrors = {};
        if (!firstName.trim()) newErrors.firstName = 'First name is required.';
        if (!surname.trim()) newErrors.surname = 'Surname is required.';
        if (surname.length > 0 && surname.length < 3) newErrors.surname = 'Surname must be at least 3 characters.';
        
        // Basic South African ID number validation
        if (!idNumber.trim()) {
            newErrors.idNumber = 'ID number is required.';
        } else if (!/^\d{13}$/.test(idNumber)) {
            newErrors.idNumber = 'Please enter a valid 13-digit ID number.';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };
    
    // --- Event Handlers ---
    const handleSubmit = async (event) => {
        event.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsLoading(true);
        const registrationData = {
            firstName,
            surname,
            idNumber,
            employeeNumber
        };

        // --- API Integration ---
        try {
            // Replace with your actual backend endpoint
            const response = await fetch('http://localhost:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(registrationData),
            });

            const result = await response.json();

            if (!response.ok) {
                // If the server returns an error, display it
                throw new Error(result.message || 'An unknown error occurred.');
            }
            
            setModalMessage(`Successfully registered ${firstName} ${surname}! Employee Number: ${employeeNumber}`);
            // Reset form fields after successful submission
            setFirstName('');
            setSurname('');
            setIdNumber('');
            setErrors({});

        } catch (error) {
            setModalMessage(`Registration Failed: ${error.message}. Please check the console and ensure the backend server is running.`);
            console.error('API Error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // --- Render Method ---
    return (
        <div className="bg-gray-100 min-h-screen font-sans flex items-center justify-center p-4">
            <Modal message={modalMessage} onClose={() => setModalMessage('')} />
            <div className="w-full max-w-lg">
                <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-10">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-gray-800">New Employee Registration</h1>
                        <p className="text-gray-500 mt-2">Complete the form to add a new team member.</p>
                    </div>

                    <form onSubmit={handleSubmit} noValidate>
                        <div className="space-y-6">
                            {/* First Name Input */}
                            <div>
                                <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                                <input
                                    type="text"
                                    id="firstName"
                                    value={firstName}
                                    onChange={(e) => setFirstName(e.target.value)}
                                    className={`w-full px-4 py-2.5 border rounded-lg bg-gray-50 focus:ring-2 focus:outline-none transition-all duration-300 ${errors.firstName ? 'border-red-500 ring-red-200' : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-200'}`}
                                    placeholder="e.g., Jane"
                                />
                                {errors.firstName && <p className="text-red-500 text-xs mt-1">{errors.firstName}</p>}
                            </div>

                            {/* Surname Input */}
                            <div>
                                <label htmlFor="surname" className="block text-sm font-medium text-gray-700 mb-1">Surname</label>
                                <input
                                    type="text"
                                    id="surname"
                                    value={surname}
                                    onChange={(e) => setSurname(e.target.value)}
                                    className={`w-full px-4 py-2.5 border rounded-lg bg-gray-50 focus:ring-2 focus:outline-none transition-all duration-300 ${errors.surname ? 'border-red-500 ring-red-200' : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-200'}`}
                                    placeholder="e.g., Doe"
                                />
                                {errors.surname && <p className="text-red-500 text-xs mt-1">{errors.surname}</p>}
                            </div>

                            {/* ID Number Input */}
                            <div>
                                <label htmlFor="idNumber" className="block text-sm font-medium text-gray-700 mb-1">
                                    ID Number <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="text"
                                    id="idNumber"
                                    value={idNumber}
                                    onChange={(e) => setIdNumber(e.target.value.replace(/\D/g, ''))} // Allow only digits
                                    maxLength="13"
                                    className={`w-full px-4 py-2.5 border rounded-lg bg-gray-50 focus:ring-2 focus:outline-none transition-all duration-300 ${errors.idNumber ? 'border-red-500 ring-red-200' : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-200'}`}
                                    placeholder="13-digit identification number"
                                    required
                                />
                                {errors.idNumber && <p className="text-red-500 text-xs mt-1">{errors.idNumber}</p>}
                            </div>

                            {/* Generated Employee Number Display */}
                            <div>
                                <label htmlFor="employeeNumber" className="block text-sm font-medium text-gray-700 mb-1">Generated Employee Number</label>
                                <div className="w-full px-4 py-3 bg-indigo-50 border border-indigo-200 rounded-lg text-indigo-800 font-mono text-center h-12 flex items-center justify-center">
                                    {employeeNumber || '---'}
                                </div>
                            </div>
                        </div>

                        {/* Submit Button */}
                        <div className="mt-8">
                            <button
                                type="submit"
                                disabled={isLoading || !employeeNumber}
                                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-all duration-300"
                            >
                                {isLoading ? (
                                    <>
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Registering...
                                    </>
                                ) : (
                                    <>
                                        <UserPlusIcon />
                                        Register Employee
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </div>
                 <footer className="text-center mt-6 text-sm text-gray-500">
                    <p>Powered by React & Tailwind CSS</p>
                </footer>
            </div>
        </div>
    );
}
