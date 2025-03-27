// Toggle password visibility
function togglePasswordVisibility() {
  const passwordInput = document.getElementById('password');
  const icon = document.getElementById('togglePassword');

  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
  } else {
    passwordInput.type = 'password';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
  }
}

function toggleConfirmPasswordVisibility() {
  const passwordInput = document.getElementById('confirm_password');
  const icon = document.getElementById('toggleConfirmPassword');

  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
  } else {
    passwordInput.type = 'password';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
  }
}

// Password validation
document.addEventListener('DOMContentLoaded', function () {
  const passwordInput = document.getElementById('password');
  const confirmPasswordInput = document.getElementById('confirm_password');
  const registerForm = document.getElementById('registerForm');
  const registerBtn = document.getElementById('registerBtn');

  // Requirements elements
  const lengthReq = document.getElementById('length-requirement');
  const letterReq = document.getElementById('letter-requirement');
  const numberReq = document.getElementById('number-requirement');
  const uppercaseReq = document.getElementById('uppercase-requirement');
  const matchReq = document.getElementById('match-requirement');

  // Function to validate password
  function validatePassword() {
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    // Check length
    if (password.length >= 8) {
      lengthReq.classList.add('valid');
      lengthReq.classList.remove('invalid');
      lengthReq.querySelector('i').classList.remove('fa-times-circle');
      lengthReq.querySelector('i').classList.add('fa-check-circle');
    } else {
      lengthReq.classList.add('invalid');
      lengthReq.classList.remove('valid');
      lengthReq.querySelector('i').classList.remove('fa-check-circle');
      lengthReq.querySelector('i').classList.add('fa-times-circle');
    }

    // Check for letters
    if (/[a-zA-Z]/.test(password)) {
      letterReq.classList.add('valid');
      letterReq.classList.remove('invalid');
      letterReq.querySelector('i').classList.remove('fa-times-circle');
      letterReq.querySelector('i').classList.add('fa-check-circle');
    } else {
      letterReq.classList.add('invalid');
      letterReq.classList.remove('valid');
      letterReq.querySelector('i').classList.remove('fa-check-circle');
      letterReq.querySelector('i').classList.add('fa-times-circle');
    }

    // Check for numbers
    if (/[0-9]/.test(password)) {
      numberReq.classList.add('valid');
      numberReq.classList.remove('invalid');
      numberReq.querySelector('i').classList.remove('fa-times-circle');
      numberReq.querySelector('i').classList.add('fa-check-circle');
    } else {
      numberReq.classList.add('invalid');
      numberReq.classList.remove('valid');
      numberReq.querySelector('i').classList.remove('fa-check-circle');
      numberReq.querySelector('i').classList.add('fa-times-circle');
    }

    // Check for uppercase
    if (/[A-Z]/.test(password)) {
      uppercaseReq.classList.add('valid');
      uppercaseReq.classList.remove('invalid');
      uppercaseReq.querySelector('i').classList.remove('fa-times-circle');
      uppercaseReq.querySelector('i').classList.add('fa-check-circle');
    } else {
      uppercaseReq.classList.add('invalid');
      uppercaseReq.classList.remove('valid');
      uppercaseReq.querySelector('i').classList.remove('fa-check-circle');
      uppercaseReq.querySelector('i').classList.add('fa-times-circle');
    }

    // Check if passwords match
    if (password && confirmPassword && password === confirmPassword) {
      matchReq.classList.add('valid');
      matchReq.classList.remove('invalid');
      matchReq.querySelector('i').classList.remove('fa-times-circle');
      matchReq.querySelector('i').classList.add('fa-check-circle');
    } else {
      matchReq.classList.add('invalid');
      matchReq.classList.remove('valid');
      matchReq.querySelector('i').classList.remove('fa-check-circle');
      matchReq.querySelector('i').classList.add('fa-times-circle');
    }

    // Check if all requirements are met
    if (password.length >= 8 &&
      /[a-zA-Z]/.test(password) &&
      /[0-9]/.test(password) &&
      /[A-Z]/.test(password) &&
      password === confirmPassword &&
      password &&
      confirmPassword) {
      registerBtn.classList.add('active');
      return true;
    } else {
      registerBtn.classList.remove('active');
      return false;
    }
  }

  // Add event listeners
  passwordInput.addEventListener('input', validatePassword);
  confirmPasswordInput.addEventListener('input', validatePassword);

  // Form submission
  registerForm.addEventListener('submit', function (event) {
    if (!validatePassword()) {
      event.preventDefault();
      alert("Please ensure all password requirements are met.");
    }
  });
});