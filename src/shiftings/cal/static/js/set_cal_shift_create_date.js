'use strict';
(function () {
  document.addEventListener('DOMContentLoaded', initialize);

  function initialize() {
    let selectShiftOrgModal = document.getElementById('selectShiftOrgModal');
    selectShiftOrgModal.addEventListener('show.bs.modal', function (event) {
      // Button that triggered the modal
      let button = event.relatedTarget;
      // Extract info from data-bs-* attributes
      document.getElementById('id_action_date').value = button.getAttribute('data-bs-date');
    });
  }
})();