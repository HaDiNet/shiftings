'use strict';
(function () {
  document.addEventListener('DOMContentLoaded', initialize);

  function initialize() {
    let confirmRemoveModal = document.getElementById('confirmRemoveModal');
    confirmRemoveModal.addEventListener('show.bs.modal', function (event) {
      // Button that triggered the modal
      let button = event.relatedTarget;
      // Extract info from data-bs-* attributes

      let removeObjectPlaceholder1 = document.getElementById('remove_object_placeholder_1');
      let removeObjectPlaceholder2 = document.getElementById('remove_object_placeholder_2');
      let removeForm = document.getElementById('id_remove_form');
        
      removeForm.action = button.getAttribute('data-bs-remove-url');
      console.log(removeObjectPlaceholder1)
      console.log(removeObjectPlaceholder2)
      removeObjectPlaceholder1.textContent = button.getAttribute('data-bs-remove-name');
      removeObjectPlaceholder2.textContent = button.getAttribute('data-bs-remove-name');
    });
  }
})();