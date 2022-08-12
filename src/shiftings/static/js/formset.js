'use strict';
(function () {
  function initialize() {
    const template = document.getElementById('formset_template');
    const totalElement = document.getElementById('id_form-TOTAL_FORMS');
    let totalValue = parseInt(totalElement.value);
    const maxValue = parseInt(document.getElementById('id_form-MAX_NUM_FORMS').value);
    const form = document.getElementById('formset_form') || totalElement.parentElement;
    const insert = document.getElementById('formset_insert') || form;

    let addLink = document.getElementById('formset_add');
    if (!addLink) {
      addLink = document.createElement('a');
      addLink.classList.add('btn', 'btn-secondary');
      addLink.innerHTML = '<i class="fas fa-plus"></i>';
      const submit = document.getElementById('formset_submit') || form.querySelector('[type=submit]');
      if (submit) {
        submit.parentNode.insertBefore(addLink, submit);
      } else {
        form.insertAdjacentElement('beforeend', addLink);
      }
    }

    addLink.addEventListener('click', () => {
      let newForm = template.content.cloneNode(true);
      Array.from(newForm.children).forEach(e => e.innerHTML = e.innerHTML.replaceAll('__prefix__', totalValue));
      totalElement.value = ++totalValue;
      insert.appendChild(newForm);
      if (totalValue >= maxValue) {
        addLink.classList.add('hidden');
      }
    });
  }

  document.addEventListener('DOMContentLoaded', initialize);
})();