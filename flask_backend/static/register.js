document.addEventListener('DOMContentLoaded', function () {
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirm_password');
  const lengthRequirement = document.getElementById('length-requirement');
  const letterRequirement = document.getElementById('letter-requirement');
  const numberRequirement = document.getElementById('number-requirement');
  const uppercaseRequirement = document.getElementById('uppercase-requirement');
  const matchRequirement = document.getElementById('match-requirement');
  const sendVerificationBtn = document.getElementById('send-verification-btn');
  const verificationSection = document.getElementById('verification-section');
  const registerBtn = document.getElementById('register-btn');

  // Password validation functions
  function checkPasswordRequirements() {
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    // Check length
    if (password.length >= 8) {
      lengthRequirement.querySelector('i').className = 'fas fa-check-circle';
      lengthRequirement.style.color = 'green';
    } else {
      lengthRequirement.querySelector('i').className = 'fas fa-times-circle';
      lengthRequirement.style.color = 'red';
    }

    // Check for letters
    if (/[a-zA-Z]/.test(password)) {
      letterRequirement.querySelector('i').className = 'fas fa-check-circle';
      letterRequirement.style.color = 'green';
    } else {
      letterRequirement.querySelector('i').className = 'fas fa-times-circle';
      letterRequirement.style.color = 'red';
    }

    // Check for numbers
    if (/\d/.test(password)) {
      numberRequirement.querySelector('i').className = 'fas fa-check-circle';
      numberRequirement.style.color = 'green';
    } else {
      numberRequirement.querySelector('i').className = 'fas fa-times-circle';
      numberRequirement.style.color = 'red';
    }

    // Check for uppercase
    if (/[A-Z]/.test(password)) {
      uppercaseRequirement.querySelector('i').className = 'fas fa-check-circle';
      uppercaseRequirement.style.color = 'green';
    } else {
      uppercaseRequirement.querySelector('i').className = 'fas fa-times-circle';
      uppercaseRequirement.style.color = 'red';
    }

    // Check if passwords match
    if (password === confirmPassword && password !== '') {
      matchRequirement.querySelector('i').className = 'fas fa-check-circle';
      matchRequirement.style.color = 'green';
    } else {
      matchRequirement.querySelector('i').className = 'fas fa-times-circle';
      matchRequirement.style.color = 'red';
    }
  }

  passwordInput.addEventListener('keyup', checkPasswordRequirements);
  confirmPasswordInput.addEventListener('keyup', checkPasswordRequirements);

  // Send verification code
  sendVerificationBtn.addEventListener('click', function () {
    const email = document.querySelector('input[name="email"]').value;
    const username = document.querySelector('input[name="username"]').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    // Basic form validation
    if (!email || !username || !password || !confirmPassword) {
      alert('Please fill in all fields');
      return;
    }

    // Email validation
    if (!validateEmail(email)) {
      alert('Please enter a valid email address');
      return;
    }

    // Password validation
    if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    if (password.length < 8 || !/[a-zA-Z]/.test(password) ||
      !/\d/.test(password) || !/[A-Z]/.test(password)) {
      alert('Password does not meet all requirements');
      return;
    }

    // Send the verification code request
    fetch('/send_verification', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email,
        username: username,
        password: password
      }),
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Show verification code section
          verificationSection.style.display = 'block';
          sendVerificationBtn.style.display = 'none';
          registerBtn.style.display = 'block';
        } else {
          alert(data.error || 'Failed to send verification code');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
      });
  });

  // Email validation function
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  }
});

function togglePasswordVisibility() {
  const passwordInput = document.getElementById("password");
  const toggleIcon = document.getElementById("togglePassword");
  
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    toggleIcon.classList.remove("fa-eye-slash");
    toggleIcon.classList.add("fa-eye");
  } else {
    passwordInput.type = "password";
    toggleIcon.classList.remove("fa-eye");
    toggleIcon.classList.add("fa-eye-slash");
  }
}

// Function to toggle password visibility for the confirm password field
function toggleConfirmPasswordVisibility() {
  const confirmPasswordInput = document.getElementById("confirm_password");
  const toggleIcon = document.getElementById("toggleConfirmPassword");
  
  if (confirmPasswordInput.type === "password") {
    confirmPasswordInput.type = "text";
    toggleIcon.classList.remove("fa-eye-slash");
    toggleIcon.classList.add("fa-eye");
  } else {
    confirmPasswordInput.type = "password";
    toggleIcon.classList.remove("fa-eye");
    toggleIcon.classList.add("fa-eye-slash");
  }
}