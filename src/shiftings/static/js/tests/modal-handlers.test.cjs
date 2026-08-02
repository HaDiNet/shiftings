const assert = require('node:assert/strict');
const path = require('node:path');
const test = require('node:test');

const {
  MockCustomEvent,
  createDocument,
  createElement,
  installDomGlobals,
  loadScript,
  teardownDomGlobals,
} = require('./dom-harness.cjs');

function setupRemoveModalEnvironment() {
  const root = createElement({ tagName: 'HTML', id: 'root' });
  const modal = createElement({ id: 'confirmRemoveModal' });
  const placeholder1 = createElement({ id: 'remove_object_placeholder_1' });
  const placeholder2 = createElement({ id: 'remove_object_placeholder_2' });
  const successUrl = createElement({ id: 'id_success_url', tagName: 'INPUT', value: '' });
  const form = createElement({ id: 'id_remove_form' });
  root.appendChild(modal);
  root.appendChild(placeholder1);
  root.appendChild(placeholder2);
  root.appendChild(successUrl);
  root.appendChild(form);

  const document = createDocument({ root });
  installDomGlobals(document, { CustomEvent: MockCustomEvent });
  return { document, modal, placeholder1, placeholder2, successUrl, form };
}

function setupAutofocusEnvironment() {
  const root = createElement({ tagName: 'HTML', id: 'root' });
  const modal = createElement({ id: 'modal' });
  const autofocusField = createElement({ id: 'focus-me', tagName: 'INPUT' });
  autofocusField.setAttribute('autofocus', 'autofocus');
  modal.appendChild(autofocusField);
  root.appendChild(modal);

  const document = createDocument({ root });
  installDomGlobals(document, { CustomEvent: MockCustomEvent });
  return { document, modal, autofocusField };
}

function setupSelectShiftOrgEnvironment() {
  const root = createElement({ tagName: 'HTML', id: 'root' });
  const modal = createElement({ id: 'selectShiftOrgModal' });
  const actionDate = createElement({ id: 'id_action_date', tagName: 'INPUT', value: '' });
  root.appendChild(modal);
  root.appendChild(actionDate);

  const document = createDocument({ root });
  installDomGlobals(document, { CustomEvent: MockCustomEvent });
  return { document, modal, actionDate };
}

test('remove modal fills placeholders from triggering button', () => {
  const env = setupRemoveModalEnvironment();
  loadScript(path.resolve(__dirname, '..', 'remove_modal.js'));
  env.document.dispatchEvent('DOMContentLoaded');

  const button = {
    getAttribute(attributeName) {
      return {
        'data-bs-remove-url': '/delete/1/',
        'data-bs-remove-name': 'Test item',
        'data-bs-success-url': '/success/',
      }[attributeName];
    },
  };

  env.modal.dispatchEvent(new MockCustomEvent('show.bs.modal', { relatedTarget: button }));

  assert.equal(env.form.action, '/delete/1/');
  assert.equal(env.placeholder1.textContent, 'Test item');
  assert.equal(env.placeholder2.textContent, 'Test item');
  assert.equal(env.successUrl.value, '/success/');

  teardownDomGlobals();
});

test('modal autofocus focuses first autofocus field', () => {
  const env = setupAutofocusEnvironment();
  loadScript(path.resolve(__dirname, '..', '..', '..', 'shifts', 'static', 'js', 'modal_autofocus.js'));

  env.document.dispatchEvent(new MockCustomEvent('shown.bs.modal', { target: env.modal }));

  assert.equal(env.autofocusField.focusCalled, true);

  teardownDomGlobals();
});

test('calendar shift modal copies date into action field', () => {
  const env = setupSelectShiftOrgEnvironment();
  loadScript(path.resolve(__dirname, '..', '..', '..', 'cal', 'static', 'js', 'set_cal_shift_create_date.js'));
  env.document.dispatchEvent('DOMContentLoaded');

  const button = {
    getAttribute(attributeName) {
      return {
        'data-bs-date': '2026-04-17',
      }[attributeName];
    },
  };

  env.modal.dispatchEvent(new MockCustomEvent('show.bs.modal', { relatedTarget: button }));

  assert.equal(env.actionDate.value, '2026-04-17');

  teardownDomGlobals();
});
