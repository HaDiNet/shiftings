'use strict';
(function () {
  function removeForm(event) {
    const element = event.currentTarget;
    if (!element.id) {
      return;
    }
    const form = document.getElementById(element.id.replace('remove', 'container'));
    if (form) {
      const id = parseInt(element.id.replace('id_form-', '').replace('_remove', ''));
      form.insertAdjacentHTML('beforeend', `<input type="checkbox" id="id_form-${id}-DELETE" name="form-${id}-DELETE" checked>`);
      form.classList.add('d-none');
    }
  }

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
      const newForm = template.content.cloneNode(true);
      newForm.id = `id_form-${totalValue}-container`;
      Array.from(newForm.children).forEach(e => {
        e.id = e.id.replaceAll('__prefix__', totalValue);
        e.innerHTML = e.innerHTML.replaceAll('__prefix__', totalValue);
      });
      insert.appendChild(newForm);
      const removeLink = document.getElementById(`id_form-${totalValue}_remove`);
      if (removeLink) {
        removeLink.addEventListener('click', removeForm);
      }
      totalElement.value = ++totalValue;
      if (totalValue >= maxValue) {
        addLink.classList.add('d-none');
      }
    });

    for (const removeLink of document.getElementsByClassName('formset-form-remove')) {
      removeLink.addEventListener('click', removeForm);
    }
  }

  document.addEventListener('DOMContentLoaded', initialize);
})();