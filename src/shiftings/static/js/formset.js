'use strict';
(function () {
  function initialize() {
    let total = document.getElementById('id_form-TOTAL_FORMS');
    let totalValue = parseInt(total.value);
    let max = document.getElementById('id_form-MAX_NUM_FORMS');
    let maxValue = parseInt(max.value);
    if (totalValue >= maxValue) {
      return;
    }
    let form = total.parentElement;
    let insert = document.getElementById('formset_insert');
    let template = document.getElementById('formset_template');

    let addLink = document.createElement('a');
    addLink.classList.add('btn', 'btn-secondary');
    addLink.innerHTML = '<i class="fas fa-plus"></i>';

    addLink.addEventListener('click', () => {
      let newForm = template.content.cloneNode(true);
      Array.from(newForm.children).forEach(e => e.innerHTML = e.innerHTML.replaceAll('__prefix__', totalValue));
      total.value = ++totalValue;
      insert.appendChild(newForm);
      if (totalValue >= maxValue) {
        addLink.remove();
      }
    });

    let submit = form.querySelector('[type=submit]');
    if (submit) {
      submit.parentNode.insertBefore(addLink, submit);
    } else {
      form.insertAdjacentElement('beforeend', addLink);
    }
  }

  document.addEventListener('DOMContentLoaded', initialize);
})();