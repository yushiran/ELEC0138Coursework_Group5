function togglePasswordVisibility() {
  var passwordInput = document.getElementById("password");
  var toggleIcon = document.getElementById("togglePassword");

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
document.addEventListener('DOMContentLoaded', function () {
  console.log("登录页面脚本已加载");

  // 获取DOM元素，添加null检查
  const sendCodeBtn = document.getElementById('send-code-btn');
  const loginBtn = document.getElementById('login-btn');
  const verificationSection = document.getElementById('verification-section');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');

  // 检查DOM元素是否存在
  if (!sendCodeBtn) console.error("找不到发送验证码按钮");
  if (!loginBtn) console.error("找不到登录按钮");
  if (!verificationSection) console.error("找不到验证码区域");
  if (!usernameInput) console.error("找不到用户名输入框");
  if (!passwordInput) console.error("找不到密码输入框");

  // 只有当所有必要元素都存在时才添加事件监听
  if (sendCodeBtn && usernameInput && passwordInput) {
    sendCodeBtn.addEventListener('click', function (e) {
      console.log("发送验证码按钮被点击");
      e.preventDefault(); // 阻止表单提交

      const username = usernameInput.value;
      const password = passwordInput.value;

      // 基本验证
      if (!username || !password) {
        showMessage('请填写用户名和密码', 'error');
        return;
      }

      // 显示加载状态
      sendCodeBtn.disabled = true;
      sendCodeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中...';

      // 发送请求获取验证码
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
        .then(response => response.json())
        .then(data => {
          sendCodeBtn.disabled = false;
          sendCodeBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 获取验证码';

          if (data.success) {
            showMessage('验证码已发送到您的邮箱', 'success');
            // 显示验证码输入区域和登录按钮
            if (verificationSection && loginBtn) {
              verificationSection.style.display = 'block';
              sendCodeBtn.style.display = 'none';
              loginBtn.style.display = 'block';
            }
          } else {
            showMessage(data.error || '发送验证码失败', 'error');
          }
        })
        .catch(error => {
          console.error('Error:', error);
          sendCodeBtn.disabled = false;
          sendCodeBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 获取验证码';
          showMessage('发生错误，请稍后重试', 'error');
        });
    });
  }

  // 显示消息的函数
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
    }, 5000); // 5秒后消失
  }
});