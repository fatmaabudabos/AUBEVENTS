const AUB_DOMAINS = ["@mail.aub.edu", "@aub.edu.lb"];

function showPage(id) {
  document.querySelectorAll('.container').forEach(c => c.style.display = 'none');
  document.getElementById(id).style.display = 'block';
}

function isAUBEmail(email) {
  email = email.trim().toLowerCase();
  return AUB_DOMAINS.some(domain => email.endsWith(domain));
}

function loginUser() {
  const email = document.getElementById('loginEmail').value;
  document.getElementById('userEmail').innerText = email;
  showPage('landing');
}

function signupUser() {
  const email = document.getElementById('signupEmail').value;
  const pw = document.getElementById('signupPassword').value;
  const pw2 = document.getElementById('signupConfirm').value;
  const errorDiv = document.getElementById('signupError');

  if (!isAUBEmail(email)) {
    errorDiv.style.display = 'block';
    errorDiv.innerText = 'Only AUB emails allowed: @mail.aub.edu or @aub.edu.lb';
    return;
  }
  if (pw.length < 8) {
    errorDiv.style.display = 'block';
    errorDiv.innerText = 'Password must be at least 8 characters.';
    return;
  }
  if (pw !== pw2) {
    errorDiv.style.display = 'block';
    errorDiv.innerText = 'Passwords do not match.';
    return;
  }

  errorDiv.style.display = 'none';
  document.getElementById('userEmail').innerText = email;
  showPage('landing');
}

function logout() {
  document.getElementById('userEmail').innerText = 'User';
  showPage('login');
}

// Reset request email validation
const resetRequestForm = document.getElementById('resetRequestForm');
const resetRequestError = document.getElementById('resetRequestError');

resetRequestForm.addEventListener('submit', function(e) {
  e.preventDefault();
  const email = document.getElementById('resetRequestEmail').value;

  if (!isAUBEmail(email)) {
    resetRequestError.style.display = 'block';
    resetRequestError.innerText = 'Only AUB emails allowed: @mail.aub.edu or @aub.edu.lb';
    return;
  }

  resetRequestError.style.display = 'none';
  showPage('resetSuccess');
});

// Reset password form
const resetForm = document.getElementById('resetPasswordForm');
const resetError = document.getElementById('resetError');

resetForm.addEventListener('submit', function(e) {
  e.preventDefault();
  const email = document.getElementById('resetEmail').value;
  const pw = document.getElementById('newPassword').value;
  const pw2 = document.getElementById('confirmPassword').value;

  if (!isAUBEmail(email)) {
    resetError.style.display = 'block';
    resetError.innerText = 'Only AUB emails allowed: @mail.aub.edu or @aub.edu.lb';
    return;
  }
  if (pw.length < 8) {
    resetError.style.display = 'block';
    resetError.innerText = 'Password must be at least 8 characters.';
    return;
  }
  if (pw !== pw2) {
    resetError.style.display = 'block';
    resetError.innerText = 'Passwords do not match.';
    return;
  }

  resetError.style.display = 'none';
  showPage('resetDone');
});
