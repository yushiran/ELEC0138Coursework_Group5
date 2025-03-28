document.addEventListener('DOMContentLoaded', function () {
    // Elements for step 1
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const emailInput = document.getElementById('email');
    const sendCodeBtn = document.getElementById('send-code-btn');
    const step1Message = document.getElementById('step1-message');
    
    // Elements for step 2
    const verificationCodeInput = document.getElementById('verification-code');
    const verifyCodeBtn = document.getElementById('verify-code-btn');
    const step2Message = document.getElementById('step2-message');
    
    // Elements for step 3
    const newPasswordInput = document.getElementById('new-password');
    const confirmNewPasswordInput = document.getElementById('confirm-new-password');
    const resetPasswordBtn = document.getElementById('reset-password-btn');
    const step3Message = document.getElementById('step3-message');
    
    // Password requirement elements
    const lengthRequirement = document.getElementById('length-requirement');
    const letterRequirement = document.getElementById('letter-requirement');
    const numberRequirement = document.getElementById('number-requirement');
    const uppercaseRequirement = document.getElementById('uppercase-requirement');
    const matchRequirement = document.getElementById('match-requirement');
    
    // Store email for later steps
    let userEmail = '';
    
    // Step 1: Send verification code
    sendCodeBtn.addEventListener('click', function() {
        const email = emailInput.value;
        
        // Validate email
        if (!validateEmail(email)) {
            showMessage(step1Message, 'Please enter a valid email address', 'error');
            return;
        }
        
        // Store email for later use
        userEmail = email;
        
        // Send request to server
        fetch('/send_reset_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(step1Message, 'Verification code sent! Check your email.', 'success');
                // Move to step 2 after a short delay
                setTimeout(() => {
                    step1.classList.remove('active');
                    step2.classList.add('active');
                }, 1500);
            } else {
                showMessage(step1Message, data.error || 'Failed to send verification code', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage(step1Message, 'An error occurred. Please try again.', 'error');
        });
    });
    
    // Step 2: Verify code
    verifyCodeBtn.addEventListener('click', function() {
        const verificationCode = verificationCodeInput.value;
        
        if (!verificationCode) {
            showMessage(step2Message, 'Please enter the verification code', 'error');
            return;
        }
        
        fetch('/verify_reset_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: userEmail,
                verification_code: verificationCode
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(step2Message, 'Code verified successfully!', 'success');
                // Move to step 3 after a short delay
                setTimeout(() => {
                    step2.classList.remove('active');
                    step3.classList.add('active');
                }, 1500);
            } else {
                showMessage(step2Message, data.error || 'Invalid or expired verification code', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage(step2Message, 'An error occurred. Please try again.', 'error');
        });
    });
    
    // Step 3: Password validation functions
    function checkPasswordRequirements() {
        const password = newPasswordInput.value;
        const confirmPassword = confirmNewPasswordInput.value;

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

    newPasswordInput.addEventListener('keyup', checkPasswordRequirements);
    confirmNewPasswordInput.addEventListener('keyup', checkPasswordRequirements);
    
    // Step 3: Reset password
    resetPasswordBtn.addEventListener('click', function() {
        const newPassword = newPasswordInput.value;
        const confirmNewPassword = confirmNewPasswordInput.value;
        
        // Validate password
        if (newPassword !== confirmNewPassword) {
            showMessage(step3Message, 'Passwords do not match', 'error');
            return;
        }
        
        if (newPassword.length < 8 || 
            !/[a-zA-Z]/.test(newPassword) || 
            !/\d/.test(newPassword) || 
            !/[A-Z]/.test(newPassword)) {
            showMessage(step3Message, 'Password does not meet all requirements', 'error');
            return;
        }
        
        fetch('/reset_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: userEmail,
                password: newPassword,
                verification_code: verificationCodeInput.value
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(step3Message, 'Password has been reset successfully!', 'success');
                // Redirect to login page after a short delay
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showMessage(step3Message, data.error || 'Failed to reset password', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage(step3Message, 'An error occurred. Please try again.', 'error');
        });
    });
    
    // Helper function to show messages
    function showMessage(element, message, type) {
        element.textContent = message;
        element.className = 'message ' + type;
    }
    
    // Email validation function
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }
});

// 替换原来的两个toggle函数，使用一个统一的函数
function togglePasswordVisibility() {
    const newPasswordInput = document.getElementById("new-password");
    const confirmPasswordInput = document.getElementById("confirm-new-password");
    const toggleIcon = document.getElementById("toggle-password-visibility");
    
    // 同步切换两个密码框的可见性
    if (newPasswordInput.type === "password") {
      // 切换到明文
      newPasswordInput.type = "text";
      confirmPasswordInput.type = "text";
      toggleIcon.classList.remove("fa-eye-slash");
      toggleIcon.classList.add("fa-eye");
    } else {
      // 切换到密文
      newPasswordInput.type = "password";
      confirmPasswordInput.type = "password";
      toggleIcon.classList.remove("fa-eye");
      toggleIcon.classList.add("fa-eye-slash");
    }
  }