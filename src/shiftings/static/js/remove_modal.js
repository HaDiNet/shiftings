'use strict';
(function () {
  document.addEventListener('DOMContentLoaded', initialize);

  function initialize() {
    let confirmRemoveModal = document.getElementById('confirmRemoveModal');
    confirmRemoveModal.addEventListener('show.bs.modal', function (event) {
      // Button that triggered the modal
      let button = event.relatedTarget;
      // Extract info from data-bs-* attributes

      let removeObjectPlaceholder = document.getElementById('remove_object_placeholder');
      let removeForm = document.getElementById('id_remove_form');
        
      removeForm.action = button.getAttribute('data-bs-remove-url');
      removeObjectPlaceholder.textContent = button.getAttribute('data-bs-remove-name');
    });
  }
})();