document.getElementById('employeeForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const formData = {
    firstName: document.getElementById('firstName').value,
    lastName: document.getElementById('lastName').value,
    idNumber: document.getElementById('idNumber').value,
    email: document.getElementById('email').value,
    department: document.getElementById('department').value
  };

  const response = await fetch('/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
  });

  const result = await response.json();
  document.getElementById('responseMessage').textContent = result.message;
});