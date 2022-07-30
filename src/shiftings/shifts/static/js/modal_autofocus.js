(function() {
  document.addEventListener('shown.bs.modal', event => {
    event.target.querySelector('[autofocus=autofocus]')?.focus();
  })
})();