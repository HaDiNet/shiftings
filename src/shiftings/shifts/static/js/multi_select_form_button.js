(function () {
  let selectAllButton;
  let deSelectAllButton;
  let submitSelectedButton;
  let selectInfoButton;
  let multiSelectBoxes;

  function initialize() {
    selectAllButton = document.getElementById('select_all_button');
    deSelectAllButton = document.getElementById('deselect_all_button');
    submitSelectedButton = document.getElementById('multi_select_button');
    selectInfoButton = document.getElementById('multi_select_info_button');
    multiSelectBoxes = Array.from(document.getElementsByName('object_id'));
    if (selectAllButton) {
      selectAllButton.addEventListener('click', () => {
        multiSelectBoxes.forEach(selectBox => {
          selectBox.checked = true;
        });
        onChangeSetButtonVisibility();
      });
    }
    if (deSelectAllButton) {
      deSelectAllButton.addEventListener('click', () => {
        multiSelectBoxes.forEach(selectBox => {
          selectBox.checked = false;
        });
        onChangeSetButtonVisibility();
      });
    }
    if (submitSelectedButton) {
      multiSelectBoxes.forEach(selectBox => {
        selectBox.addEventListener('click', onChangeSetButtonVisibility);
      });
      onChangeSetButtonVisibility();
    }
  }

  function onChangeSetButtonVisibility() {
    let isAnyBoxSelected = false;
    multiSelectBoxes.some(selectBox => {
      if (selectBox.checked) {
        isAnyBoxSelected = true;
        return true;
      }
    });
    if (isAnyBoxSelected) {
      submitSelectedButton.classList.remove('d-none');
      deSelectAllButton.classList.remove('d-none');
      selectInfoButton.classList.add('d-none');
      selectAllButton.classList.add('d-none');
    } else {
      submitSelectedButton.classList.add('d-none');
      deSelectAllButton.classList.add('d-none');
      selectInfoButton.classList.remove('d-none');
      selectAllButton.classList.remove('d-none');
    }
  }

  document.addEventListener('DOMContentLoaded', initialize);
})();