import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, addDoc, onSnapshot, doc, deleteDoc, query } from 'firebase/firestore';
import {
  UserPlus,
  Mail,
  Briefcase,
  Building,
  User,
  Trash2,
  CheckCircle,
  XCircle,
  Loader2,
  Fingerprint, // For ID Number
  Hash // For Employee Number
} from 'lucide-react';

// Helper function for custom modal/message box
const showMessage = (setter, message, type = 'success') => {
  setter({ message, type });
  setTimeout(() => setter(null), 3000); // Clear message after 3 seconds
};

// Function to generate a simple unique employee number
const generateEmployeeNumber = () => {
  // Using a combination of timestamp and a random string for uniqueness
  const timestampPart = Date.now().toString(36); // Base 36 to make it shorter
  const randomPart = Math.random().toString(36).substring(2, 8); // Random 6 characters
  return `EMP-${timestampPart}-${randomPart}`.toUpperCase();
};

// Main App Component
const App = () => {
  const [db, setDb] = useState(null);
  const [auth, setAuth] = useState(null);
  const [userId, setUserId] = useState(null);
  const [isAuthReady, setIsAuthReady] = useState(false);
  const [loadingFirebase, setLoadingFirebase] = useState(true);

  // Form states
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [position, setPosition] = useState('');
  const [department, setDepartment] = useState('');
  const [idNumber, setIdNumber] = useState(''); // New ID Number field

  // Data states
  const [employees, setEmployees] = useState([]);
  const [loadingEmployees, setLoadingEmployees] = useState(false);
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [message, setMessage] = useState(null); // { message: '...', type: 'success' | 'error' }

  // Initialize Firebase and Auth
  useEffect(() => {
    try {
      // Ensure Firebase config and app ID are available from the environment
      // These are global variables provided by the Canvas environment.
      const currentAppId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
      const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

      // Check if Firebase config is valid before initializing
      if (!firebaseConfig.apiKey || !firebaseConfig.projectId) {
        console.error('Firebase configuration is missing or invalid.');
        setLoadingFirebase(false);
        showMessage(setMessage, 'Firebase configuration missing. Cannot initialize application.', 'error');
        return;
      }

      const app = initializeApp(firebaseConfig);
      const firestoreDb = getFirestore(app);
      const firebaseAuth = getAuth(app);

      setDb(firestoreDb);
      setAuth(firebaseAuth);

      const unsubscribe = onAuthStateChanged(firebaseAuth, async (user) => {
        if (user) {
          setUserId(user.uid);
          setIsAuthReady(true);
        } else {
          // If no user, try to sign in anonymously or with custom token (from Canvas)
          try {
            if (initialAuthToken) {
              await signInWithCustomToken(firebaseAuth, initialAuthToken);
            } else {
              await signInAnonymously(firebaseAuth);
            }
          } catch (error) {
            console.error('Error during anonymous/custom token sign-in:', error);
            setIsAuthReady(true); // Still set true to allow app to proceed even if auth failed
            showMessage(setMessage, 'Authentication failed. Please try again.', 'error');
          }
        }
        setLoadingFirebase(false);
      });

      return () => unsubscribe();
    } catch (error) {
      console.error('Failed to initialize Firebase:', error);
      setLoadingFirebase(false);
      showMessage(setMessage, 'Failed to initialize application. Check console for details.', 'error');
    }
  }, []); // Empty dependency array means this runs once on mount

  // Fetch employees when Firebase is ready and user ID is available
  useEffect(() => {
    if (db && userId && isAuthReady) {
      setLoadingEmployees(true);
      // Determine the app ID based on the global variable from Canvas
      const currentAppId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';

      // Construct the collection path based on userId and currentAppId
      const employeesCollectionPath = `/artifacts/${currentAppId}/users/${userId}/employees`;
      const employeesCollectionRef = collection(db, employeesCollectionPath);

      // Listen for real-time updates
      const unsubscribe = onSnapshot(employeesCollectionRef, (snapshot) => {
        const employeeList = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
        // Sort employees by name for consistent display (client-side sorting)
        employeeList.sort((a, b) => a.name.localeCompare(b.name));
        setEmployees(employeeList);
        setLoadingEmployees(false);
      }, (error) => {
        console.error('Error fetching employees:', error);
        showMessage(setMessage, 'Failed to load employees. Please refresh.', 'error');
        setLoadingEmployees(false);
      });

      return () => unsubscribe();
    }
  }, [db, userId, isAuthReady]); // Depend on db, userId, and isAuthReady

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!name || !email || !position || !department || !idNumber) {
      showMessage(setMessage, 'All fields are required!', 'error');
      return;
    }

    if (!db || !userId) {
      showMessage(setMessage, 'Database not ready or user not authenticated. Please wait.', 'error');
      return;
    }

    setFormSubmitting(true);
    try {
      const currentAppId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      const employeesCollectionPath = `/artifacts/${currentAppId}/users/${userId}/employees`;
      const newEmployeeNumber = generateEmployeeNumber(); // Generate employee number

      await addDoc(collection(db, employeesCollectionPath), {
        employeeNumber: newEmployeeNumber, // Add generated employee number
        name,
        email,
        position,
        department,
        idNumber, // Add ID Number
        timestamp: new Date().toISOString() // Add a timestamp for reference
      });
      showMessage(setMessage, 'Employee registered successfully!', 'success');
      // Clear form
      setName('');
      setEmail('');
      setPosition('');
      setDepartment('');
      setIdNumber(''); // Clear ID Number field
    } catch (error) {
      console.error('Error adding document: ', error);
      showMessage(setMessage, 'Error registering employee. Please try again.', 'error');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleDeleteEmployee = async (employeeId) => {
    if (!db || !userId) {
      showMessage(setMessage, 'Database not ready or user not authenticated.', 'error');
      return;
    }

    // Custom confirmation dialog
    const confirmDelete = window.confirm("Are you sure you want to delete this employee?");
    if (!confirmDelete) return;

    try {
      const currentAppId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
      const employeesCollectionPath = `/artifacts/${currentAppId}/users/${userId}/employees`;
      await deleteDoc(doc(db, employeesCollectionPath, employeeId));
      showMessage(setMessage, 'Employee deleted successfully!', 'success');
    } catch (error) {
      console.error('Error deleting document: ', error);
      showMessage(setMessage, 'Error deleting employee. Please try again.', 'error');
    }
  };

  if (loadingFirebase) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
        <Loader2 className="animate-spin h-10 w-10 text-blue-500" />
        <span className="ml-3 text-lg text-gray-700 dark:text-gray-300">Loading application...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 p-4 font-sans antialiased dark:from-gray-800 dark:to-gray-900">
      <div className="max-w-5xl mx-auto bg-white dark:bg-gray-800 shadow-xl rounded-xl p-6 md:p-8 space-y-8 border border-gray-200 dark:border-gray-700">
        <h1 className="text-4xl font-extrabold text-center text-gray-900 dark:text-white mb-8">
          New Employee Registration
        </h1>

        {/* User ID Display */}
        {userId && (
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg text-blue-800 dark:text-blue-300 text-sm flex items-center justify-center shadow-inner">
            <User className="h-5 w-5 mr-2" />
            <p>Your User ID: <span className="font-mono break-all">{userId}</span></p>
          </div>
        )}

        {/* Global Message Box */}
        {message && (
          <div className={`p-4 rounded-lg flex items-center gap-3 ${message.type === 'success' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300' : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'} shadow-md`}>
            {message.type === 'success' ? <CheckCircle className="h-5 w-5" /> : <XCircle className="h-5 w-5" />}
            <p>{message.message}</p>
          </div>
        )}

        {/* Registration Form */}
        <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-100 dark:border-gray-600">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6 flex items-center">
            <UserPlus className="h-6 w-6 mr-3 text-indigo-500 dark:text-indigo-400" /> Register New Employee
          </h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="pl-10 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-colors duration-200"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-colors duration-200"
                  placeholder="john.doe@example.com"
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="position" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Position</label>
              <div className="relative">
                <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  id="position"
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                  className="pl-10 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-colors duration-200"
                  placeholder="Software Engineer"
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="department" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Department</label>
              <div className="relative">
                <Building className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  id="department"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="pl-10 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-colors duration-200"
                  placeholder="Engineering"
                  required
                />
              </div>
            </div>
            <div className="col-span-1 md:col-span-2"> {/* Make ID Number span full width on small screens and 1 column on larger */}
              <label htmlFor="idNumber" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">ID Number (Mandatory)</label>
              <div className="relative">
                <Fingerprint className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  id="idNumber"
                  value={idNumber}
                  onChange={(e) => setIdNumber(e.target.value)}
                  className="pl-10 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white transition-colors duration-200"
                  placeholder="e.g., 9012315000089"
                  required
                />
              </div>
            </div>
            <button
              type="submit"
              className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-lg font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed col-span-1 md:col-span-2"
              disabled={formSubmitting || !db || !userId}
            >
              {formSubmitting ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={20} /> Registering...
                </>
              ) : (
                'Register Employee'
              )}
            </button>
          </form>
        </div>

        {/* Registered Employees List */}
        <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg shadow-inner border border-gray-100 dark:border-gray-600">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6 flex items-center">
            <Briefcase className="h-6 w-6 mr-3 text-teal-500 dark:text-teal-400" /> Registered Employees
          </h2>
          {loadingEmployees ? (
            <div className="flex items-center justify-center py-10 text-gray-600 dark:text-gray-300">
              <Loader2 className="animate-spin h-8 w-8 text-teal-500" />
              <span className="ml-3 text-lg">Loading employees...</span>
            </div>
          ) : employees.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-10">No employees registered yet.</p>
          ) : (
            <div className="overflow-x-auto rounded-md border border-gray-200 dark:border-gray-600">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
                <thead className="bg-gray-100 dark:bg-gray-600">
                  <tr>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider">Emp. No.</th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider">Name</th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider">Email</th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider">Position</th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider">Department</th>
                    <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider">ID Number</th>
                    <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-600 dark:text-gray-200 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-700 divide-y divide-gray-200 dark:divide-gray-600">
                  {employees.map((employee) => (
                    <tr key={employee.id} className="hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors duration-150">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{employee.employeeNumber}</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{employee.name}</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{employee.email}</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{employee.position}</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{employee.department}</td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{employee.idNumber}</td>
                      <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleDeleteEmployee(employee.id)}
                          className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 transition-colors duration-200 p-2 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                          aria-label={`Delete ${employee.name}`}
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
