'use strict';
(function () {
  function toggleRemove(event) {
    const button = event.currentTarget;
    if (!button.id) {
      return;
    }
    const id = parseInt(button.id.replace('id_form-', '').replace('_remove', '').replace('_restore', ''));
    const form = document.getElementById(`id_form-${id}_container`);
    if (!form) {
      return;
    }
    const remove = button.id.includes('remove');
    const deleteId = `id_form-${id}-DELETE`;
    const deleteElement = document.getElementById(deleteId);
    if (remove && !deleteElement) {
      form.insertAdjacentHTML('beforeend',
          `<input type="checkbox" id="${deleteId}" name="form-${id}-DELETE" checked class="d-none">`);
    } else if (deleteElement) {
      deleteElement.checked = remove;
    }
    document.getElementById(`id_form-${id}_remove`).classList.toggle('d-none', remove);
    document.getElementById(`id_form-${id}_restore`).classList.toggle('d-none', !remove);

    for (const inner of form.getElementsByClassName('border')) {
      inner.classList.toggle('border-danger', remove);
    }
    form.classList.toggle('border-danger', remove);
    form.style.opacity = remove ? '.5' : '1';
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
      document.getElementById('empty_alert').classList.add('d-none')
      const newForm = template.content.cloneNode(true);
      newForm.id = `id_form-${totalValue}-container`;
      Array.from(newForm.children).forEach(e => {
        e.id = e.id.replaceAll('__prefix__', totalValue);
        e.innerHTML = e.innerHTML.replaceAll('__prefix__', totalValue);
      });
      insert.appendChild(newForm);
      const removeLink = document.getElementById(`id_form-${totalValue}_remove`);
      if (removeLink) {
        removeLink.addEventListener('click', toggleRemove);
      }
      const restoreLink = document.getElementById(`id_form-${totalValue}_restore`);
      if (restoreLink) {
        restoreLink.addEventListener('click', toggleRemove);
      }
      totalElement.value = ++totalValue;
      if (totalValue >= maxValue) {
        addLink.classList.add('d-none');
      }
    });

    for (const removeLink of document.getElementsByClassName('formset-form-remove')) {
      removeLink.addEventListener('click', toggleRemove);
    }
    for (const removeLink of document.getElementsByClassName('formset-form-restore')) {
      removeLink.addEventListener('click', toggleRemove);
    }
  }

  document.addEventListener('DOMContentLoaded', initialize);
})();