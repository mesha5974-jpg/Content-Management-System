// Marginalia — login / register behaviour (no dependencies)

// Show / hide password
document.querySelectorAll('.pw-toggle').forEach(function (btn) {
  btn.addEventListener('click', function () {
    var input = document.getElementById(btn.getAttribute('aria-controls'));
    var showing = input.type === 'text';
    input.type = showing ? 'password' : 'text';
    btn.textContent = showing ? 'Show' : 'Hide';
    btn.setAttribute('aria-pressed', String(!showing));
  });
});

// Confirm-password must match (register page only)
var pw = document.getElementById('id_password1') || document.getElementById('password');
var confirmPw = document.getElementById('id_password2') || document.getElementById('confirm');
if (pw && confirmPw) {
  var checkMatch = function () {
    confirmPw.setCustomValidity(
      confirmPw.value && confirmPw.value !== pw.value
        ? 'Passwords do not match.'
        : ''
    );
  };
  pw.addEventListener('input', checkMatch);
  confirmPw.addEventListener('input', checkMatch);
}

// Show validation messages inline instead of browser pop-ups
document.querySelectorAll('.auth-form').forEach(function (form) {
  function errorFor(input) {
    var wrap = input.closest('.field, .check');
    return wrap ? wrap.querySelector('.field__error') : null;
  }

  form.addEventListener('invalid', function (e) {
    e.preventDefault();
    var input = e.target;
    var err = errorFor(input);
    input.setAttribute('aria-invalid', 'true');
    if (err) err.textContent = input.validationMessage;

    // Move focus to the first invalid field only
    if (!form.dataset.focused) {
      input.focus();
      form.dataset.focused = '1';
      setTimeout(function () { delete form.dataset.focused; }, 0);
    }
  }, true);

  form.addEventListener('input', function (e) {
    var input = e.target;
    if (input.validity && input.validity.valid) {
      input.removeAttribute('aria-invalid');
      var err = errorFor(input);
      if (err) err.textContent = '';
    }
  });
});
