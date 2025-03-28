function togglePasswordVisibility() {
  const passwordInput = document.getElementById("password");
  const toggleIcon = document.getElementById("togglePassword");
  
  if (passwordInput && toggleIcon) {
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
}

document.addEventListener('DOMContentLoaded', function () {
  console.log("Login page script loaded");

  // Get DOM elements and add null checks
  const sendCodeBtn = document.getElementById('send-code-btn');
  const loginBtn = document.getElementById('login-btn');
  const verificationSection = document.getElementById('verification-section');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');

  // Check if DOM elements exist
  if (!sendCodeBtn) console.error("Send code button not found");
  if (!loginBtn) console.error("Login button not found");
  if (!verificationSection) console.error("Verification section not found");
  if (!usernameInput) console.error("Username input field not found");
  if (!passwordInput) console.error("Password input field not found");

  // Add event listeners only if all necessary elements exist
  if (sendCodeBtn && usernameInput && passwordInput) {
    sendCodeBtn.addEventListener('click', function (e) {
      console.log("Send code button clicked");
      e.preventDefault(); // Prevent form submission

      const username = usernameInput.value;
      const password = passwordInput.value;

      // Basic validation
      if (!username || !password) {
        showMessage('Please fill in both username and password', 'error');
        return;
      }

      // Show loading state
      sendCodeBtn.disabled = true;
      sendCodeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

      // Send request to get verification code
      fetch('/send_login_code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password
        }),
      })
        .then(response => {
          // Save status code for handling special cases
          const status = response.status;
          return response.json().then(data => {
            // Return both status code and data
            return { status, data };
          });
        })
        .then(({ status, data }) => {
          sendCodeBtn.disabled = false;
          sendCodeBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Get Code';

          if (data.success) {
            showMessage('Verification code has been sent to your email', 'success');
            // Show verification input section and login button
            if (verificationSection && loginBtn) {
              verificationSection.style.display = 'block';
              sendCodeBtn.style.display = 'none';
              loginBtn.style.display = 'block';
            }
          } else {
            // Check if the error is due to account lock
            if (status === 403) {
              // Display lock information specifically
              showMessage(data.error, 'warning');
              // Optionally disable the send code button until the lock period ends
              sendCodeBtn.disabled = true;
              sendCodeBtn.classList.add('disabled');
            } else {
              showMessage(data.error || 'Failed to send verification code', 'error');
            }
          }
        })
        .catch(error => {
          console.error('Error:', error);
          sendCodeBtn.disabled = false;
          sendCodeBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Get Code';
          showMessage('An error occurred, please try again later', 'error');
        });
    });
  }

  // Function to display messages
  function showMessage(message, type) {
    let messageContainer = document.getElementById('message-container');

    if (!messageContainer) {
      messageContainer = document.createElement('div');
      messageContainer.id = 'message-container';
      const form = document.querySelector('form');
      if (form) {
        form.insertAdjacentElement('afterend', messageContainer);
      } else {
        document.body.appendChild(messageContainer);
      }
    }

    messageContainer.innerHTML = `<div class="message ${type}">${message}</div>`;
    setTimeout(() => {
      messageContainer.innerHTML = '';
    }, 5000); // Disappear after 5 seconds
  }
});